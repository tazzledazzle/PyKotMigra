package dev.pykotmig.statushub

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

class ApplicationTest {
    @Test
    fun health() =
        testApplication {
            application { module() }
            val response = client.get("/health")
            assertEquals(HttpStatusCode.OK, response.status)
            assertEquals("""{"status":"ok"}""", response.bodyAsText())
        }

    @Test
    fun echoOk() =
        testApplication {
            application { module() }
            val response =
                client.post("/echo") {
                    contentType(ContentType.Application.Json)
                    setBody("""{"message":"hello","count":2}""")
                }
            assertEquals(HttpStatusCode.OK, response.status)
            assertEquals("""{"message":"hello","count":2}""", response.bodyAsText())
        }
}
