package dev.pykotmig.clibatch

fun mapLines(
    lines: Iterable<String>,
    transform: (String) -> String,
): List<String> {
    val out = ArrayList<String>()
    for (raw in lines) {
        val line = raw.trimEnd('\n')
        if (line.isBlank()) {
            continue
        }
        out.add(transform(line))
    }
    return out
}
