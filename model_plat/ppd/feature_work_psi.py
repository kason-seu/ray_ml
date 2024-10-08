import os
import pandas as pd
from typing import Tuple, List, Any
import time
import ray
import logging
from model_plat.utils import partition_list
from model_plat.feature_lib import calculate_woe_iv_by_single_feature, calculate_psi_bydf
from model_plat.feature_engine.feature_abstract import FeatureProcess

ray.init(ignore_reinit_error=True)
job_id = ray.get_runtime_context().get_job_id
print(f"ray feature process job_id={job_id}")


@ray.remote
def calculate_psi_by_feature_list(base_df_ref, target_df, feature_list, target_partition) -> List[
    Tuple[str, str, float]]:
    feature_iv_results = []
    for feature in feature_list:
        feature_iv_results.append(
            (target_partition, feature, calculate_psi_bydf(ray.get(base_df_ref), feature, target_df, feature)))

    return feature_iv_results


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
        self.pdf_ref = None

    def read(self):
        if self.pdf_ref is not None:
            return self.pdf_ref
        pdf: pd.DataFrame = pd.read_csv(self.partition, header=0,low_memory=False)
        print(pdf.dtypes)
        self.pdf_ref = ray.put(pdf)
        return self.pdf_ref

    def handle(self, num_partitions=1):
        pass


@ray.remote(num_cpus=1)
class PSIFeatureHandle(FeatureProcess):

    def __init__(self, base_feature_ref, partition, label_col):
        self.partition = partition
        self.base_feature_ref = base_feature_ref
        self.label_col = label_col
        self.pdf_ref = None

    def read(self):

        if self.pdf_ref is not None:
            return self.pdf_ref
        pdf: pd.DataFrame = pd.read_csv(self.partition, header=0, low_memory=False)
        self.pdf_ref = ray.put(pdf)
        return self.pdf_ref

    def handle(self, num_partitions=1):
        start_time = time.time()
        pdf_ref = self.read()
        print("produce data use", time.time() - start_time, 's')
        column_names = ray.get(pdf_ref).columns
        # 需要计算psi的列（排除掉目标变量y的列)
        feature_names = [n for n in column_names if n != self.label_col]
        base_df = self.base_feature_ref.read.remote()
        return self.calculate_psi_of_features_batch(base_df, pdf_ref, feature_names, self.partition, 3)

    @staticmethod
    def calculate_psi_of_features_batch(base_df_ref, df, feature_names, partition, num_partitions):
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
        task_refs = [calculate_psi_by_feature_list.remote(base_df_ref=base_df_ref, target_df=df, feature_list=sub_list,
                                                          target_partition=partition) for sub_list
                     in
                     partition_sub_lists]
        psi_values = []
        while len(task_refs) > 0:
            finished_task, task_refs = ray.wait(task_refs, num_returns=1, timeout=300)

            col_woe_iv_list = ray.get(finished_task)
            # log 耗时，去除掉
            # print(
            #     f"task_finish,cost = {time.time() - task_start_time}, cal iv and woe finished, type = {type(col_woe_iv_list)},"
            #     f"iv = {col_woe_iv_list[0]}")

            feature_iv_results = col_woe_iv_list[0]
            psi_values.extend(feature_iv_results)
        print(f"total task_finish,cost = {time.time() - task_start_time}")
        return psi_values


start = time.time()
columns = None
# base_partition = ["data/m1.csv"]
# train_partitions = ["data/m2.csv", "data/m2.csv"]
base_partition = ["data/d1_one.csv"]
train_partitions = ["data/d1_two.csv", "data/d1_three.csv"]
path = os.path.abspath("..")
# 基础数据源的数据reference获取
base_feature_actors = [
    FeatureHandler.remote(partition=os.path.join(path, partition), feature_columns=None, label_col='target')
    for partition in
    base_partition]

train_feature_actors = [
    PSIFeatureHandle.remote(base_feature_ref=base_feature_actors[0], partition=os.path.join(path, partition), label_col="target")
    for partition in
    train_partitions]

# 分区50批
train_dts = [psi_handle_actor.handle.remote(num_partitions=10) for psi_handle_actor in train_feature_actors]

for r in train_dts:
    iv_values = ray.get(r)
    for target_partition, feature, psi in iv_values:
        print(f"partition_dt = {target_partition}, feature = {feature},avg_iv = {psi}")

for bse_r in base_feature_actors:
    ray.kill(bse_r)
for r in train_feature_actors:
    ray.kill(r)

print(f"driver time cost {time.time() - start}")
