package dev.pykotmig.aipipeline

import dev.langchain4j.data.document.Document

/**
 * Composable pipeline mirroring the Python LangChain `Runnable` demo (normalize → retrieve → render)
 * without live LLM calls. Retrieval uses LangChain4j [Document] metadata; swap [renderAnswer] for a
 * [dev.langchain4j.model.chat.ChatLanguageModel] when wiring production RAG.
 */
fun buildDemoPipeline(): (Map<String, Any?>) -> Map<String, Any?> =
    { input ->
        renderAnswer(buildContext(normalizeQuery(input)))
    }

private fun normalizeQuery(data: Map<String, Any?>): Map<String, Any?> {
    val q = (data["query"] as? String ?: "").trim()
    return mapOf("query" to q)
}

private fun buildContext(data: Map<String, Any?>): Map<String, Any?> {
    val docs =
        listOf(
            Document.from("overview"),
            Document.from("faq"),
        )
    val ctx = docs.map { "doc:${it.text()}" }
    return data + mapOf("context" to ctx)
}

private fun renderAnswer(data: Map<String, Any?>): Map<String, Any?> {
    val q = data["query"] as String
    @Suppress("UNCHECKED_CAST")
    val ctx = data["context"] as? List<*> ?: emptyList<Any>()
    val answer = "q='$q' sources=${ctx.size}"
    return mapOf("answer" to answer)
}
