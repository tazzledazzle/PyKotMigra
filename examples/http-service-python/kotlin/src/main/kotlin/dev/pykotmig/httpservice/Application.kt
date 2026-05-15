package dev.pykotmig.httpservice

import io.ktor.http.HttpStatusCode
import io.ktor.serialization.kotlinx.json.json
import io.ktor.server.application.Application
import io.ktor.server.application.install
import io.ktor.server.plugins.contentnegotiation.ContentNegotiation
import io.ktor.server.request.receive
import io.ktor.server.response.respond
import io.ktor.server.routing.get
import io.ktor.server.routing.post
import io.ktor.server.routing.routing
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

private const val NAME_MAX_LEN = 80

@Serializable
data class GreetIn(val name: String)

@Serializable
data class GreetOut(val message: String)

fun Application.module() {
    val json =
        Json {
            encodeDefaults = true
            ignoreUnknownKeys = true
        }

    install(ContentNegotiation) {
        json(json)
    }

    routing {
        get("/health") {
            call.respond(mapOf("status" to "ok"))
        }
        post("/greet") {
            val body = call.receive<GreetIn>()
            val name = body.name.trim()
            if (name.isEmpty() || name.length > NAME_MAX_LEN) {
                call.respond(HttpStatusCode.UnprocessableEntity, mapOf("detail" to "invalid name"))
                return@post
            }
            call.respond(GreetOut(message = "Hello, $name"))
        }
    }
}
