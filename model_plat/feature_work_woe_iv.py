import os
import pandas as pd
from typing import Tuple, List, Any
import time
import ray
import logging
from feature.utils import partition_list
from feature.feature_lib import calculate_woe_iv_by_single_feature
from feature.feature_abstract import FeatureProcess

ray.init()
job_id = ray.get_runtime_context().get_job_id
print(f"ray feature process job_id={job_id}")


@ray.remote
def calculate_woe_iv_by_feature_list(df, feature_list, target) -> List[Tuple[str, Any, float]]:
    feature_iv_results = []
    for feature in feature_list:
        feature_iv_results.append(calculate_woe_iv_by_single_feature(df, feature, target))

    return feature_iv_results


@ray.remote
def calculate_woe_iv_by_feature(df, feature, target) -> Tuple[str, Any, float]:
    """

    Args:
        df:
        feature:
        target:

    Returns: tuple(特征列名，_， iv值)

    """
    return calculate_woe_iv_by_single_feature(df, feature, target)


@ray.remote(num_cpus=1)
class FeatureHandler(FeatureProcess):
    def __init__(self, partition, feature_columns=None, label_col=None):
        if feature_columns is None:
            feature_columns = []
        self.partition = partition
        self.label_col = label_col
        self.feature_columns = feature_columns
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def calculate_woe_iv_of_features_batch(df, feature_names, target, num_partitions):
        """
        将所有的特征列，按照批次进行分批进行并发计算
        :param df:
        :param feature_names:
        :param target:
        :param num_partitions:
        :return:
        """
        task_start_time = time.time()
        partition_sub_lists = partition_list(feature_names, num_partitions)
        task_refs = [calculate_woe_iv_by_feature_list.remote(df=df, feature_list=sub_list, target=target) for sub_list
                     in
                     partition_sub_lists]
        woe_iv_values = []
        while len(task_refs) > 0:
            finished_task, task_refs = ray.wait(task_refs, num_returns=1, timeout=300)

            col_woe_iv_list = ray.get(finished_task)
            # log 耗时，去除掉
            # print(
            #     f"task_finish,cost = {time.time() - task_start_time}, cal iv and woe finished, type = {type(col_woe_iv_list)},"
            #     f"iv = {col_woe_iv_list[0]}")

            col_woe_iv: List[Tuple[str, Any, float]] = col_woe_iv_list[0]
            woe_iv_values.extend(col_woe_iv)
        print(f"total task_finish,cost = {time.time() - task_start_time}")
        return woe_iv_values

    @staticmethod
    def calculate_woe_iv_of_features_onebyone(train_data, label_column_name, column_names=None) -> List[
        Tuple[str, Any, float]]:
        """

        Args:
            train_data:
            label_column_name:
            column_names:

        Returns:

        """
        # WOE Encode For category column
        columns_features = [i for i in column_names if i != label_column_name]  # column names except label column
        # calculate IV value for category column
        print(f"label = {label_column_name}, cols_size = {len(columns_features)}, columns_features={columns_features}")
        woe_iv_values = []
        task_start_time = time.time()
        woe_iv_tasks_ref = [calculate_woe_iv_by_feature.remote(df=train_data, feature=col, target=label_column_name) for
                            col in columns_features]
        while len(woe_iv_tasks_ref) > 0:
            finished_task, woe_iv_tasks_ref = ray.wait(woe_iv_tasks_ref, num_returns=1, timeout=300)
            col_woe_iv_list = ray.get(finished_task)
            # print(
            #     f"task_finish,cost = {time.time() - task_start_time}, cal iv and woe finished, type = {type(col_woe_iv_list)},"
            #     f"iv = {col_woe_iv_list[0]}")
            col_woe_iv: Tuple[str, Any, float] = col_woe_iv_list[0]
            woe_iv_values.append((col_woe_iv[0], _, col_woe_iv[2]))
        print(f"total task_finish,cost = {time.time() - task_start_time}")
        return woe_iv_values

    def read(self):
        pdf: pd.DataFrame = pd.read_csv(self.partition, header=0)
        return pdf

    def handle(self, num_partitions=1):
        start_time = time.time()
        pdf: pd.DataFrame = self.read()
        pdf_ref = ray.put(pdf)
        print("produce data use", time.time() - start_time, 's')
        column_names = pdf.columns
        feature_names = [n for n in column_names if n != self.label_col]
        # 使用reference传递大对象
        # return self.calculate_iv(pdf_ref, self.label_col, column_names=column_names)
        return self.partition, self.calculate_woe_iv_of_features_batch(pdf_ref, feature_names=feature_names,
                                                                       target=self.label_col,
                                                                       num_partitions=num_partitions)


start = time.time()
columns = None
train_partitions = ["data/d1_one.csv", "data/d1_two.csv", "data/d1_three.csv"]
path = os.path.abspath("")
feature_handler_actors = [
    FeatureHandler.remote(partition=os.path.join(path, partition), feature_columns=None, label_col='target')
    for partition in
    train_partitions]
# 分区50批
train_dts = [feature_handle_actor.handle.remote(num_partitions=50) for feature_handle_actor in feature_handler_actors]

for r in train_dts:
    partition_dt, iv_values = ray.get(r)
    for c, _, avg_iv in iv_values:
        print(f"partition_dt = {partition_dt}, feature = {c},avg_iv = {avg_iv}")
for r in feature_handler_actors:
    ray.kill(r)

print(f"driver time cost {time.time() - start}")
