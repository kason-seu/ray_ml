
class Chinese:

    def __init__(self):
        self._lan = "chinese"

    def speak_chinese(self):
        print("谢谢")

    def get_lan(self):
        return self._lan

class American:

    def __init__(self):
        self._lan = "english"

    def speak_english(self):
        print("thanks")

    def get_lan(self):
        return self._lan

class Japan:

    def __init__(self):
        self._lan = "Japanese"

    def speak_japanese(self):
        print("哦哈哟狗砸以马斯")

    def get_lan(self):
        return self._lan

class Adapter:
    # kwargs_fns 记录的我们打算适配的方法,然后Adapter就可以调用该适配的方法了
    def __init__(self, object, **kwargs_fns):
        self._object = object
        # 讲这些内容存储到Adapter实例中，这样Adapter就能调用这些方法了
        self.__dict__.update(**kwargs_fns)
        # 下面一句他可以将object实例所有的__dict__存储的属性，方法都更新进来
        #self.__dict__.update(self._object.__dict__)

    # 获取适配的对象的其他属性信息
    def __getattr__(self, item):
        return getattr(self._object, item)


c = Chinese()
a = Adapter(c, speak = c.speak_chinese, lan = c.get_lan)
a.speak()
print(f"通过geatattr获取属性={a._lan}")
print(f"通过适配器方法获取属性={a.lan()}")

print("==============")
e = American()
american = Adapter(e, speak=e.speak_english, lan = e.get_lan)
american.speak()
print(f"通过geatattr获取属性={american._lan}")
print(f"通过适配器方法获取属性={american.lan()}")