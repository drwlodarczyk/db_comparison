import sys
import os
import math
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import psycopg2
import time
import pandas as pd
from config.postgres_config import POSTGRES_CONFIG

def run_query(cur, query, params=None):
    start = time.time()
    cur.execute(query, params or ())
    _ = cur.fetchall() if cur.description else None
    end = time.time()
    return (end - start) * 1000  # ms

def ensure_data(cur, record_count):
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] < record_count:
        os.system(f"python3 data_generators/postgres_seeder.py {record_count}")

def main():
    record_count = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    limit_case = sys.argv[2] if len(sys.argv) > 2 else 'all'
    if limit_case == 'all':
        id_start = 1
        id_end = record_count
    elif limit_case == '10pct':
        id_start = 1
        id_end = max(1, math.ceil(record_count * 0.1))
    elif limit_case == '1pct':
        id_start = 1
        id_end = max(1, math.ceil(record_count * 0.01))
    else:
        id_start = 1
        id_end = 1
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cur = conn.cursor()
    ensure_data(cur, record_count)
    results = []
    queries = [
        ("Select all users", f"SELECT * FROM users WHERE id BETWEEN {id_start} AND {id_end}", None),
        ("Select all products in category", f"SELECT * FROM products WHERE category = %s AND id BETWEEN {id_start} AND {id_end}", ('Shirts',)),
        ("Select all orders for user", f"SELECT * FROM orders WHERE user_id = %s AND id BETWEEN {id_start} AND {id_end}", (1,)),
        ("Top 10 best-selling products", "SELECT product_id, COUNT(*) as cnt FROM order_reviews GROUP BY product_id ORDER BY cnt DESC LIMIT 10", None),
        ("Average rating per product", "SELECT product_id, AVG(rating) FROM order_reviews GROUP BY product_id LIMIT 10", None),
    ]
    for name, query, params in queries:
        times = []
        for _ in range(5):
            t = run_query(cur, query, params)
            times.append(t)
        results.append({
            'operation': name,
            'avg_time_ms': sum(times)/len(times),
            'stddev_ms': pd.Series(times).std(),
            'num_records': len(times),
            'query': query
        })
    df = pd.DataFrame(results)
    df.to_csv(f'results/raw/postgres_results_{record_count}_{limit_case}.csv', index=False)
    cur.close()
    conn.close()

if __name__ == '__main__':
    main() 