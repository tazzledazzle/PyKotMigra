package dev.pykotmig.orderapi

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

class ApplicationTest {
    @Test
    fun createGetListDelete() =
        testApplication {
            application { module() }
            val json = Json { ignoreUnknownKeys = true; encodeDefaults = true }
            val create =
                client.post("/orders") {
                    contentType(ContentType.Application.Json)
                    setBody("""{"title":"  Book  "}""")
                }
            assertEquals(HttpStatusCode.Created, create.status)
            val order = json.decodeFromString<Order>(create.bodyAsText())
            assertEquals("Book", order.title)
            val get = client.get("/orders/${order.id}")
            assertEquals(HttpStatusCode.OK, get.status)
            assertEquals("Book", json.decodeFromString<Order>(get.bodyAsText()).title)
            val list = client.get("/orders")
            assertEquals(HttpStatusCode.OK, list.status)
            val del = client.delete("/orders/${order.id}")
            assertEquals(HttpStatusCode.NoContent, del.status)
            val missing = client.get("/orders/${order.id}")
            assertEquals(HttpStatusCode.NotFound, missing.status)
        }
}
