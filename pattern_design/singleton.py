
class Borg:

    # 类变量，所有实例共享类变量
    _share_data = {}

    def __init__(self):
        self.__dict__ = self._share_data


class Singleton(Borg):

    def __init__(self, **kwargs):
        Borg.__init__(self)
        self._share_data.update(**kwargs)

    def __str__(self):
        return f"{self._share_data}"


s1 =Singleton(http="asd")
print(s1)

s2 = Singleton(smtp="smtp")
print(s2)