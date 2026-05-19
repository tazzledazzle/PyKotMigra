package dev.pykotmig.clibatch

import com.github.ajalt.clikt.core.parse
import kotlin.io.path.createTempFile
import kotlin.io.path.writeText
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals

class CliBatchTest {
    @Test
    fun mapLinesSkipsBlank() {
        assertEquals(listOf("HELLO"), mapLines(listOf("hello", "", "  \n"), String::uppercase))
    }

    @Test
    fun cliUpper() {
        val tmp = createTempFile(prefix = "cli-batch", suffix = ".txt")
        tmp.writeText("hello\n\nWorld\n")
        CliBatchDemo().parse(listOf("upper", "--input", tmp.toString()))
    }
}
