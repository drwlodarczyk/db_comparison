import subprocess
import os
import shutil

record_sizes = [10000, 20000, 30000, 50000, 80000, 100000, 150000, 250000, 500000, 1000000]
limits = ['all', '10pct', '1pct', '1']

RESULT_DIRS = [
    'results/head_mongo',
    'results/head_postgres',
    'results/summary_mongo',
    'results/summary_postgres',
    'results/plots_mongo',
    'results/plots_postgres',
    'results/line_graphs',
    'results/raw',
]

def clean_and_prepare_dirs():
    if os.path.exists('results'):
        shutil.rmtree('results')
    for d in RESULT_DIRS:
        os.makedirs(d, exist_ok=True)

def run_cmd(cmd, result_file=None):
    try:
        print(f'Running: {cmd}')
        subprocess.check_call(cmd, shell=True)
        return True
    except subprocess.CalledProcessError:
        print(f'Error running: {cmd}')
        if result_file and os.path.exists(result_file):
            os.remove(result_file)
        return False

def main():
    clean_and_prepare_dirs()
    for n in record_sizes:
        # Seed only once per record size
        run_cmd(f'python3 data_generators/postgres_seeder.py {n}')
        run_cmd(f'python3 data_generators/mongo_seeder.py {n}')
        for limit in limits:
            run_cmd(f'python3 tests/postgres_tests.py {n} {limit}', f'results/raw/postgres_results_{n}_{limit}.csv')
            run_cmd(f'python3 tests/mongo_tests.py {n} {limit}', f'results/raw/mongo_results_{n}_{limit}.csv')

if __name__ == '__main__':
    main() 