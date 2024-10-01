import ray
import typing
@ray.remote
def fn(i) -> int:
    return i * i


def gn(*args, **kwargs) -> typing.Tuple[int,int]:
    return len(args) , len(kwargs)

if __name__ == "__main__":
    #ray.init(address='192.168.1.6:6379')
    ray.init("ray://192.168.1.6:10001")
    ref = fn.remote(i=3)
    print(ray.get(ref))

    gn_ref = ray.remote(**{"num_cpus":2.0})(gn)
    gnArgsAnsRef, gnKwargsAnsRef = gn_ref.options(num_returns=2).remote(*[1,2,3], **{"a":1})
    print(ray.get(gnArgsAnsRef))
    print(ray.get(gnKwargsAnsRef))
