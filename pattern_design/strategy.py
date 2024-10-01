import types


class StrategyObj:

    def __init__(self, name='策略模式', strategy_function=None):
        self._name = name
        if strategy_function:
            self.execute = types.MethodType(strategy_function, self)

    def execute(self, param):
        print(f'{self._name}default execute,with param = {param}')


def strategy1(strategyObj, param):
    print(f'[name{strategyObj._name}] strategy1 execute,with param {param}')


def strategy2(strategyObj, param):
    print(f'[name{strategyObj._name}] strategy2 execute,with param {param}')


s = StrategyObj()
s.execute(123)

s2 = StrategyObj(name="使用策略1", strategy_function=strategy1)
s2.execute(123)

s23 = StrategyObj(name="使用策略2", strategy_function=strategy2)
s23.execute(123)

