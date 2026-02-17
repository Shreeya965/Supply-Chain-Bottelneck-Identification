# Supply Chain Bottleneck Identification SQL Project

## Project Overview
This project identifies bottlenecks in a supply chain by analyzing shipment delays from suppliers to warehouses. It uses realistic simulated data and advanced SQL techniques (CTEs, Window Functions) to provide actionable insights for data analysts.

## Repository Structure
- `sql/`: Contains all SQL scripts.
  - `01_schema.sql`: Table definitions and relationships.
  - `02_data.sql`: 150+ sample records with simulated delays.
  - `03_analysis.sql`: Analytical queries and views for bottleneck identification.
- `scripts/`: Data generation tools.
  - `generate_data.py`: Python script used to create the sample dataset.

## How to Run the Project

### Quick Start (Instant Results)
If you have Python installed, you can run a self-contained demo that uses SQLite to simulate the entire project and display the analysis:
```bash
python scripts/demo_sqlite.py
```

### Standard Setup (PostgreSQL / MySQL)

### Prerequisites
- A PostgreSQL or MySQL database instance.
- Python 3.x (optional, only if you want to regenerate data).

### Execution Steps
1. **Create the Schema**:
   Run the contents of `sql/01_schema.sql` in your SQL editor or terminal.
   ```bash
   psql -d your_database -f sql/01_schema.sql
   ```
2. **Load the Data**:
   Run the contents of `sql/02_data.sql` to populate the tables.
   ```bash
   psql -d your_database -f sql/02_data.sql
   ```
3. **Run the Analysis**:
   Execute `sql/03_analysis.sql`. This will create views and return analysis results.
   ```bash
   psql -d your_database -f sql/03_analysis.sql
   ```

## Key Insights Provided
- **Top 5 Underperforming Suppliers**: Ranked by average delay days.
- **Warehouse Performance**: Identifies which hubs are facing the most significant inbound delays.
- **Product Risk**: pinpoints products most affected by supply chain disruptions.
- **Rolling Averages**: Visualizes trends in delivery performance over time.
