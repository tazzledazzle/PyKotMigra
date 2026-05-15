package dev.pykotmig.httpservice

import io.ktor.client.request.get
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.client.statement.bodyAsText
import io.ktor.http.ContentType
import io.ktor.http.HttpStatusCode
import io.ktor.http.contentType
import io.ktor.server.testing.testApplication
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class ApplicationTest {
    @Test
    fun health() =
        testApplication {
            application { module() }
            val r = client.get("/health")
            assertEquals(HttpStatusCode.OK, r.status)
            assertTrue(r.bodyAsText().contains("\"status\":\"ok\""))
        }

    @Test
    fun greet() =
        testApplication {
            application { module() }
            val r =
                client.post("/greet") {
                    contentType(ContentType.Application.Json)
                    setBody("""{"name":"Ada"}""")
                }
            assertEquals(HttpStatusCode.OK, r.status)
            assertTrue(r.bodyAsText().contains("Ada"))
        }
}
