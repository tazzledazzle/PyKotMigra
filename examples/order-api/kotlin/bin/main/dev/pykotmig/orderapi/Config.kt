package dev.pykotmig.orderapi

data class AppConfig(val externalHttpUrl: String?) {
    companion object {
        fun fromEnv(): AppConfig {
            val raw = System.getenv("EXTERNAL_HTTP_URL")?.trim().orEmpty()
            return AppConfig(raw.ifEmpty { null })
        }
    }
}
