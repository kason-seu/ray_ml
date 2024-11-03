def partition_list(lst, num_partition):
    """
    将列表lst按照num_partition数量切分成多个子列表。

    参数:
    lst -- 要切分的原始列表
    num_partition -- 切分后的子列表数量

    返回:
    一个包含num_partition个子列表的列表
    """
    # 确保num_partition不为0，避免除以0错误
    if num_partition <= 0:
        raise ValueError("num_partition必须大于0")

    # 计算每个分区大约应该有的元素数量
    partition_size = len(lst) // num_partition
    remainder = len(lst) % num_partition  # 剩余的元素数量

    # 初始化结果列表
    partitions = []

    # 开始切分列表
    start_index = 0
    for i in range(num_partition):
        # 如果有剩余元素，当前分区多取一个元素
        end_index = start_index + partition_size + (1 if i < remainder else 0)
        sub_list = lst[start_index:end_index]
        # 从lst中切片并添加到partitions
        if len(sub_list) > 0:
            partitions.append(lst[start_index:end_index])
        # 更新下一次切片的起始索引
        start_index = end_index

    return partitions


if __name__ == '__main__':
    # 示例使用
    my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    num_partitions = 3
    print(partition_list(my_list, num_partitions))
    my_list = [1, 2, 3, 4, 5, 6, 7]
    num_partitions = 3
    print(partition_list(my_list, num_partitions))

    my_list = [1, 2]
    num_partitions = 3
    print(partition_list(my_list, num_partitions))