package dev.pykotmig.statushub

import io.ktor.server.application.Application
import io.ktor.server.application.ApplicationCallPipeline
import io.ktor.server.application.call
import io.ktor.server.application.install
import io.ktor.server.plugins.contentnegotiation.ContentNegotiation
import io.ktor.server.plugins.statuspages.StatusPages
import io.ktor.serialization.kotlinx.json.json
import io.ktor.server.request.receive
import io.ktor.server.request.path
import io.ktor.server.response.header
import io.ktor.server.response.respond
import io.ktor.server.routing.get
import io.ktor.server.routing.post
import io.ktor.server.routing.routing
import io.ktor.http.HttpStatusCode
import io.ktor.util.AttributeKey
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory
import java.util.UUID

private val log = LoggerFactory.getLogger("status_hub")

val CorrelationIdKey = AttributeKey<String>("CorrelationId")

@Serializable
data class HealthResponse(val status: String = "ok")

@Serializable
data class VersionResponse(val name: String = "status-hub", val version: String = "0.1.0")

@Serializable
data class EchoRequest(val message: String, val count: Int)

@Serializable
data class EchoResponse(val message: String, val count: Int)

fun Application.module() {
    val json =
        Json {
            encodeDefaults = true
            ignoreUnknownKeys = true
        }

    install(ContentNegotiation) {
        json(json)
    }

    intercept(ApplicationCallPipeline.Call) {
        val existing = call.request.headers["X-Correlation-Id"]
        val cid = existing ?: UUID.randomUUID().toString()
        call.attributes.put(CorrelationIdKey, cid)
        call.response.header("X-Correlation-Id", cid)
        val start = System.nanoTime()
        try {
            proceed()
        } finally {
            val ms = (System.nanoTime() - start) / 1_000_000.0
            log.info(
                "request correlation_id={} path={} duration_ms={}",
                cid,
                call.request.path(),
                String.format("%.2f", ms),
            )
        }
    }

    install(StatusPages) {
        exception<IllegalArgumentException> { call, cause ->
            val cid = call.attributes.getOrNull(CorrelationIdKey)
            call.respond(
                HttpStatusCode.UnprocessableEntity,
                mapOf("detail" to (cause.message ?: "invalid"), "correlation_id" to cid),
            )
        }
    }

    routing {
        get("/health") { call.respond(HealthResponse()) }
        get("/version") { call.respond(VersionResponse()) }
        post("/echo") {
            val body = call.receive<EchoRequest>()
            val msg = body.message.trim()
            if (msg.isEmpty()) {
                throw IllegalArgumentException("message cannot be empty")
            }
            if (body.count < 1 || body.count > 100) {
                throw IllegalArgumentException("count out of range")
            }
            call.respond(EchoResponse(message = msg, count = body.count))
        }
    }
}
