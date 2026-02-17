import random
from datetime import datetime, timedelta

def generate_data():
    suppliers = [
        ("Global Tech Parts", "San Jose, CA", 5),
        ("Precision Manufacturing", "Detroit, MI", 10),
        ("Asia Logistics Hub", "Singapore", 15),
        ("Euro Component Co", "Berlin, Germany", 12),
        ("Coastal Supplies", "Seattle, WA", 7),
        ("Northern Iron & Steel", "Chicago, IL", 20),
        ("South Sea Electronics", "Shenzhen, China", 25),
        ("Latin America Freight", "Mexico City", 18),
        ("Mountain Raw Materials", "Denver, CO", 14),
        ("Island Precision", "Tokyo, Japan", 22)
    ]

    products = [
        ("Microprocessor X1", "Electronics"),
        ("Industrial Grade Steel", "Raw Materials"),
        ("LCD Display Panel", "Electronics"),
        ("Aluminum Casing", "Components"),
        ("Lithium Battery Pack", "Components"),
        ("Hydraulic Valve", "Industrial"),
        ("Copper Wiring 500m", "Raw Materials"),
        ("Control Circuit Board", "Electronics"),
        ("High-Torque Motor", "Industrial"),
        ("Graphite Electrode", "Raw Materials")
    ]

    warehouses = [
        ("East Coast Distribution Center", "Newark, NJ"),
        ("West Coast Hub", "Long Beach, CA"),
        ("Central Logistics Base", "Memphis, TN"),
        ("European Gateway", "Rotterdam, Netherlands"),
        ("Asia-Pacific Depot", "Hong Kong")
    ]

    sql_statements = []

    # Insert Suppliers
    for i, (name, loc, lt) in enumerate(suppliers, 1):
        sql_statements.append(f"INSERT INTO Suppliers (name, location, lead_time_days) VALUES ('{name}', '{loc}', {lt});")

    # Insert Products
    for i, (name, cat) in enumerate(products, 1):
        sql_statements.append(f"INSERT INTO Products (name, category) VALUES ('{name}', '{cat}');")

    # Insert Warehouses
    for i, (name, loc) in enumerate(warehouses, 1):
        sql_statements.append(f"INSERT INTO Warehouses (name, location) VALUES ('{name}', '{loc}');")

    # Insert Shipments (150 rows)
    start_date = datetime(2023, 1, 1)
    for i in range(1, 151):
        p_id = random.randint(1, len(products))
        s_id = random.randint(1, len(suppliers))
        w_id = random.randint(1, len(warehouses))
        qty = random.randint(100, 5000)
        
        order_date = start_date + timedelta(days=random.randint(0, 365))
        
        # Simulate delivery delays
        avg_lead_time = suppliers[s_id-1][2]
        # 30% chance of a significant delay
        if random.random() < 0.3:
            actual_days = avg_lead_time + random.randint(5, 30)
        else:
            actual_days = avg_lead_time + random.randint(-2, 3)
            if actual_days < 1: actual_days = 1
            
        delivery_date = order_date + timedelta(days=actual_days)
        
        sql_statements.append(
            f"INSERT INTO Shipments (product_id, supplier_id, warehouse_id, quantity, order_date, delivery_date) "
            f"VALUES ({p_id}, {s_id}, {w_id}, {qty}, '{order_date.date()}', '{delivery_date.date()}');"
        )

    with open('../sql/02_data.sql', 'w') as f:
        f.write("\n".join(sql_statements))
    
    print("Data generation complete. File saved to ../sql/02_data.sql")

if __name__ == "__main__":
    generate_data()
