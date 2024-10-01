import ray
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import numpy as np
# Initialize Ray
ray.init()


@ray.remote
def train_decision_tree(subset_x, subset_y):
    """Train a decision tree on a subset of data."""
    clf = DecisionTreeClassifier()
    clf.fit(subset_x, subset_y)
    return clf


def distribute_training(data, labels, num_splits=4):
    """Distribute training across multiple cores using Ray."""
    # Split the data into multiple subsets
    chunked_data = np.array_split(data, num_splits)
    chunked_labels = np.array_split(labels, num_splits)

    # Distribute the training tasks
    futures = [train_decision_tree.remote(chunked_data[i], chunked_labels[i]) for i in range(num_splits)]

    # Fetch results
    models = ray.get(futures)
    return models


if __name__ == "__main__":
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(iris.data, iris.target, test_size=0.2, random_state=42)

    models = distribute_training(X_train, y_train)
    for model in models:
        score = model.score(X_test, y_test)
        print(f"Model accuracy: {score:.2f}")

# Shutdown Ray
ray.shutdown()
