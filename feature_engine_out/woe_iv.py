import pandas as pd
import numpy as np
import ray


# Generate synthetic data
def generate_data(n_samples=1000):
    feature_data = np.random.choice(['A', 'B', 'C'], n_samples)
    target_data = np.random.randint(0, 2, n_samples)
    return pd.DataFrame({'feature': feature_data, 'target': target_data})


# Save to multiple files
num_files = 3
for i in range(num_files):
    df = generate_data()
    df.to_csv(f"file{i + 1}.csv", index=False)

ray.init(ignore_reinit_error=True)


@ray.remote
def calculate_woe_iv(file_path, feature, target):
    # Load the data from the file
    data = pd.read_csv(file_path)

    # Calculate WoE and IV

    event = data[target].sum()
    non_event = len(data) - event

    agg = data.groupby(feature)[target].agg(['count', 'sum'])
    agg['non_event'] = agg['count'] - agg['sum']
    agg = agg.rename(columns={'sum': 'event'})

    agg['woe'] = np.log(((agg['event'] + 0.5) / event) / ((agg['non_event'] + 0.5) / non_event))
    agg['iv'] = (agg['event'] / event - agg['non_event'] / non_event) * agg['woe']
    iv = agg['iv'].sum()

    return agg['woe'].to_dict(), iv


def distributed_woe_iv(file_paths, feature, target):
    futures = [calculate_woe_iv.remote(file, feature, target) for file in file_paths]
    results = ray.get(futures)

    all_woes = {}
    total_iv = 0
    for woe, iv in results:
        total_iv += iv
        for k, v in woe.items():
            if k not in all_woes:
                all_woes[k] = []
            all_woes[k].append(v)

    avg_woe = {k: np.mean(v) for k, v in all_woes.items()}
    avg_iv = total_iv / len(file_paths)

    return avg_woe, avg_iv


# Calculate WoE and IV using generated files
file_paths = [f"file{i + 1}.csv" for i in range(num_files)]
woe, iv = distributed_woe_iv(file_paths, 'feature', 'target')
print("WoE:", woe)
print("IV:", iv)

ray.shutdown()
