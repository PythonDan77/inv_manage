from db.connection import get_conn

# Check for stocked items under the low limit and create an auto generated purchase request
def sync_inventory_status():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO purchase_requests (
                part_id, order_quantity, requested_by, request_date, status, notes
            )
            SELECT i.id, 0, 'system', CURDATE(), 'requested', 'Auto-generated low stock request'
            FROM inventory_items i
            LEFT JOIN purchase_requests pr 
                ON i.id = pr.part_id AND pr.status IN ('requested', 'approved', 'ordered')
            WHERE i.item_type = 'Stocked'
              AND i.quantity <= i.low_limit
              AND pr.id IS NULL
        """)
    conn.commit()