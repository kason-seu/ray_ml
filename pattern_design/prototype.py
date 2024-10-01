import copy


class Prototype:

    def __init__(self):
        self._objects = {}

    def reigister_object(self, name, obj):
        self._objects[name] = obj

    def unregister_object(self, name):
        del self._objects[name]

    def clone(self,name, **kwargs):
        obj = copy.deepcopy(self._objects.get(name))
        obj.__dict__.update(kwargs)
        return obj

class Car:

    def __init__(self, color='red', brand='china'):
        self._color = color
        self._brand = brand

    def print_car(self):
        print(f"color = {self._color}, brand = {self._brand}")


c = Car()
p = Prototype()

p.reigister_object('car', c)
c = p.clone('car', _color='green', _brand='japen')
c.print_car()