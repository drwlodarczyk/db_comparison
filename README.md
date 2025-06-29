# Database Comparison: PostgreSQL vs MongoDB

This project compares PostgreSQL and MongoDB for an online clothing shop scenario, focusing on:
- Query time
- Scalability
- Data model complexity
- CRUD operations complexity
- Clarity of queries

## Data Structure
- Users
- Products
- Orders
- Order Reviews

## Metrics Collected
- Average query time (ms)
- Standard deviation
- Number of used records
- Difference with/without indexing
- Subjective grading of query clarity
- Database size and memory usage

## Record Counts Tested
10k, 20k, 30k, 50k, 80k, 100k, 150k, 250k, 500k, 1mil

## Project Structure
```
db_comparison/
├── config/
├── data_generators/
├── tests/
├── metrics/
├── results/
├── requirements.txt
└── README.md
```

## Setup
1. Install Python 3.x
2. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure PostgreSQL and MongoDB are installed and running locally.

## Usage
- Use the data_generators to seed databases.
- Run tests to collect metrics.
- Results are saved in the `results/` directory as CSV files.

## Analysis
- Use the metrics/analyzer.py to analyze and visualize results. 