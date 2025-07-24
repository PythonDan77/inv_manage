from db.connection import get_conn

# Check for stocked items under the low limit and create an auto generated purchase request
def sync_inventory_status():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO purchase_requests (
                part_id, requested_by, request_date, status, notes
            )
            SELECT i.id, 'system', CURDATE(), 'requested', 'Auto-generated low stock request'
            FROM inventory_items i
            LEFT JOIN purchase_requests pr 
                ON i.id = pr.part_id AND pr.status IN ('requested', 'approved', 'ordered')
            WHERE i.item_type = 'Stocked'
              AND i.quantity <= i.low_limit
              AND pr.id IS NULL
        """)
    conn.commit()

def sync_final_assembly():
    conn = get_conn()
    with conn.cursor() as cur:
        # Add to final_assembly only if amp & cabinet builds are complete and it's not already added
        cur.execute("""
            INSERT INTO final_assembly (order_id, product_id, assembly_complete)
                SELECT o.id, o.product_id, NULL
                FROM orders o
                JOIN products p ON o.product_id = p.id
                LEFT JOIN amplifier_builds ab ON o.id = ab.order_id
                LEFT JOIN cabinet_builds cb ON o.id = cb.order_id
                LEFT JOIN final_assembly fa ON o.id = fa.order_id
                WHERE fa.id IS NULL
                AND (
                        -- For amplifiers, require both amp and cab completed
                        (p.product_type = 'Amplifier' AND ab.status = 'Completed' AND cb.status = 'Completed')
                        OR
                        -- For cabinets, only require cab completed
                        (p.product_type = 'Cabinet' AND cb.status = 'Completed')
                    )
        """)
    conn.commit()