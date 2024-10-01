import abc


# 维度(独立)， 拆分m * n个子类变成 m+ n个子类

class PayMode(abc.ABC):

    def __init__(self, payFunc):
        self.payFunc = payFunc
        pass

    @abc.abstractmethod
    def pay(self, **kwargs):
        pass


class WxPayMode(PayMode):

    def __init__(self, payFunc):
        super().__init__(payFunc)
        self.payMode = '使用微信支付'

    def pay(self, **kwargs):
        print(f'wake up 微信 app， open it')
        self.payFunc.input(**kwargs)
        check = self.payFunc.security_check(**kwargs)
        if check:
            self.payFunc.pay(**kwargs)
        else:
            print(f'check failed')


class ZhifuBaoPayMode(PayMode):

    def __init__(self, payFunc):
        super().__init__(payFunc)
        self.payMode = '支付宝支付'

    def pay(self, **kwargs):
        print(f'wake up 支付宝 app， open it')
        self.payFunc.input(**kwargs)
        check = self.payFunc.security_check(**kwargs)
        if check:
            self.payFunc.pay(**kwargs)
        else:
            print(f'check failed')


class PayFunc(abc.ABC):

    def __init__(self):
        pass

    @abc.abstractmethod
    def security_check(self, userId):
        pass

    @abc.abstractmethod
    def pay(self, amount):
        pass


class PwdPayFunc(PayFunc):

    def __init__(self):
        super().__init__()

    def input(self, **kwargs):
        uid = kwargs["userId"]
        pwd = kwargs["pwd"]
        print(f'输入用户名和密码 userId = {uid}, pwd = {pwd}')

    def security_check(self, **kwargs):
        print(f'校验用户名在数据库里面存在, 以及密码是否正确')
        return True

    def pay(self, **kwargs):
        amount = kwargs["amount"]
        print(f"根据用户名和密码支付相应金额, 付款amount = {amount}")


class FacePayFunc(PayFunc):
    def __init__(self):
        super().__init__()

    def input(self, **kwargs):
        uid = kwargs["userId"]
        face = kwargs["face"]
        print(f'输入用户名和密码 userId = {uid}, face = {face}')

    def security_check(self, **kwargs):
        print(f'校验保留的人脸信息')
        return True

    def pay(self, **kwargs):
        amount = kwargs["amount"]
        print(f"扫脸支付相应金额,付款amount = {amount}")


class FingerPrintPayFunc(PayFunc):
    def __init__(self):
        super().__init__()

    def input(self, **kwargs):
        uid = kwargs["userId"]
        fingerprint = kwargs["fingerprint"]
        print(f'输入用户名和密码 userId = {uid}, fingerprint = {fingerprint}')

    def security_check(self, **kwargs):
        print(f'校验保留的指纹信息')
        return True

    def pay(self, **kwargs):
        amount = kwargs["amount"]
        print(f"指纹支付相应金额, 付款amount = {amount}")


c = WxPayMode(payFunc=PwdPayFunc())

c.pay(userId= "张三", pwd = "123", amount = 123.0)