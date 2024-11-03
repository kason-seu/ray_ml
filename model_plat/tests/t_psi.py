import time

import pandas as pd
import numpy as np
from model_plat.feature.feature_lib import calculate_psi, calculate_psi_v2, calculate_psi_bydf

# 生成模拟的训练样本评分和测试样本评分
# np.random.seed(0)
# prob_dev = np.random.rand(5000)
# prob_test = np.random.rand(5000)
np.random.seed(324)

probas = np.random.random(10000).reshape(-1, 1)
train_proba = probas[: 9000]
test_proba = probas[9000:]

#评分转换为 DataFrame 格式
df_dev = pd.DataFrame(train_proba, columns=['score'])
df_test = pd.DataFrame(test_proba, columns=['score'])

start_time = time.time()
psi = calculate_psi_bydf(df_dev, 'score', df_test, 'score')
t2 = time.time()
print("PSI1 值为:", psi, "v1 cost", (t2 - start_time))
psi = calculate_psi(train_proba, test_proba, bins=10)
t3 = time.time()
print("PSI1 值为:", psi, "v1 cost", (t3 - t2))


psi_v3 = calculate_psi_v2(train_proba, test_proba, bins=10)
print("PSI2 值为 ", psi_v3, "v2 cost", (time.time() - t3))