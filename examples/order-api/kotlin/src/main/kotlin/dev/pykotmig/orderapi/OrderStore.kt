package dev.pykotmig.orderapi

import java.util.UUID
import java.util.concurrent.ConcurrentHashMap
import kotlinx.serialization.Serializable

@Serializable
data class Order(val id: String, val title: String)

class OrderStore {
    private val orders = ConcurrentHashMap<String, Order>()

    fun put(order: Order) {
        orders[order.id] = order
    }

    operator fun get(id: String): Order? = orders[id]

    fun all(): List<Order> = orders.values.toList()

    fun remove(id: String): Boolean = orders.remove(id) != null

    fun clear() {
        orders.clear()
    }
}

fun newOrderId(): String = UUID.randomUUID().toString()
