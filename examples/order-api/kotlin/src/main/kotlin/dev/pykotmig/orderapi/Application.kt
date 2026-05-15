package dev.pykotmig.orderapi

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
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import org.koin.ktor.ext.get

class NotFoundException : RuntimeException()

@Serializable
data class CreateOrderBody(val title: String)

fun Application.module() {
    configureDependencies()

    val json =
        Json {
            encodeDefaults = true
            ignoreUnknownKeys = true
        }

    install(ContentNegotiation) {
        json(json)
    }

    install(StatusPages) {
        exception<NotFoundException> { call, _ ->
            call.respond(HttpStatusCode.NotFound, mapOf("detail" to "order not found"))
        }
    }

    routing {
        post("/orders") {
            val body = call.receive<CreateOrderBody>()
            val title = body.title.trim()
            if (title.isEmpty()) {
                call.respond(HttpStatusCode.UnprocessableEntity, mapOf("detail" to "invalid title"))
                return@post
            }
            val store = call.get<OrderStore>()
            val notify = call.get<NotifyClient>()
            val id = newOrderId()
            val order = Order(id = id, title = title)
            store.put(order)
            notify.notifyOrderCreated(id)
            call.respond(HttpStatusCode.Created, order)
        }
        get("/orders/{id}") {
            val id = call.parameters["id"] ?: throw NotFoundException()
            val order = call.get<OrderStore>()[id] ?: throw NotFoundException()
            call.respond(order)
        }
        get("/orders") {
            call.respond(call.get<OrderStore>().all())
        }
        delete("/orders/{id}") {
            val id = call.parameters["id"] ?: throw NotFoundException()
            val removed = call.get<OrderStore>().remove(id)
            if (!removed) throw NotFoundException()
            call.respond(HttpStatusCode.NoContent)
        }
    }
}
