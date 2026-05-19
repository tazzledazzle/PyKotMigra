package dev.pykotmig.orderapi

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
) {
    private val log = LoggerFactory.getLogger("order_api.notify")

    suspend fun notifyOrderCreated(orderId: String) {
        val base = config.externalHttpUrl?.trim()?.takeIf { it.isNotEmpty() }
        if (base == null) {
            log.info("notify skipped: EXTERNAL_HTTP_URL unset order_id={}", orderId)
            return
        }
        val url = "${base.trimEnd('/')}/notify"
        try {
            val r =
                http.post(url) {
                    contentType(ContentType.Application.Json)
                    setBody(NotifyBody(orderId))
                }
            log.info("notify done order_id={} status={} url={}", orderId, r.status, url)
        } catch (e: Exception) {
            log.warn("notify failed order_id={} error={}", orderId, e.message)
        }
    }

    @Serializable
    private data class NotifyBody(val order_id: String)
}
