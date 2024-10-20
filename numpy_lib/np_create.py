import numpy as np

# create numpy
print("first------------------")
a = np.array([1,2,3,4])
print(a.shape)
print(a.size)
print(a.dtype)

print("second------------------")
a = np.arange(3.0)
print(a.shape)
print(a.size)
print(a.dtype)
print("second------------------")
a = np.arange(1, 10, 2)
print(a.shape)
print(a.size)
print(a.dtype)

print("second------------------")
a = np.arange(1, 10, 2)
print(a.shape)
print(a.size)
print(a.dtype)

# dataframe、Series转换numpy
import os

dir_path = os.path.abspath("../")
file_path = os.path.join(dir_path, "model_plat/data/allData_1.csv")
import pandas as pd

df = pd.read_csv(file_path, low_memory=False)

arr = df.to_numpy()
print(arr, np.size(arr))
arr = np.array(df)
print(arr, np.size(arr))
arr = df.values
print(arr, np.size(arr))