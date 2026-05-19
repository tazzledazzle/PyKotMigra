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
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class ApplicationTest {
    private val json = Json { ignoreUnknownKeys = true; encodeDefaults = true }

    @Test
    fun createGetListDeleteGoldenHttp() =
        testApplication {
            application { module(AppConfig(externalHttpUrl = null)) }
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
            assertEquals("""{"id":"${order.id}","title":"Book"}""", get.bodyAsText())
            val list = client.get("/orders")
            assertEquals(HttpStatusCode.OK, list.status)
            assertEquals("""[{"id":"${order.id}","title":"Book"}]""", list.bodyAsText())
            val del = client.delete("/orders/${order.id}")
            assertEquals(HttpStatusCode.NoContent, del.status)
            val missing = client.get("/orders/${order.id}")
            assertEquals(HttpStatusCode.NotFound, missing.status)
            assertEquals("""{"detail":"order not found"}""", missing.bodyAsText())
        }

    @Test
    fun titleTooLongReturns422() =
        testApplication {
            application { module(AppConfig(externalHttpUrl = null)) }
            val longTitle = "x".repeat(201)
            val response =
                client.post("/orders") {
                    contentType(ContentType.Application.Json)
                    setBody("""{"title":"$longTitle"}""")
                }
            assertEquals(HttpStatusCode.UnprocessableEntity, response.status)
            assertEquals("""{"detail":"title too long"}""", response.bodyAsText())
        }

    @Test
    fun notifyOnCreatePostsToExternalUrl() {
        val server = MockWebServer()
        server.enqueue(MockResponse().setResponseCode(204))
        server.start()
        try {
            val base = server.url("/").toString().trimEnd('/')
            testApplication {
                application { module(AppConfig(externalHttpUrl = base)) }
                val create =
                    client.post("/orders") {
                        contentType(ContentType.Application.Json)
                        setBody("""{"title":"x"}""")
                    }
                assertEquals(HttpStatusCode.Created, create.status)
            }
            val req = server.takeRequest()
            assertEquals("POST", req.method)
            assertTrue(req.path!!.endsWith("/notify"))
            assertTrue(req.body.readUtf8().contains("order_id"))
        } finally {
            server.shutdown()
        }
    }
}
