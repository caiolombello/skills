def read_order(connection, order_id, tenant_id):
    return connection.fetch_one(
        "SELECT * FROM orders WHERE id = ? AND tenant_id = ?",
        (order_id, tenant_id),
    )
