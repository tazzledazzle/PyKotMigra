package dev.pykotmig.clibatch

import com.github.ajalt.clikt.core.CliktCommand
import com.github.ajalt.clikt.core.Context
import com.github.ajalt.clikt.core.subcommands
import com.github.ajalt.clikt.parameters.options.option
import kotlin.io.path.Path
import kotlin.io.path.exists
import kotlin.io.path.isRegularFile
import kotlin.io.path.readLines

private fun readLinesOrStdin(path: java.nio.file.Path?): List<String> =
    if (path == null) {
        generateSequence { readlnOrNull() }.toList()
    } else {
        path.readLines()
    }

private fun resolveInputPath(raw: String?): java.nio.file.Path? {
    if (raw == null) {
        return null
    }
    val path = Path(raw)
    require(path.exists()) { "path does not exist: $path" }
    require(path.isRegularFile()) { "path must be a regular file: $path" }
    return path
}

class Upper : CliktCommand(name = "upper") {
    override fun help(context: Context) = "Uppercase each line"

    private val input by option("--input", "-i")

    override fun run() {
        val path = resolveInputPath(input)
        val lines = readLinesOrStdin(path)
        mapLines(lines, String::uppercase).forEach { println(it) }
    }
}

class Lower : CliktCommand(name = "lower") {
    override fun help(context: Context) = "Lowercase each line"

    private val input by option("--input", "-i")

    override fun run() {
        val path = resolveInputPath(input)
        val lines = readLinesOrStdin(path)
        mapLines(lines, String::lowercase).forEach { println(it) }
    }
}

class CliBatchDemo : CliktCommand(name = "cli-batch-demo") {
    override fun help(context: Context) = "Batch line transforms."

    init {
        subcommands(Upper(), Lower())
    }

    override fun run() = Unit
}
