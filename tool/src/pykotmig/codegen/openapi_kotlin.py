from __future__ import annotations

from typing import Any

from pykotmig.codegen.load import CodegenError

_SKIP_SCHEMAS = frozenset({"HTTPValidationError", "ValidationError"})


def _kotlin_ident(name: str) -> str:
    if name in {"fun", "val", "var", "in", "is", "class", "package", "return", "object"}:
        return f"`{name}`"
    return name


def _escape_kotlin_string(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _schema_to_kotlin_type(
    schema: dict[str, Any],
    schemas: dict[str, Any],
    *,
    _depth: int = 0,
) -> str:
    if _depth > 12:
        raise CodegenError(
            "JSON schema $ref chain too deep.",
            hint="Simplify models or extend the emitter.",
            rule_id="GEN_OPENAPI_UNSUPPORTED",
        )
    if "$ref" in schema:
        ref = schema["$ref"]
        if not isinstance(ref, str) or not ref.startswith("#/components/schemas/"):
            raise CodegenError(
                f"Unsupported $ref form: {ref!r}",
                hint="Only #/components/schemas/Name refs are supported.",
                rule_id="GEN_OPENAPI_UNSUPPORTED",
            )
        return ref.rsplit("/", 1)[-1]
    t = schema.get("type")
    if t == "string":
        return "String"
    if t == "integer":
        return "Int"
    if t == "number":
        return "Double"
    if t == "boolean":
        return "Boolean"
    if t == "array":
        it = schema.get("items") or {}
        inner = _schema_to_kotlin_type(it, schemas, _depth=_depth + 1)
        return f"List<{inner}>"
    if t == "object":
        raise CodegenError(
            "Inline object types are not supported for properties.",
            hint="Extract a named schema in OpenAPI.",
            rule_id="GEN_OPENAPI_UNSUPPORTED",
        )
    raise CodegenError(
        f"Unsupported schema type: {t!r}",
        hint="Use string, integer, boolean, array, or $ref.",
        rule_id="GEN_OPENAPI_UNSUPPORTED",
    )


def _default_literal_for_schema(schema: dict[str, Any], schemas: dict[str, Any]) -> str | None:
    if "default" in schema:
        d = schema["default"]
        t = schema.get("type")
        if t == "string":
            return f'"{_escape_kotlin_string(str(d))}"'
        if t == "integer":
            return str(int(d))
        if t == "number":
            return str(float(d))
        if t == "boolean":
            return "true" if d else "false"
    return None


def emit_models_kotlin(openapi: dict[str, Any], package: str) -> str:
    schemas = (openapi.get("components") or {}).get("schemas") or {}
    if not isinstance(schemas, dict):
        return f"package {package}\n"

    lines: list[str] = [
        f"package {package}",
        "",
        "import kotlinx.serialization.Serializable",
        "",
    ]
    for name, body in sorted(schemas.items(), key=lambda x: x[0]):
        if name in _SKIP_SCHEMAS:
            continue
        if not isinstance(body, dict) or body.get("type") != "object":
            continue
        props = body.get("properties") or {}
        if not isinstance(props, dict) or not props:
            continue
        required = set(body.get("required") or [])
        if not isinstance(required, set):
            required = set()

        lines.append("@Serializable")
        lines.append(f"data class {name}(")
        field_lines: list[str] = []
        for pname in sorted(props.keys()):
            pschema = props[pname]
            if not isinstance(pschema, dict):
                continue
            kt = _schema_to_kotlin_type(pschema, schemas)
            ident = _kotlin_ident(pname)
            default_expr: str | None = None
            if pname not in required:
                default_expr = _default_literal_for_schema(pschema, schemas)
            elif "default" in pschema:
                default_expr = _default_literal_for_schema(pschema, schemas)

            line = f"    val {ident}: {kt}"
            if default_expr is not None:
                line += f" = {default_expr}"
            field_lines.append(line)
        if field_lines:
            lines.append(",\n".join(field_lines) + ",")
        lines.append(")")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def emit_status_hub_application(package: str, openapi: dict[str, Any]) -> str:
    _ = openapi  # reserved for future OpenAPI-driven tweaks
    return f'''package {package}

import io.ktor.http.HttpStatusCode
import io.ktor.serialization.kotlinx.json.json
import io.ktor.server.application.Application
import io.ktor.server.application.ApplicationCallPipeline
import io.ktor.server.application.call
import io.ktor.server.application.install
import io.ktor.server.plugins.contentnegotiation.ContentNegotiation
import io.ktor.server.plugins.statuspages.StatusPages
import io.ktor.server.request.receive
import io.ktor.server.request.path
import io.ktor.server.response.header
import io.ktor.server.response.respond
import io.ktor.server.routing.get
import io.ktor.server.routing.post
import io.ktor.server.routing.routing
import io.ktor.util.AttributeKey
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import java.util.UUID

private val log = LoggerFactory.getLogger("generated_status_hub")

val CorrelationIdKey = AttributeKey<String>("CorrelationId")

fun Application.module() {{
    val json =
        Json {{
            encodeDefaults = true
            ignoreUnknownKeys = true
        }}

    install(ContentNegotiation) {{
        json(json)
    }}

    intercept(ApplicationCallPipeline.Call) {{
        val existing = call.request.headers["X-Correlation-Id"]
        val cid = existing ?: UUID.randomUUID().toString()
        call.attributes.put(CorrelationIdKey, cid)
        call.response.header("X-Correlation-Id", cid)
        val start = System.nanoTime()
        try {{
            proceed()
        }} finally {{
            val ms = (System.nanoTime() - start) / 1_000_000.0
            log.info(
                "request correlation_id={{}} path={{}} duration_ms={{}}",
                cid,
                call.request.path(),
                String.format("%.2f", ms),
            )
        }}
    }}

    install(StatusPages) {{
        exception<IllegalArgumentException> {{ call, cause ->
            val cid = call.attributes.getOrNull(CorrelationIdKey)
            call.respond(
                HttpStatusCode.UnprocessableEntity,
                mapOf("detail" to (cause.message ?: "invalid"), "correlation_id" to cid),
            )
        }}
    }}

    routing {{
        get("/health") {{ call.respond(HealthResponse()) }}
        get("/version") {{ call.respond(VersionResponse()) }}
        post("/echo") {{
            val body = call.receive<EchoRequest>()
            val msg = body.message.trim()
            if (msg.isEmpty()) {{
                throw IllegalArgumentException("message cannot be empty")
            }}
            if (body.count < 1 || body.count > 100) {{
                throw IllegalArgumentException("count out of range")
            }}
            call.respond(EchoResponse(message = msg, count = body.count))
        }}
    }}
}}
'''


def emit_status_hub_main(package: str) -> str:
    return f"""package {package}

import io.ktor.server.engine.embeddedServer
import io.ktor.server.netty.Netty

fun main() {{
    val port = System.getenv("PORT")?.toIntOrNull() ?: 8080
    embeddedServer(Netty, port = port, host = "127.0.0.1") {{
        module()
    }}.start(wait = true)
}}
"""


def emit_status_hub_application_test(package: str) -> str:
    return f"""package {package}

import io.ktor.client.request.get
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.client.statement.bodyAsText
import io.ktor.http.ContentType
import io.ktor.http.HttpStatusCode
import io.ktor.http.contentType
import io.ktor.server.testing.testApplication
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlinx.serialization.json.Json

class ApplicationTest {{
    private val json = Json {{ ignoreUnknownKeys = true; encodeDefaults = true }}

    @Test
    fun health() =
        testApplication {{
            application {{ module() }}
            val response = client.get("/health")
            assertEquals(HttpStatusCode.OK, response.status)
            val body = json.decodeFromString<HealthResponse>(response.bodyAsText())
            assertEquals("ok", body.status)
        }}

    @Test
    fun echoOk() =
        testApplication {{
            application {{ module() }}
            val response =
                client.post("/echo") {{
                    contentType(ContentType.Application.Json)
                    setBody(json.encodeToString(EchoRequest.serializer(), EchoRequest(message = "hello", count = 2)))
                }}
            assertEquals(HttpStatusCode.OK, response.status)
            val out = json.decodeFromString<EchoResponse>(response.bodyAsText())
            assertEquals("hello", out.message)
            assertEquals(2, out.count)
        }}
}}
"""


def emit_settings_gradle_kts(project_name: str) -> str:
    """Gradle 8 + Kotlin DSL: pin Kotlin plugin versions in *settings* to avoid classpath conflicts."""
    return f"""pluginManagement {{
    repositories {{
        gradlePluginPortal()
        mavenCentral()
    }}
    plugins {{
        kotlin("jvm") version "2.0.21"
        kotlin("plugin.serialization") version "2.0.21"
    }}
}}

rootProject.name = "{project_name}"
"""


def emit_status_hub_build_gradle_kts(_openapi: dict[str, Any]) -> str:
    _ = _openapi
    return """plugins {
    kotlin("jvm")
    kotlin("plugin.serialization")
    application
}

group = "dev.pykotmig"
version = "0.1.0"

repositories {
    mavenCentral()
}

val ktorVersion = "3.0.3"
val kotestVersion = "5.9.1"

dependencies {
    implementation(platform("io.ktor:ktor-bom:$ktorVersion"))
    implementation("io.ktor:ktor-server-core")
    implementation("io.ktor:ktor-server-netty")
    implementation("io.ktor:ktor-server-content-negotiation")
    implementation("io.ktor:ktor-serialization-kotlinx-json")
    implementation("io.ktor:ktor-server-status-pages")
    implementation("org.slf4j:slf4j-api:2.0.16")
    implementation("ch.qos.logback:logback-classic:1.5.12")

    testImplementation("io.ktor:ktor-server-test-host")
    testImplementation("io.kotest:kotest-runner-junit5:$kotestVersion")
    testImplementation("io.kotest:kotest-assertions-core:$kotestVersion")
    testImplementation(kotlin("test"))
}

application {
    mainClass.set("__MAIN_CLASS__")
}

kotlin {
    jvmToolchain(17)
}

tasks.test {
    useJUnitPlatform()
}
"""


def emit_order_api_build_gradle_kts(_openapi: dict[str, Any]) -> str:
    _ = _openapi
    return """plugins {
    kotlin("jvm")
    kotlin("plugin.serialization")
    application
}

group = "dev.pykotmig"
version = "0.1.0"

repositories {
    mavenCentral()
}

val ktorVersion = "3.0.3"
val kotestVersion = "5.9.1"
val koinVersion = "3.5.6"

dependencies {
    implementation(platform("io.ktor:ktor-bom:$ktorVersion"))
    implementation("io.ktor:ktor-server-core")
    implementation("io.ktor:ktor-server-netty")
    implementation("io.ktor:ktor-server-content-negotiation")
    implementation("io.ktor:ktor-serialization-kotlinx-json")
    implementation("io.ktor:ktor-server-status-pages")
    implementation("io.ktor:ktor-client-core")
    implementation("io.ktor:ktor-client-cio")
    implementation("io.ktor:ktor-client-content-negotiation")
    implementation("io.insert-koin:koin-ktor:$koinVersion")
    implementation("org.slf4j:slf4j-api:2.0.16")
    implementation("ch.qos.logback:logback-classic:1.5.12")

    testImplementation("io.ktor:ktor-server-test-host")
    testImplementation("io.kotest:kotest-runner-junit5:$kotestVersion")
    testImplementation("io.kotest:kotest-assertions-core:$kotestVersion")
    testImplementation(kotlin("test"))
}

application {
    mainClass.set("__MAIN_CLASS__")
}

kotlin {
    jvmToolchain(17)
}

tasks.test {
    useJUnitPlatform()
}
"""


def emit_order_api_config(package: str) -> str:
    return f"""package {package}

data class AppConfig(val externalHttpUrl: String?) {{
    companion object {{
        fun fromEnv(): AppConfig {{
            val raw = System.getenv("EXTERNAL_HTTP_URL")?.trim().orEmpty()
            return AppConfig(raw.ifEmpty {{ null }})
        }}
    }}
}}
"""


def emit_order_api_order_store(package: str) -> str:
    return f"""package {package}

import java.util.UUID
import java.util.concurrent.ConcurrentHashMap

class OrderStore {{
    private val orders = ConcurrentHashMap<String, Order>()

    fun put(order: Order) {{
        orders[order.id] = order
    }}

    operator fun get(id: String): Order? = orders[id]

    fun all(): List<Order> = orders.values.toList()

    fun remove(id: String): Boolean = orders.remove(id) != null

    fun clear() {{
        orders.clear()
    }}
}}

fun newOrderId(): String = UUID.randomUUID().toString()
"""


def emit_order_api_notify_client(package: str) -> str:
    return f"""package {package}

import io.ktor.client.HttpClient
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.client.statement.bodyAsText
import io.ktor.http.ContentType
import io.ktor.http.contentType
import kotlinx.serialization.Serializable
import org.slf4j.LoggerFactory

class NotifyClient(
    private val http: HttpClient,
    private val config: AppConfig,
) {{
    private val log = LoggerFactory.getLogger("order_api.notify")

    suspend fun notifyOrderCreated(orderId: String) {{
        val base = config.externalHttpUrl?.trim()?.takeIf {{ it.isNotEmpty() }}
        if (base == null) {{
            log.info("notify skipped: EXTERNAL_HTTP_URL unset order_id={{}}", orderId)
            return
        }}
        val url = "${{base.trimEnd('/')}}/notify"
        try {{
            val r =
                http.post(url) {{
                    contentType(ContentType.Application.Json)
                    setBody(NotifyBody(order_id = orderId))
                }}
            log.info("notify done order_id={{}} status={{}} url={{}}", orderId, r.status, url)
        }} catch (e: Exception) {{
            log.warn("notify failed order_id={{}} error={{}}", orderId, e.message)
        }}
    }}

    @Serializable
    private data class NotifyBody(val order_id: String)
}}
"""


def emit_order_api_koin(package: str) -> str:
    return f"""package {package}

import io.ktor.client.HttpClient
import io.ktor.client.engine.cio.CIO
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.server.application.Application
import io.ktor.server.application.install
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.json.Json
import org.koin.dsl.module
import org.koin.ktor.plugin.Koin

fun appModule(config: AppConfig) =
    module {{
        single {{ config }}
        single {{ OrderStore() }}
        single {{
            HttpClient(CIO) {{
                install(ContentNegotiation) {{
                    json(
                        Json {{
                            ignoreUnknownKeys = true
                            encodeDefaults = true
                        }},
                    )
                }}
            }}
        }}
        single {{ NotifyClient(get(), get()) }}
    }}

fun Application.configureDependencies(config: AppConfig = AppConfig.fromEnv()) {{
    install(Koin) {{
        modules(appModule(config))
    }}
}}
"""


def emit_order_api_application(package: str, openapi: dict[str, Any]) -> str:
    _ = openapi
    return f"""package {package}

import io.ktor.http.HttpStatusCode
import io.ktor.serialization.kotlinx.json.json
import io.ktor.server.application.Application
import io.ktor.server.application.install
import io.ktor.server.plugins.contentnegotiation.ContentNegotiation
import io.ktor.server.plugins.statuspages.StatusPages
import io.ktor.server.request.receive
import io.ktor.server.response.respond
import io.ktor.server.routing.delete
import io.ktor.server.routing.get
import io.ktor.server.routing.post
import io.ktor.server.routing.routing
import kotlinx.serialization.json.Json
import org.koin.ktor.ext.get

class NotFoundException : RuntimeException()

fun Application.module() {{
    configureDependencies()

    val json =
        Json {{
            encodeDefaults = true
            ignoreUnknownKeys = true
        }}

    install(ContentNegotiation) {{
        json(json)
    }}

    install(StatusPages) {{
        exception<NotFoundException> {{ call, _ ->
            call.respond(HttpStatusCode.NotFound, mapOf("detail" to "order not found"))
        }}
    }}

    routing {{
        post("/orders") {{
            val body = call.receive<CreateOrderBody>()
            val title = body.title.trim()
            if (title.isEmpty()) {{
                call.respond(HttpStatusCode.UnprocessableEntity, mapOf("detail" to "invalid title"))
                return@post
            }}
            val store = call.get<OrderStore>()
            val notify = call.get<NotifyClient>()
            val id = newOrderId()
            val order = Order(id = id, title = title)
            store.put(order)
            notify.notifyOrderCreated(id)
            call.respond(HttpStatusCode.Created, order)
        }}
        get("/orders/{{order_id}}") {{
            val id = call.parameters["order_id"] ?: throw NotFoundException()
            val order = call.get<OrderStore>()[id] ?: throw NotFoundException()
            call.respond(order)
        }}
        get("/orders") {{
            call.respond(call.get<OrderStore>().all())
        }}
        delete("/orders/{{order_id}}") {{
            val id = call.parameters["order_id"] ?: throw NotFoundException()
            val removed = call.get<OrderStore>().remove(id)
            if (!removed) throw NotFoundException()
            call.respond(HttpStatusCode.NoContent)
        }}
    }}
}}
"""


def emit_order_api_main(package: str) -> str:
    return f"""package {package}

import io.ktor.server.engine.embeddedServer
import io.ktor.server.netty.Netty

fun main() {{
    val port = System.getenv("PORT")?.toIntOrNull() ?: 8081
    embeddedServer(Netty, port = port, host = "127.0.0.1") {{
        module()
    }}.start(wait = true)
}}
"""


def emit_order_api_application_test(package: str) -> str:
    tq = '"""'
    body_json = '{"title":"  Book  "}'
    return f"""package {package}

import io.ktor.client.request.delete
import io.ktor.client.request.get
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.client.statement.bodyAsText
import io.ktor.http.ContentType
import io.ktor.http.HttpStatusCode
import io.ktor.http.contentType
import io.ktor.server.testing.testApplication
import kotlinx.serialization.json.Json
import kotlin.test.Test
import kotlin.test.assertEquals

class ApplicationTest {{
    @Test
    fun createGetListDelete() =
        testApplication {{
            application {{ module() }}
            val json = Json {{ ignoreUnknownKeys = true; encodeDefaults = true }}
            val create =
                client.post("/orders") {{
                    contentType(ContentType.Application.Json)
                    setBody({tq}{body_json}{tq})
                }}
            assertEquals(HttpStatusCode.Created, create.status)
            val order = json.decodeFromString<Order>(create.bodyAsText())
            assertEquals("Book", order.title)
            val get = client.get("/orders/${{order.id}}")
            assertEquals(HttpStatusCode.OK, get.status)
            assertEquals("Book", json.decodeFromString<Order>(get.bodyAsText()).title)
            val list = client.get("/orders")
            assertEquals(HttpStatusCode.OK, list.status)
            val del = client.delete("/orders/${{order.id}}")
            assertEquals(HttpStatusCode.NoContent, del.status)
            val missing = client.get("/orders/${{order.id}}")
            assertEquals(HttpStatusCode.NotFound, missing.status)
        }}
}}
"""




def emit_generated_readme(project_name: str, profile: str) -> str:
    return f"""# {project_name} (generated)

Profile: **{profile}**. Produced by `pykotmig-cli generate` from `analysis.json`.

## Run locally

```bash
./gradlew run
```

`PORT` defaults to **8080** (status-hub) or **8081** (order-api).

## Tests

```bash
./gradlew test
```

## Container image (KT-07)

Minimal Docker build from this directory:

```dockerfile
FROM eclipse-temurin:17-jre
WORKDIR /app
COPY build/libs/*.jar /app/app.jar
ENV PORT=8080
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
```

Build the fat JAR first (add the Shadow plugin or use `installDist` and copy the lib layout). For a portfolio shortcut, run `./gradlew build` and document that production images should use **Jib** or **Cloud Native Buildpacks** for layer caching.

See [Jib](https://github.com/GoogleContainerTools/jib) for Gradle integration.
"""


def validate_openapi_for_profile(openapi: dict[str, Any], profile: str) -> None:
    title = (openapi.get("info") or {}).get("title", "")
    paths = set((openapi.get("paths") or {}).keys())
    if profile == "status-hub":
        need = {"/health", "/version", "/echo"}
        if not need.issubset(paths):
            raise CodegenError(
                f"OpenAPI paths missing for status-hub: expected {need}, got {paths}",
                hint="Analyze the status-hub FastAPI project.",
                rule_id="GEN_PROFILE_MISMATCH",
            )
        if "status" not in str(title).lower():
            raise CodegenError(
                f"OpenAPI title {title!r} does not look like status-hub.",
                hint="Pass --profile status-hub only with status-hub analysis.",
                rule_id="GEN_PROFILE_MISMATCH",
            )
    elif profile == "order-api":
        if "/orders/{order_id}" not in paths and not any(
            p.startswith("/orders/") and "{" in p for p in paths
        ):
            raise CodegenError(
                f"OpenAPI paths missing dynamic /orders/{{param}} route: {paths}",
                hint="Analyze the order-api FastAPI project.",
                rule_id="GEN_PROFILE_MISMATCH",
            )
        if "/orders" not in paths:
            raise CodegenError(
                f"OpenAPI missing /orders: {paths}",
                hint="Analyze the order-api FastAPI project.",
                rule_id="GEN_PROFILE_MISMATCH",
            )
        if "order" not in str(title).lower():
            raise CodegenError(
                f"OpenAPI title {title!r} does not look like order-api.",
                hint="Pass --profile order-api only with order-api analysis.",
                rule_id="GEN_PROFILE_MISMATCH",
            )
    else:
        raise CodegenError(
            f"Unknown profile: {profile!r}",
            hint="Use --profile status-hub or --profile order-api.",
            rule_id="GEN_PROFILE_UNKNOWN",
        )


def main_class_for_package(package: str) -> str:
    return f"{package}.MainKt"
