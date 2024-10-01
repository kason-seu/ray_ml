import time
from functools import wraps
from time import sleep


def enhance_function(fn):
    @wraps(fn)
    def decorator(*args, **kwargs):
        t1 = time.time()
        ret = fn(*args, **kwargs)
        t2 = time.time()
        print(f'cost = {t2 - t1}')
        return ret

    return decorator


@enhance_function
def cal():
    sleep(10)
    return 'finished'


c = cal()
print(c)