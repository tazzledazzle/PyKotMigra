plugins {
    kotlin("jvm") version "2.0.21"
    application
}

group = "dev.pykotmig"
version = "0.1.0"

repositories {
    mavenCentral()
}

val kafkaVersion = "3.8.0"

dependencies {
    implementation("org.apache.kafka:kafka-clients:$kafkaVersion")
    testImplementation("org.junit.jupiter:junit-jupiter-api:5.11.4")
    testImplementation(kotlin("test"))
}

application {
    mainClass.set("dev.pykotmig.kafkaconsumer.ConsumerMainKt")
}

kotlin {
    jvmToolchain(17)
}

tasks.test {
    useJUnitPlatform()
}
