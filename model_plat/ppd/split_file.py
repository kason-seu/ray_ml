import os.path

import pandas as pd

path = os.path.abspath("..")

data_path = os.path.join(path, "data/allData_1.csv")

df = pd.read_csv(data_path, header=0, low_memory=False)

print(df.head())

print(df.shape)

rows = df.shape[0]
df_one = df.loc[0: rows / 3, :]

df_one.to_csv(os.path.join(path, 'data/d1_one.csv'), header=True, columns=df.columns, index=False)


df_two = df.loc[rows / 3 + 1:(rows / 3) * 2, :]
df_two.to_csv(os.path.join(path, 'data/d1_two.csv'), header=True, columns=df.columns, index=False)


df_three = df.loc[(rows / 3) * 2 + 1:rows, :]
df_three.to_csv(os.path.join(path, 'data/d1_three.csv'), header=True, columns=df.columns, index=False)