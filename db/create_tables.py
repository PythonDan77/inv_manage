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