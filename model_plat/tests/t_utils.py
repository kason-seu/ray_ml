
from model_plat.utils import partition_list


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
