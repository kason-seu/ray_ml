from sklearn.datasets import load_iris
import pandas as pd
import numpy as np
import ray
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier

def create_mock_csv_files(num_files=4):
    iris = load_iris()
    df = pd.DataFrame(data=np.c_[iris['data'], iris['target']], columns=iris['feature_names'] + ['target'])

    # Split and save to CSV
    chunked_data = np.array_split(df, num_files)
    file_paths = []
    for i, chunk in enumerate(chunked_data):
        file_name = f"data{i + 1}.csv"
        chunk.to_csv(file_name, index=False)
        file_paths.append(file_name)

    return file_paths




@ray.remote
def load_data(file_path):
    """Load data from a given file."""
    # For demonstration, I'm assuming the data is in CSV format.
    data = pd.read_csv(file_path)
    X = data.drop('target', axis=1).values
    y = data['target'].values
    return X, y


@ray.remote
def train_random_forest(X, y):
    """Train a random forest on given data."""
    clf = RandomForestClassifier(n_estimators=10)  # Using 10 trees for demonstration
    clf.fit(X, y)
    return clf


def distributed_loading_and_training(file_paths):
    """Distribute data loading and training across cores using Ray."""

    # Distribute the data loading tasks
    data_futures = [load_data.remote(file) for file in file_paths]
    datasets = ray.get(data_futures)

    # Distribute the training tasks
    training_futures = [train_random_forest.remote(X, y) for X, y in datasets]
    models = ray.get(training_futures)

    return models


if __name__ == "__main__":
    file_paths = create_mock_csv_files()
    print(f"Created CSV files: {file_paths}")
    # Initialize Ray
    ray.init()
    models = distributed_loading_and_training(file_paths)

    # Testing the ensemble's performance
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.2, random_state=42)

    # Average the predictions from all models to get the final prediction
    predictions = []
    for x in X_test:
        model_predictions = [model.predict([x])[0] for model in models]
        # Using majority voting for classification
        final_prediction = max(set(model_predictions), key=model_predictions.count)
        predictions.append(final_prediction)

    accuracy = accuracy_score(y_test, predictions)
    print(f"Ensemble model accuracy: {accuracy:.2f}")
    # Shutdown Ray
    ray.shutdown()


