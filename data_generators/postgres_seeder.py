import psycopg2
import random
import string
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.postgres_config import POSTGRES_CONFIG

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def create_schema(cur):
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100) UNIQUE
        );
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            category VARCHAR(50),
            price NUMERIC
        );
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            order_date TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS order_reviews (
            id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES orders(id),
            product_id INTEGER REFERENCES products(id),
            rating INTEGER,
            review TEXT
        );
    ''')

def truncate_tables(cur):
    cur.execute('''
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'order_reviews') THEN
                EXECUTE 'TRUNCATE TABLE order_reviews RESTART IDENTITY CASCADE';
            END IF;
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'orders') THEN
                EXECUTE 'TRUNCATE TABLE orders RESTART IDENTITY CASCADE';
            END IF;
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'products') THEN
                EXECUTE 'TRUNCATE TABLE products RESTART IDENTITY CASCADE';
            END IF;
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
                EXECUTE 'TRUNCATE TABLE users RESTART IDENTITY CASCADE';
            END IF;
        END
        $$;
    ''')

def seed_users(cur, n):
    for i in range(n):
        cur.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (random_string(8), f"{random_string(5)}_{i}@mail.com")
        )

def seed_products(cur, n):
    categories = ['Shirts', 'Pants', 'Shoes', 'Accessories']
    for _ in range(n):
        cur.execute(
            "INSERT INTO products (name, category, price) VALUES (%s, %s, %s)",
            (random_string(10), random.choice(categories), round(random.uniform(10, 200), 2))
        )

def seed_orders(cur, n, user_count):
    for _ in range(n):
        cur.execute(
            "INSERT INTO orders (user_id, order_date) VALUES (%s, NOW())",
            (random.randint(1, user_count),)
        )

def seed_order_reviews(cur, n, order_count, product_count):
    for _ in range(n):
        cur.execute(
            "INSERT INTO order_reviews (order_id, product_id, rating, review) VALUES (%s, %s, %s, %s)",
            (
                random.randint(1, order_count),
                random.randint(1, product_count),
                random.randint(1, 5),
                random_string(20)
            )
        )

def main():
    user_n = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    product_n = int(user_n * 0.2)
    order_n = int(user_n * 1.5)
    review_n = int(order_n * 0.5)
    conn = psycopg2.connect(**POSTGRES_CONFIG)
    cur = conn.cursor()
    create_schema(cur)
    truncate_tables(cur)
    print('Seeding users...')
    seed_users(cur, user_n)
    print('Seeding products...')
    seed_products(cur, product_n)
    print('Seeding orders...')
    seed_orders(cur, order_n, user_n)
    print('Seeding order reviews...')
    seed_order_reviews(cur, review_n, order_n, product_n)
    conn.commit()
    cur.close()
    conn.close()
    print('Done.')

if __name__ == '__main__':
    main() 