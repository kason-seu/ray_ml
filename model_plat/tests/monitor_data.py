import pandas as pd
import numpy as np
from model_plat.feature_lib import calculate_psi_bydf

df = pd.DataFrame({
    "f1": np.random.randint(low = 101, high=1000, size = 1000, dtype='int'),
    "f2": np.random.randint(low = 301, high=1000, size = 1000, dtype='int'),
    "f3": np.random.randint(low = 201, high=1000, size = 1000, dtype='int'),
    "target": np.random.randint(2, size=1000)
})

import os
p = os.path.abspath("..")
df.to_csv(os.path.join(p, "data/m1.csv"), index=False)



df2 = pd.DataFrame({
    "f1": np.random.randint(low = 101, high=1000, size = 1000, dtype='int'),
    "f2": np.random.randint(low = 301, high=1000, size = 1000, dtype='int'),
    "f3": np.random.randint(low = 201, high=1000, size = 1000, dtype='int'),
    "target": np.random.randint(2, size=1000)
})


p = os.path.abspath("..")
df2.to_csv(os.path.join(p, "data/m2.csv"), index=False)



psi = calculate_psi_bydf(df, 'target', df2, 'target')

print(df['target'].head())