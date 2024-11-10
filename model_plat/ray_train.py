import ray
from ray.train import ScalingConfig
from ray.train.lightgbm import LightGBMTrainer, RayTrainReportCallback


# 初始化 Ray
ray.init(ignore_reinit_error=True)

# 定义存储 metrics 的变量
metrics_data = []


# 设置回调
class CustomRayTrainReportCallback(RayTrainReportCallback):
    def __init__(self):
        super().__init__()

    def on_epoch_end(self, iteration, evals_log):
        # 在每次 epoch 结束时保存 metrics
        print(f'iter:{iteration}, {evals_log}')
        metrics_data.append(evals_log)
        super().on_epoch_end(iteration, evals_log)


callbacks = [CustomRayTrainReportCallback()]
train_dataset = ray.data.from_items(
    [{"x": x, "y": x + 1} for x in range(32)]
)
trainer = LightGBMTrainer(
    label_column="y",
    params={"objective": "regression"},
    scaling_config=ScalingConfig(num_workers=1),
    datasets={"train": train_dataset},
    callbacks=callbacks
)
result = trainer.fit()
print(result)
