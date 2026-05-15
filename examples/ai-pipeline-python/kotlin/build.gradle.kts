plugins {
    kotlin("jvm") version "2.0.21"
}

group = "dev.pykotmig"
version = "0.1.0"

repositories {
    mavenCentral()
}

val langchain4jVersion = "0.36.2"

dependencies {
    implementation("dev.langchain4j:langchain4j-core:$langchain4jVersion")
    testImplementation("org.junit.jupiter:junit-jupiter-api:5.11.4")
    testImplementation(kotlin("test"))
}

kotlin {
    jvmToolchain(17)
}

tasks.test {
    useJUnitPlatform()
}
