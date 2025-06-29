import pandas as pd
import glob
import os
import matplotlib.pyplot as plt

QUERY_NAMES = [
    'Select all users',
    'Select all products in category',
    'Select all orders for user',
    'Top 10 best-selling products',
    'Average rating per product'
]

QUERY_FILE_NAMES = [
    'select_all_users',
    'select_all_products_in_category',
    'select_all_orders_for_user',
    'top_10_best_selling_products',
    'average_rating_per_product'
]

def analyze_csv(file_path, dbtype, n):
    print(f'\nAnalyzing {file_path}')
    df = pd.read_csv(file_path)
    # Save summary statistics
    summary = df.describe()
    summary.to_csv(f'results/summary_{dbtype}_{n}.csv')
    # Save head
    df.head().to_csv(f'results/head_{dbtype}_{n}.csv', index=False)
    # Save plot
    plt.figure(figsize=(10, 6))
    df.plot(x='operation', y='avg_time_ms', kind='bar', legend=False, ax=plt.gca())
    plt.title(f'Average Query Time: {dbtype} {n}')
    plt.ylabel('ms')
    plt.tight_layout()
    plt.savefig(f'results/plot_{dbtype}_{n}.png')
    plt.close()

def collect_query_times(query_name):
    sizes = []
    pg_times = []
    mongo_times = []
    # PostgreSQL
    pg_files = sorted(glob.glob('results/postgres_results_*.csv'), key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split('_')[-1]))
    for file_path in pg_files:
        n = int(os.path.splitext(os.path.basename(file_path))[0].split('_')[-1])
        df = pd.read_csv(file_path)
        row = df[df['operation'] == query_name]
        if not row.empty:
            sizes.append(n)
            pg_times.append(row['avg_time_ms'].values[0])
    # MongoDB
    mongo_files = sorted(glob.glob('results/mongo_results_*.csv'), key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split('_')[-1]))
    for idx, file_path in enumerate(mongo_files):
        n = int(os.path.splitext(os.path.basename(file_path))[0].split('_')[-1])
        df = pd.read_csv(file_path)
        row = df[df['operation'] == query_name]
        if not row.empty:
            # Ensure sizes are aligned
            if idx < len(sizes) and sizes[idx] == n:
                mongo_times.append(row['avg_time_ms'].values[0])
            else:
                # If not aligned, insert None
                mongo_times.append(None)
    return sizes, pg_times, mongo_times

def plot_combined_line(query_name, file_name):
    sizes, pg_times, mongo_times = collect_query_times(query_name)
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, pg_times, marker='o', label='PostgreSQL')
    plt.plot(sizes, mongo_times, marker='o', label='MongoDB')
    plt.title(f'Response Time for "{query_name}"')
    plt.xlabel('Number of Records')
    plt.ylabel('Avg Response Time (ms)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'results/line_{file_name}_combined.png')
    plt.close()

def main():
    for pattern, dbtype in [("results/postgres_results_*.csv", "postgres"), ("results/mongo_results_*.csv", "mongo")]:
        for file_path in sorted(glob.glob(pattern)):
            n = os.path.splitext(os.path.basename(file_path))[0].split('_')[-1]
            analyze_csv(file_path, dbtype, n)
    for query_name, file_name in zip(QUERY_NAMES, QUERY_FILE_NAMES):
        plot_combined_line(query_name, file_name)

if __name__ == '__main__':
    main() 