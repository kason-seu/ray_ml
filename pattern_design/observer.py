class Subject:

    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, value):
        for observer in self._observers:
            observer.update(value)


class TempSubject(Subject):

    def __init__(self):
        super().__init__()

    def temp(self, value):
        self.notify(value)


class Observer:
    def __init__(self, name):
        self._receive_value = None
        self._name = name

    def update(self, value):
        self._receive_value = value
        print(f'Observer[{self._name}] receiver subject value = {value}')


t1 = TempSubject()

o1 = Observer(name="观察者1")
o2 = Observer(name="观察者2")

t1.attach(o1)
t1.attach(o2)

t1.temp(10)
t1.temp(20)
