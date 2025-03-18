import ray

# 高级连接配置模板
# ray.init(
#     address="ray://192.168.1.6:6379",
#     _redis_password='5241590000000000',
#     # _node_ip_address="192.168.0.106",  # 客户端本机IP
#     # _system_config={
#     #     "grpc_max_attempts": 10,      # 增加gRPC重试次数
#     #     "grpc_keepalive_time_ms": 60000  # 延长keepalive时间
#     # },
#     runtime_env={
#         "env_vars": {
#             "RAY_BACKEND_LOG_LEVEL": "debug"  # 启用后端调试日志
#         }
#     },
#     logging_level="DEBUG"  # 客户端日志级别
# )


@ray.remote
def task(x):
    return x * x


futures = [task.remote(i) for i in range(10)]
print(ray.get(futures))  # 输出：[0, 1, 4, 9, 16, 25, 36, 49, 64, 81][6](@ref)
