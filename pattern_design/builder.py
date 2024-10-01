from abc import ABC, abstractmethod


class Car:

    def __init__(self):
        self._wheel = None
        self._engine = None
        self._brand = None

    def __str__(self):
        return f"wheel = {self._wheel}, engine = {self._engine}, brand = {self._brand}"

class CarBuilder:

    def __init__(self):
        self.instance = None

    def builder(self):
        self.instance = Car()
        return self

    def add_wheel(self, wheel):
        self.instance._wheel = wheel
        return self

    def add_engine(self, engine):
        self.instance._engine = engine
        return self

    def add_brand(self, brand):
        self.instance._brand = brand
        return self

    def build(self):
        return self.instance




class Builder(ABC):

    def build_car(self):
        self.car = Car()

    def get_a_car(self):
        return self.car

class CarDetailBuilder(Builder):

    def builder(self):
        self.car = Car()
        return self

    def add_wheel(self, wheel):
        self.car._wheel = wheel
        return self

    def add_engine(self, engine):
        self.car._engine = engine
        return self

    def add_brand(self, brand):
        self.car._brand = brand
        return self






class Director:

    def __init__(self, builder):
        self.builder = builder

    def construct_car(self):
        self.builder.build_car()
        self.builder.add_brand("telsa")
        self.builder.add_engine("japan engine")
        self.builder.add_wheel("china wheel")
        return self.builder.get_a_car()


d = Director(CarDetailBuilder())
c = d.construct_car()
print(c)


builder = CarBuilder().builder()
builder.add_wheel("最好的轮子")
builder.add_brand("中国制造比亚迪")
builder.add_engine("最好的发动机")
c = builder.build()

print(c)