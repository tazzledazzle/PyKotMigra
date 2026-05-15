plugins {
    kotlin("jvm") version "2.0.21"
}

group = "dev.pykotmig"
version = "0.1.0"

repositories {
    mavenCentral()
}

val coroutinesVersion = "1.9.0"
val temporalVersion = "1.25.0"

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:$coroutinesVersion")
    testImplementation("io.temporal:temporal-testing:$temporalVersion")
    testImplementation("io.temporal:temporal-sdk:$temporalVersion")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:$coroutinesVersion")
    testImplementation("org.junit.jupiter:junit-jupiter-api:5.11.4")
    testImplementation(kotlin("test"))
}

kotlin {
    jvmToolchain(17)
}

tasks.test {
    useJUnitPlatform()
}
