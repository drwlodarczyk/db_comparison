import os
import psutil
import pandas as pd
import subprocess

def get_postgres_db_size(dbname):
    try:
        result = subprocess.check_output([
            'psql', '-d', dbname, '-c', "SELECT pg_database_size('%s');" % dbname, '-t', '-A'
        ])
        return int(result.strip())
    except Exception as e:
        print('Error getting Postgres size:', e)
        return None

def get_mongo_db_size(dbname):
    try:
        import pymongo
        client = pymongo.MongoClient('localhost', 27017)
        db = client[dbname]
        stats = db.command('dbstats')
        return stats['dataSize']
    except Exception as e:
        print('Error getting MongoDB size:', e)
        return None

def get_memory_usage():
    return psutil.virtual_memory().used

def main():
    data = []
    dbs = ['db_comparison']
    for db in dbs:
        pg_size = get_postgres_db_size(db)
        mongo_size = get_mongo_db_size(db)
        mem = get_memory_usage()
        data.append({'db': db, 'postgres_size': pg_size, 'mongo_size': mongo_size, 'memory_used': mem})
    df = pd.DataFrame(data)
    df.to_csv('results/db_metrics.csv', index=False)

if __name__ == '__main__':
    main() 