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

SCENARIOS = ['all', '10pct', '1pct', '1']

RESULTS_DIR = 'results/raw/'
LINE_GRAPH_DIR = 'results/line_graphs/'

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

def collect_query_times(query_name, scenario):
    sizes = []
    pg_times = []
    mongo_times = []
    # PostgreSQL
    pg_files = sorted(glob.glob(f'{RESULTS_DIR}postgres_results_*_{scenario}.csv'), key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split('_')[2]))
    for file_path in pg_files:
        n = int(os.path.splitext(os.path.basename(file_path))[0].split('_')[2])
        df = pd.read_csv(file_path)
        row = df[df['operation'] == query_name]
        if not row.empty:
            sizes.append(n)
            pg_times.append(row['avg_time_ms'].values[0])
    # MongoDB
    mongo_files = sorted(glob.glob(f'{RESULTS_DIR}mongo_results_*_{scenario}.csv'), key=lambda x: int(os.path.splitext(os.path.basename(x))[0].split('_')[2]))
    for idx, file_path in enumerate(mongo_files):
        n = int(os.path.splitext(os.path.basename(file_path))[0].split('_')[2])
        df = pd.read_csv(file_path)
        row = df[df['operation'] == query_name]
        if not row.empty:
            if idx < len(sizes) and sizes[idx] == n:
                mongo_times.append(row['avg_time_ms'].values[0])
            else:
                mongo_times.append(None)
    return sizes, pg_times, mongo_times

def plot_combined_line(query_name, file_name, scenario):
    sizes, pg_times, mongo_times = collect_query_times(query_name, scenario)
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, pg_times, marker='o', label='PostgreSQL')
    plt.plot(sizes, mongo_times, marker='o', label='MongoDB')
    plt.title(f'Response Time for "{query_name}" ({scenario})')
    plt.xlabel('Number of Records')
    plt.ylabel('Avg Response Time (ms)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{LINE_GRAPH_DIR}line_{file_name}_{scenario}_combined.png')
    plt.close()

def main():
    os.makedirs(LINE_GRAPH_DIR, exist_ok=True)
    for scenario in SCENARIOS:
        for query_name, file_name in zip(QUERY_NAMES, QUERY_FILE_NAMES):
            plot_combined_line(query_name, file_name, scenario)

if __name__ == '__main__':
    main() 