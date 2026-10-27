def read_order(connection, order_id, tenant_id):
    return connection.fetch_one(
        "SELECT * FROM orders WHERE id = ?",
        (order_id,),
    )
