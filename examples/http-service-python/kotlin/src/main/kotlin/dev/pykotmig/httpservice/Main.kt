package dev.pykotmig.httpservice

import io.ktor.server.engine.embeddedServer
import io.ktor.server.netty.Netty

fun main() {
    val port = System.getenv("PORT")?.toIntOrNull() ?: 8010
    embeddedServer(Netty, port = port, host = "127.0.0.1") {
        module()
    }.start(wait = true)
}
