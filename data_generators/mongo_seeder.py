import pymongo
import random
import string
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.mongo_config import MONGO_CONFIG
from datetime import datetime

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def main():
    user_n = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    product_n = int(user_n * 0.2)
    order_n = int(user_n * 1.5)
    review_n = int(order_n * 0.5)
    client = pymongo.MongoClient(MONGO_CONFIG['host'], MONGO_CONFIG['port'])
    db = client[MONGO_CONFIG['database']]
    db.users.drop()
    db.products.drop()
    db.orders.drop()
    db.order_reviews.drop()
    users = [{
        'name': random_string(8),
        'email': f"{random_string(5)}_{i}@mail.com"
    } for i in range(user_n)]
    db.users.insert_many(users)
    db.users.create_index('_id')
    products = [{
        'name': random_string(10),
        'category': random.choice(['Shirts', 'Pants', 'Shoes', 'Accessories']),
        'price': round(random.uniform(10, 200), 2)
    } for _ in range(product_n)]
    db.products.insert_many(products)
    db.products.create_index([('category', 1)])
    user_ids = list(db.users.find({}, {'_id': 1}))
    product_ids = list(db.products.find({}, {'_id': 1}))
    orders = [{
        'user_id': random.choice(user_ids)['_id'],
        'order_date': datetime.utcnow()
    } for _ in range(order_n)]
    db.orders.insert_many(orders)
    db.orders.create_index([('user_id', 1)])
    order_ids = list(db.orders.find({}, {'_id': 1}))
    reviews = [{
        'order_id': random.choice(order_ids)['_id'],
        'product_id': random.choice(product_ids)['_id'],
        'rating': random.randint(1, 5),
        'review': random_string(20)
    } for _ in range(review_n)]
    db.order_reviews.insert_many(reviews)
    db.order_reviews.create_index([('product_id', 1)])
    db.order_reviews.create_index([('order_id', 1)])
    print('Done.')

if __name__ == '__main__':
    main() 