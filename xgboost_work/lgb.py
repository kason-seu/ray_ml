import ray
from ray import tune
from ray.train import Trainer
from ray.train.lightgbm import LightGBMTrainer
from ray.train.checkpointable import Checkpointable

from ray.train import Trainer, Checkpointable
from lightgbm import LGBMClassifier
import numpy as np

# ==================================================================
# 1. 初始化 Ray 和数据准备
# ==================================================================
ray.init(address="auto", num_cpus=4)

# 生成示例数据（二分类任务）
X, y = np.random.rand(10000, 100), np.random.randint(0, 2, 10000)
X_val, y_val = X[:1000], y[:1000]

# 将数据分片为 10 个部分（与 Ray 资源数匹配）
dataset = ray.train.dataset.from_numpy((X, y)).split(10)


# ==================================================================
# 2. 定义分布式训练任务（继承 Checkpointable）
# ==================================================================
class LightGBMTrainer(Checkpointable):
    def __init__(self, config):
        self.config = config
        self.model = None

    def setup(self, split_idx):
        X, y = ray.train.dataset.get_split(split_idx)
        self.model = LGBMClassifier(
            objective="binary",
            metric="auc",
            early_stopping_rounds=50,
            n_estimators=self.config["n_estimators"]
        )

    def train(self):
        self.model.fit(X, y)
        return self.model

    def save(self, checkpoint_dir):
        self.model.save_model(checkpoint_dir)

    def load(self, checkpoint_dir):
        self.model = LGBMClassifier()
        self.model.load_model(checkpoint_dir)


# ==================================================================
# 3. 使用 Ray `Trainer` API 实现分布式训练
# ==================================================================
def distributed_train():
    best_auc = -1.0
    patience_counter = 0

    for epoch in range(100):
        # 创建并启动分布式训练任务
        trainer = Trainer(
            num_workers=4,
            max_epochs=1,
            config={"n_estimators": 1000},
        )

        # 分片训练并合并模型
        models = trainer.train(dataset)
        merged_model = models[0]
        for model in models[1:]:
            merged_model.merge(model)

        current_auc = merged_model.score(X_val, y_val)
        print(f"Epoch {epoch}: Validation AUC={current_auc:.4f}")

        # 更新全局早停状态
        if current_auc > best_auc + 1e-9:
            best_auc = current_auc
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= 5:
                print("Early stopping triggered")
                break

    return best_auc


# 执行训练并输出结果
final_auc = distributed_train()
print(f"\n分布式训练完成！最佳验证 AUC: {final_auc:.4f}")