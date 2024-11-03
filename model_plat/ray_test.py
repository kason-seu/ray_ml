import time

import ray


@ray.remote
def hello_world():
    return "hello world"


# Automatically connect to the running Ray cluster.
# ray.init(address="auto")
ray.init()
print("############")
print(ray.get(hello_world.remote()))
