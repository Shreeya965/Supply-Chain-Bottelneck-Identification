-- Database Schema for Supply Chain Bottleneck Identification
-- Compatible with PostgreSQL and MySQL

-- 1. Suppliers Table
CREATE TABLE Suppliers (
    supplier_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    lead_time_days INT CHECK (lead_time_days > 0)
);

-- 2. Products Table
CREATE TABLE Products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100)
);

-- 3. Warehouses Table
CREATE TABLE Warehouses (
    warehouse_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(255)
);

-- 4. Shipments Table
CREATE TABLE Shipments (
    shipment_id SERIAL PRIMARY KEY,
    product_id INT REFERENCES Products(product_id),
    supplier_id INT REFERENCES Suppliers(supplier_id),
    warehouse_id INT REFERENCES Warehouses(warehouse_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    order_date DATE NOT NULL,
    delivery_date DATE,
    CONSTRAINT chk_dates CHECK (delivery_date IS NULL OR delivery_date >= order_date)
);

-- Add indexes for performance on frequently joined columns
CREATE INDEX idx_shipments_product ON Shipments(product_id);
CREATE INDEX idx_shipments_supplier ON Shipments(supplier_id);
CREATE INDEX idx_shipments_warehouse ON Shipments(warehouse_id);
CREATE INDEX idx_shipments_dates ON Shipments(order_date, delivery_date);
