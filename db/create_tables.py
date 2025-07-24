from db.connection import get_conn

# First run in main.py
# When first run, verify the table exists in the MYSQL db
def ensure_tables_exist():
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """CREATE TABLE IF NOT EXISTS users(
                   id INT PRIMARY KEY AUTO_INCREMENT,
                   username VARCHAR(50),
                   password_hash VARCHAR(255),
                   role ENUM('employee', 'manager', 'admin') DEFAULT 'employee',
                   full_name VARCHAR(100)
                   )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS inventory_items (
                   id INT PRIMARY KEY AUTO_INCREMENT, 
                   part_name VARCHAR(40), 
                   part_number VARCHAR(40), 
                   quantity INT, 
                   location VARCHAR(30), 
                   supplier VARCHAR(30),  
                   low_limit INT,
                   restock_qty INT,
                   item_type VARCHAR(20),
                   item_category VARCHAR(20),
                   last_receive_date VARCHAR(20),
                   last_receive_qty VARCHAR(15)
                   )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS supplier_list (
                   id INT PRIMARY KEY AUTO_INCREMENT, 
                   name VARCHAR(40), 
                   contact VARCHAR(20),
                   phone_number VARCHAR(20), 
                   email VARCHAR(30),
                   country VARCHAR(20),
                   address VARCHAR(50)   
                   )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS purchase_requests (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    part_id INT,
                    requested_by VARCHAR(50), 
                    status ENUM('requested', 'ordered', 'received partial', 'received') DEFAULT 'requested',
                    request_date VARCHAR(20),
                    notes VARCHAR(150),
                    purchased_by VARCHAR(50),
                    purchase_qty INT,
                    purchase_date VARCHAR(20),
                    outstanding_qty INT,
                    FOREIGN KEY (part_id) REFERENCES inventory_items(id)
                   )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS purchase_history (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    purchase_id INT,
                    part_id INT,
                    part_name VARCHAR(100),
                    requested_by VARCHAR(50),
                    purchased_by VARCHAR(50),
                    received_by VARCHAR(50),
                    purchase_qty INT,
                    received_qty INT,
                    request_date VARCHAR(20),
                    purchase_date VARCHAR(20),
                    receive_date VARCHAR(20),
                    notes TEXT
                )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS products (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    product_name VARCHAR(100),
                    product_code VARCHAR(50),
                    product_type VARCHAR(50)
                )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS bill_of_materials (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    product_id INT,                  
                    part_id INT,                      
                    quantity_needed INT,
                    FOREIGN KEY (product_id) REFERENCES products(id),
                    FOREIGN KEY (part_id) REFERENCES inventory_items(id)
                )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS orders (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    customer_name VARCHAR(50),
                    customer_type VARCHAR(50),
                    po_number VARCHAR(50),
                    product_id INT,
                    product_type VARCHAR(50),
                    voltage VARCHAR(20),
                    quantity INT,
                    notes VARCHAR(50),
                    status VARCHAR(50),
                    created_at VARCHAR(20),
                    created_by VARCHAR(50),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS order_customizations (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    order_id INT,
                    option_name VARCHAR(100),     -- e.g., "Tolex"
                    option_value VARCHAR(100),    -- e.g., "Red Python"
                    part_id INT,                  -- inventory_items.id
                    quantity INT DEFAULT 1,
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (part_id) REFERENCES inventory_items(id)
                )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS amplifier_builds (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    order_id INT NOT NULL,
                    product_id INT NOT NULL,
                    status VARCHAR(50),          
                    builder_name VARCHAR(100),     
                    serial_number VARCHAR(100),
                    notes TEXT,        
                    build_start VARCHAR(25),    
                    completed_at VARCHAR(25),
                    playtester VARCHAR(100),     
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS cabinet_builds (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    order_id INT NOT NULL,
                    product_id INT NOT NULL,
                    status VARCHAR(50),               
                    notes TEXT,       
                    build_start VARCHAR(25),      
                    completed_at VARCHAR(25),     
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS pedal_orders (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    order_id INT NOT NULL,
                    product_id INT NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                    )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS finished_pedals (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    product_id INT NOT NULL,
                    finished_quantity INT DEFAULT 0,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                    )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS final_assembly (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    order_id INT NOT NULL,
                    product_id INT NOT NULL,
                    assembler_name VARCHAR(100),
                    notes TEXT,
                    assembly_complete VARCHAR(25),
                    packed_at VARCHAR(25),
                    FOREIGN KEY (order_id) REFERENCES orders(id),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                    )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS shipping (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    order_id INT UNIQUE, -- one shipping record per order
                    notes TEXT,
                    shipper VARCHAR(100),
                    tracking VARCHAR(100),
                    FOREIGN KEY (order_id) REFERENCES orders(id)
                )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS shipping_history (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    order_id INT,
                    product_name VARCHAR(100),
                    customer_name VARCHAR(100),
                    po_number VARCHAR(100),
                    status VARCHAR(20), -- e.g. 'Shipped'
                    notes TEXT,
                    shipper VARCHAR(100),
                    tracking VARCHAR(100),
                    shipped_date DATETIME,
                    shipped_by VARCHAR(100),
                    FOREIGN KEY (order_id) REFERENCES orders(id)
                )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS build_history (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    order_id INT NOT NULL,
                    product_name VARCHAR(100),
                    product_type VARCHAR(50),  -- 'amplifier' or 'cabinet'
                    customer_name VARCHAR(100),
                    customer_po VARCHAR(50),
                    voltage VARCHAR(20),               -- nullable for cabinets
                    builder_name VARCHAR(100),         -- nullable for cabinets
                    serial_number VARCHAR(100),        -- nullable for cabinets
                    playtester VARCHAR(100),           -- nullable for cabinets
                    assembler_name VARCHAR(100),
                    assembly_complete VARCHAR(25),
                    customizations TEXT,               -- serialized string like "Tolex: Red Python; Grill: Wheat"
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )"""
        )