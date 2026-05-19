package dev.pykotmig.statushub

import io.ktor.client.request.get
import io.ktor.client.request.headers
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.client.statement.bodyAsText
import io.ktor.http.ContentType
import io.ktor.http.HttpStatusCode
import io.ktor.http.contentType
import io.ktor.server.testing.testApplication
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class ApplicationTest {
    @Test
    fun healthGoldenHttp() =
        testApplication {
            application { module() }
            val response = client.get("/health")
            assertEquals(HttpStatusCode.OK, response.status)
            assertEquals("""{"status":"ok"}""", response.bodyAsText())
        }

    @Test
    fun versionGoldenHttp() =
        testApplication {
            application { module() }
            val response = client.get("/version")
            assertEquals(HttpStatusCode.OK, response.status)
            assertEquals("""{"name":"status-hub","version":"0.1.0"}""", response.bodyAsText())
        }

    @Test
    fun echoOkGoldenHttp() =
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

    @Test
    fun echoInvalidReturns422() =
        testApplication {
            application { module() }
            val response =
                client.post("/echo") {
                    contentType(ContentType.Application.Json)
                    setBody("""{"message":"","count":0}""")
                }
            assertEquals(HttpStatusCode.UnprocessableEntity, response.status)
        }

    @Test
    fun scheduleJobReturns202AndRunsBackgroundWork() =
        testApplication {
            BackgroundJobRecorder.reset()
            application { module() }
            val response = client.post("/jobs")
            assertEquals(HttpStatusCode.Accepted, response.status)
            val body = response.bodyAsText()
            assertTrue(body.contains("\"job_id\""))
            assertTrue(body.contains("\"status\":\"accepted\""))
            val jobId =
                Regex("\"job_id\"\\s*:\\s*\"([^\"]+)\"").find(body)?.groupValues?.get(1)
                    ?: error("job_id not found")
            var ok = false
            for (i in 0 until 200) {
                Thread.sleep(5)
                if (BackgroundJobRecorder.snapshot().contains(jobId)) {
                    ok = true
                    break
                }
            }
            assertTrue(ok, "background job did not complete")
        }

    @Test
    fun securePingOkGoldenHttp() =
        testApplication {
            application { module() }
            val response = client.get("/secure/ping") { headers { append("x-api-key", "demo-key") } }
            assertEquals(HttpStatusCode.OK, response.status)
            assertEquals("""{"authenticated":"yes"}""", response.bodyAsText())
        }

    @Test
    fun securePingMissingKeyReturns401() =
        testApplication {
            application { module() }
            val response = client.get("/secure/ping")
            assertEquals(HttpStatusCode.Unauthorized, response.status)
            assertEquals("""{"detail":"invalid or missing API key"}""", response.bodyAsText())
        }

    @Test
    fun securePingWrongKeyReturns401() =
        testApplication {
            application { module() }
            val response = client.get("/secure/ping") { headers { append("x-api-key", "wrong") } }
            assertEquals(HttpStatusCode.Unauthorized, response.status)
        }
}
