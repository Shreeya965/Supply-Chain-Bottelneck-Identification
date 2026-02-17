-- Supply Chain Bottleneck Identification Analysis
-- Purpose: Identifying delays, underperforming suppliers, and warehouse bottlenecks.

-- 1. Calculate Delivery Delay for each shipment
-- Also calculates the deviation from the supplier's promised lead time.
CREATE OR REPLACE VIEW Shipment_Delays AS
SELECT 
    s.shipment_id,
    p.name AS product_name,
    sup.name AS supplier_name,
    w.name AS warehouse_name,
    s.order_date,
    s.delivery_date,
    sup.lead_time_days AS promised_lead_time,
    (s.delivery_date - s.order_date) AS actual_lead_time,
    ((s.delivery_date - s.order_date) - sup.lead_time_days) AS delay_days
FROM Shipments s
JOIN Products p ON s.product_id = p.product_id
JOIN Suppliers sup ON s.supplier_id = sup.supplier_id
JOIN Warehouses w ON s.warehouse_id = w.warehouse_id;

-- 2. Top 5 Suppliers causing the most significant delays
-- Filtered by average delay and total number of delayed shipments.
CREATE OR REPLACE VIEW Top_Delayed_Suppliers AS
SELECT 
    supplier_name,
    COUNT(*) AS total_shipments,
    COUNT(CASE WHEN delay_days > 0 THEN 1 END) AS delayed_shipment_count,
    ROUND(AVG(delay_days), 2) AS avg_delay_days,
    MAX(delay_days) AS max_delay_days
FROM Shipment_Delays
GROUP BY supplier_name
HAVING COUNT(CASE WHEN delay_days > 0 THEN 1 END) > 0
ORDER BY avg_delay_days DESC
LIMIT 5;

-- 3. Products most impacted by delays across all warehouses
CREATE OR REPLACE VIEW Products_Impacted_By_Delays AS
SELECT 
    product_name,
    COUNT(*) AS total_shipments,
    ROUND(AVG(delay_days), 2) AS avg_delay,
    SUM(CASE WHEN delay_days > 5 THEN 1 ELSE 0 END) AS severe_delay_count
FROM Shipment_Delays
GROUP BY product_name
ORDER BY avg_delay DESC;

-- 4. Warehouse-level bottleneck summary
-- Ranks warehouses by their performance (average delay).
CREATE OR REPLACE VIEW Warehouse_Bottleneck_Summary AS
SELECT 
    warehouse_name,
    COUNT(*) AS volume,
    ROUND(AVG(delay_days), 2) AS avg_delay,
    RANK() OVER (ORDER BY AVG(delay_days) DESC) AS bottleneck_rank
FROM Shipment_Delays
GROUP BY warehouse_name;

-- 5. Flag shipments delayed beyond the supplier's average lead time
-- This uses a window function to compare individual shipment delay against supplier average.
SELECT 
    shipment_id,
    supplier_name,
    product_name,
    delay_days,
    ROUND(AVG(delay_days) OVER(PARTITION BY supplier_name), 2) AS supplier_avg_delay,
    CASE 
        WHEN delay_days > AVG(delay_days) OVER(PARTITION BY supplier_name) THEN 'Above Average Delay'
        ELSE 'Normal/Below Average'
    END AS delay_status
FROM Shipment_Delays
ORDER BY supplier_name, delay_days DESC;

-- 6. Rolling Average of Delivery Delays
-- Provides insight into whether supply chain performance is improving or worsening over time.
SELECT 
    order_date,
    delay_days,
    ROUND(AVG(delay_days) OVER(ORDER BY order_date ROWS BETWEEN 5 PRECEDING AND CURRENT ROW), 2) AS rolling_avg_delay_6_shipments
FROM Shipment_Delays
LIMIT 20;

-- 7. Identify products frequently delayed (appearing in top 20% of delays)
WITH Percentile_Delays AS (
    SELECT 
        product_name,
        delay_days,
        PERCENT_RANK() OVER(ORDER BY delay_days) as delay_percentile
    FROM Shipment_Delays
)
SELECT DISTINCT product_name, delay_days
FROM Percentile_Delays
WHERE delay_percentile > 0.8
ORDER BY delay_days DESC;
