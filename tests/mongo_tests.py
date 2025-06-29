import sys
import os
import math
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pymongo
import time
import pandas as pd
from config.mongo_config import MONGO_CONFIG
from datetime import datetime

def run_query(collection, query_func):
    start = time.time()
    _ = query_func()
    end = time.time()
    return (end - start) * 1000  # ms

def get_id_range(collection, count):
    total = collection.count_documents({})
    if total == 0:
        return None, None
    if count >= total:
        first = collection.find_one({}, sort=[('_id', 1)])
        last = collection.find_one({}, sort=[('_id', -1)])
        return first['_id'], last['_id']
    first = collection.find_one({}, sort=[('_id', 1)])
    last = collection.find({}, sort=[('_id', 1)]).skip(count - 1).limit(1).next()
    return first['_id'], last['_id']

def main():
    record_count = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    limit_case = sys.argv[2] if len(sys.argv) > 2 else 'all'
    if limit_case == 'all':
        range_count = record_count
    elif limit_case == '10pct':
        range_count = max(1, math.ceil(record_count * 0.1))
    elif limit_case == '1pct':
        range_count = max(1, math.ceil(record_count * 0.01))
    else:
        range_count = 1
    client = pymongo.MongoClient(MONGO_CONFIG['host'], MONGO_CONFIG['port'])
    db = client[MONGO_CONFIG['database']]
    if db.users.count_documents({}) < record_count:
        os.system(f"python3 data_generators/mongo_seeder.py {record_count}")
    results = []
    user_doc = db.users.find_one({})
    user_min, user_max = get_id_range(db.users, range_count)
    prod_min, prod_max = get_id_range(db.products, range_count)
    order_min, order_max = get_id_range(db.orders, range_count)
    queries = [
        ("Select all users", lambda: list(db.users.find({'_id': {'$gte': user_min, '$lte': user_max}}))),
        ("Select all products in category", lambda: list(db.products.find({'category': 'Shirts', '_id': {'$gte': prod_min, '$lte': prod_max}}))),
    ]
    if user_doc:
        queries.append(("Select all orders for user", lambda: list(db.orders.find({'user_id': user_doc['_id'], '_id': {'$gte': order_min, '$lte': order_max}}))))
    queries += [
        ("Top 10 best-selling products", lambda: list(db.order_reviews.aggregate([
            {'$group': {'_id': '$product_id', 'cnt': {'$sum': 1}}},
            {'$sort': {'cnt': -1}},
            {'$limit': 10}
        ]))),
        ("Average rating per product", lambda: list(db.order_reviews.aggregate([
            {'$group': {'_id': '$product_id', 'avg_rating': {'$avg': '$rating'}}},
            {'$limit': 10}
        ]))),
    ]
    for name, func in queries:
        times = []
        for _ in range(5):
            t = run_query(db, func)
            times.append(t)
        results.append({
            'operation': name,
            'avg_time_ms': sum(times)/len(times),
            'stddev_ms': pd.Series(times).std(),
            'num_records': len(times),
            'query': str(func)
        })
    df = pd.DataFrame(results)
    df.to_csv(f'results/raw/mongo_results_{record_count}_{limit_case}.csv', index=False)
    client.close()

if __name__ == '__main__':
    main() 