import sqlite3
import random
from datetime import datetime, timedelta

def setup_database():
    conn = sqlite3.connect('supply_chain.db')
    cursor = conn.cursor()

    # Drop existing tables
    cursor.execute("DROP TABLE IF EXISTS Shipments")
    cursor.execute("DROP TABLE IF EXISTS Warehouses")
    cursor.execute("DROP TABLE IF EXISTS Products")
    cursor.execute("DROP TABLE IF EXISTS Suppliers")

    # 1. Create Schema
    cursor.execute("""
    CREATE TABLE Suppliers (
        supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT,
        lead_time_days INTEGER
    )""")

    cursor.execute("""
    CREATE TABLE Products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT
    )""")

    cursor.execute("""
    CREATE TABLE Warehouses (
        warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT
    )""")

    cursor.execute("""
    CREATE TABLE Shipments (
        shipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER REFERENCES Products(product_id),
        supplier_id INTEGER REFERENCES Suppliers(supplier_id),
        warehouse_id INTEGER REFERENCES Warehouses(warehouse_id),
        quantity INTEGER NOT NULL,
        order_date TEXT NOT NULL,
        delivery_date TEXT
    )""")

    # 2. Populate Data
    suppliers = [
        ("Global Tech Parts", "San Jose, CA", 5),
        ("Precision Manufacturing", "Detroit, MI", 10),
        ("Asia Logistics Hub", "Singapore", 15),
        ("Euro Component Co", "Berlin, Germany", 12),
        ("Coastal Supplies", "Seattle, WA", 7)
    ]
    cursor.executemany("INSERT INTO Suppliers (name, location, lead_time_days) VALUES (?, ?, ?)", suppliers)

    products = [
        ("Microprocessor X1", "Electronics"),
        ("Industrial Grade Steel", "Raw Materials"),
        ("LCD Display Panel", "Electronics"),
        ("Aluminum Casing", "Components"),
        ("Lithium Battery Pack", "Components")
    ]
    cursor.executemany("INSERT INTO Products (name, category) VALUES (?, ?)", products)

    warehouses = [
        ("East Coast Distribution Center", "Newark, NJ"),
        ("West Coast Hub", "Long Beach, CA"),
        ("Central Logistics Base", "Memphis, TN")
    ]
    cursor.executemany("INSERT INTO Warehouses (name, location) VALUES (?, ?)", warehouses)

    # Insert 50 shipments for demo
    start_date = datetime(2023, 1, 1)
    for _ in range(50):
        p_id = random.randint(1, 5)
        s_id = random.randint(1, 5)
        w_id = random.randint(1, 3)
        qty = random.randint(100, 2000)
        
        order_dt = start_date + timedelta(days=random.randint(0, 180))
        # 30% chance of delay
        lead_time = suppliers[s_id-1][2]
        actual_days = lead_time + (random.randint(5, 15) if random.random() < 0.3 else random.randint(-1, 2))
        delivery_dt = order_dt + timedelta(days=max(1, actual_days))
        
        cursor.execute(
            "INSERT INTO Shipments (product_id, supplier_id, warehouse_id, quantity, order_date, delivery_date) VALUES (?, ?, ?, ?, ?, ?)",
            (p_id, s_id, w_id, qty, order_dt.strftime('%Y-%m-%d'), delivery_dt.strftime('%Y-%m-%d'))
        )

    conn.commit()
    return conn

def run_analysis(conn):
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("SUPPLY CHAIN BOTTLENECK ANALYSIS (SQLite Demo)")
    print("="*60)

    # 1. Shipment Delays View (Internal logic using julianday for SQLite)
    # Using a CTE instead of a permanent view for the demo
    base_query = """
    WITH Shipment_Delays AS (
        SELECT 
            s.shipment_id,
            p.name AS product_name,
            sup.name AS supplier_name,
            w.name AS warehouse_name,
            s.order_date,
            s.delivery_date,
            sup.lead_time_days AS promised_lead_time,
            CAST(julianday(s.delivery_date) - julianday(s.order_date) AS INTEGER) AS actual_lead_time,
            CAST((julianday(s.delivery_date) - julianday(s.order_date)) - sup.lead_time_days AS INTEGER) AS delay_days
        FROM Shipments s
        JOIN Products p ON s.product_id = p.product_id
        JOIN Suppliers sup ON s.supplier_id = sup.supplier_id
        JOIN Warehouses w ON s.warehouse_id = w.warehouse_id
    )
    """

    # Analysis 1: Top 5 Delayed Suppliers
    print("\n[1] Top 5 Suppliers with Highest Average Delays:")
    cursor.execute(base_query + """
    SELECT 
        supplier_name,
        COUNT(*) AS total_shipments,
        COUNT(CASE WHEN delay_days > 0 THEN 1 END) AS delayed_count,
        ROUND(AVG(delay_days), 2) AS avg_delay
    FROM Shipment_Delays
    GROUP BY supplier_name
    ORDER BY avg_delay DESC
    LIMIT 5
    """)
    print(f"{'Supplier':<25} | {'Total':<6} | {'Delayed':<8} | {'Avg Delay':<9}")
    print("-" * 60)
    for row in cursor.fetchall():
        print(f"{row[0]:<25} | {row[1]:<6} | {row[2]:<8} | {row[3]:<9}")

    # Analysis 2: Warehouse Bottlenecks
    print("\n[2] Warehouse Performance Ranking:")
    cursor.execute(base_query + """
    SELECT 
        warehouse_name,
        COUNT(*) AS volume,
        ROUND(AVG(delay_days), 2) AS avg_delay,
        RANK() OVER (ORDER BY AVG(delay_days) DESC) as rank
    FROM Shipment_Delays
    GROUP BY warehouse_name
    """)
    print(f"{'Warehouse':<35} | {'Volume':<6} | {'Avg Delay':<9} | {'Rank'}")
    print("-" * 60)
    for row in cursor.fetchall():
        print(f"{row[0]:<35} | {row[1]:<6} | {row[2]:<9} | {row[3]}")

    # Analysis 3: Products Impacted
    print("\n[3] Products Most Affected by Delays:")
    cursor.execute(base_query + """
    SELECT 
        product_name,
        ROUND(AVG(delay_days), 2) AS avg_delay,
        SUM(CASE WHEN delay_days > 5 THEN 1 ELSE 0 END) AS severe_delays
    FROM Shipment_Delays
    GROUP BY product_name
    ORDER BY avg_delay DESC
    LIMIT 3
    """)
    print(f"{'Product':<25} | {'Avg Delay':<9} | {'Severe Delays'}")
    print("-" * 60)
    for row in cursor.fetchall():
        print(f"{row[0]:<25} | {row[1]:<9} | {row[2]}")

    # Analysis 4: Rolling Average (Window Function)
    print("\n[4] Recent Delivery Delay Trends (Rolling Avg of 5):")
    cursor.execute(base_query + """
    SELECT 
        order_date,
        delay_days,
        ROUND(AVG(delay_days) OVER(ORDER BY order_date ROWS BETWEEN 4 PRECEDING AND CURRENT ROW), 2)
    FROM Shipment_Delays
    ORDER BY order_date DESC
    LIMIT 10
    """)
    print(f"{'Order Date':<12} | {'Delay':<6} | {'Rolling Avg'}")
    print("-" * 35)
    for row in cursor.fetchall():
        print(f"{row[0]:<12} | {row[1]:<6} | {row[2]}")

if __name__ == "__main__":
    db_conn = setup_database()
    run_analysis(db_conn)
    db_conn.close()
    print("\nDemo complete. Database saved to 'supply_chain.db'.")
