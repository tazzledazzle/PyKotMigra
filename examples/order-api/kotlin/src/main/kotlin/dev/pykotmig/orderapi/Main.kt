package dev.pykotmig.orderapi

import io.ktor.server.engine.embeddedServer
import io.ktor.server.netty.Netty

fun main() {
    val port = System.getenv("PORT")?.toIntOrNull() ?: 8081
    embeddedServer(Netty, port = port, host = "127.0.0.1") {
        module(AppConfig.fromEnv())
    }.start(wait = true)
}
