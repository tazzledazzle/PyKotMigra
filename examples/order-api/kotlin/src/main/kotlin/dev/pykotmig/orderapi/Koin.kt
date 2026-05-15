package dev.pykotmig.orderapi

import io.ktor.client.HttpClient
import io.ktor.client.engine.cio.CIO
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.server.application.Application
import io.ktor.server.application.install
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.json.Json
import org.koin.dsl.module
import org.koin.ktor.plugin.Koin

fun appModule(config: AppConfig) =
    module {
        single { config }
        single { OrderStore() }
        single {
            HttpClient(CIO) {
                install(ContentNegotiation) {
                    json(
                        Json {
                            ignoreUnknownKeys = true
                            encodeDefaults = true
                        },
                    )
                }
            }
        }
        single { NotifyClient(get(), get()) }
    }

fun Application.configureDependencies(config: AppConfig = AppConfig.fromEnv()) {
    install(Koin) {
        modules(appModule(config))
    }
}
