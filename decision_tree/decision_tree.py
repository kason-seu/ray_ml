from sklearn.datasets import load_iris
import pandas as pd
import numpy as np
import ray
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier

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
def train_decision_tree(X, y):
    """Train a decision tree on given data."""
    clf = DecisionTreeClassifier()
    clf.fit(X, y)
    return clf


def distributed_loading_and_training(file_paths):
    """Distribute data loading and training across cores using Ray."""

    # Distribute the data loading tasks
    data_futures = [load_data.remote(file) for file in file_paths]
    datasets = ray.get(data_futures)

    # Distribute the training tasks
    training_futures = [train_decision_tree.remote(X, y) for X, y in datasets]
    models = ray.get(training_futures)

    return models


# if __name__ == "__main__":
#     # Assume you have data split across 4 CSV files
#     file_paths = ["data1.csv", "data2.csv", "data3.csv", "data4.csv"]
#
#     models = distributed_loading_and_training(file_paths)
#     # Note: For demonstration purposes, this example lacks testing and accuracy reporting.
#     # You can extend it as per the previous example.



#file_paths = create_mock_csv_files()
#print(f"Created CSV files: {file_paths}")

if __name__ == "__main__":
    file_paths = create_mock_csv_files()
    print(f"Created CSV files: {file_paths}")
    # Initialize Ray
    ray.init()
    models = distributed_loading_and_training(file_paths)

    # Test the performance of one of the models
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.2, random_state=42)
    predictions = models[0].predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    print(f"Model accuracy: {accuracy:.2f}")
    # Shutdown Ray
    ray.shutdown()
