import ray
import pandas as pd
from xgboost_ray import RayDMatrix, train, RayParams
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import xgboost as xgb
import numpy as np
from sklearn.datasets import make_classification

# 1. Generate and save the synthetic dataset

X, y = make_classification(n_samples=1000000, n_features=20, random_state=42)
df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])
df['label'] = y

# Split data into train and validation sets
train_df, val_df = train_test_split(df, test_size=0.05, random_state=42)

train_df.to_csv("synthetic_data.csv", index=False)
val_df.to_csv("validation_data.csv", index=False)

# 2. Load data and train models on distributed chunks using Ray

ray.init(ignore_reinit_error=True)

@ray.remote
def load_and_train_chunk(file_path, start, end, params, num_boost_round):
    chunk = pd.read_csv(file_path, skiprows=range(1, start), nrows=end - start)
    labels = chunk.pop("label")
    dtrain = RayDMatrix(chunk, label=labels)  # Using RayDMatrix here

    ray_params = RayParams(num_actors=2)  # Setting the number of actors

    bst = train(
        params,
        dtrain,
        evals=[(dtrain, "train")],
        num_boost_round=num_boost_round,
        ray_params=ray_params  # Passing the RayParams to the train function
    )

    return bst


num_rows = 950000  # 95% of 1 million
num_chunks = 10
rows_per_chunk = num_rows // num_chunks

params = {
    "objective": "binary:logistic",
    "eval_metric": ["logloss", "error"],
}

futures = [load_and_train_chunk.remote("synthetic_data.csv", i * rows_per_chunk, (i + 1) * rows_per_chunk, params, 100)
           for i in range(num_chunks)]
bst_models = ray.get(futures)

# 3. Combine these models using stacking

val_data = pd.read_csv("validation_data.csv")
y_val = val_data.pop("label")
val_dmatrix = xgb.DMatrix(val_data)

stacked_predictions = np.column_stack([
    model.predict(val_dmatrix) for model in bst_models
])

meta_model = xgb.XGBClassifier().fit(stacked_predictions, y_val)

# 4. Evaluate the ensemble on the held-out test set

final_predictions = meta_model.predict(stacked_predictions)
accuracy = accuracy_score(y_val, final_predictions)
print("Stacked Model Accuracy:", accuracy)

# Shutdown Ray
ray.shutdown()
