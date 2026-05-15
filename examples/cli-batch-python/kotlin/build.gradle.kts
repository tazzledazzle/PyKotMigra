plugins {
    kotlin("jvm") version "2.0.21"
    application
}

group = "dev.pykotmig"
version = "0.1.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation("com.github.ajalt.clikt:clikt:5.0.3")
    testImplementation("org.junit.jupiter:junit-jupiter-api:5.11.4")
    testImplementation(kotlin("test"))
}

application {
    mainClass.set("dev.pykotmig.clibatch.MainKt")
}

kotlin {
    jvmToolchain(17)
}

tasks.test {
    useJUnitPlatform()
}
