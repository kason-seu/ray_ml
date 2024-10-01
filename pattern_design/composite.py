class common_componet:

    def __init__(self, name):
        self._name = name

    def print(self):
        print(f'name{self._name}')


class File(common_componet):

    def __init__(self, name):
        super().__init__(name)

    def print(self):
        print(f"{self._name}")


class Directory(common_componet):

    def __init__(self, name):
        super().__init__(name)
        self._list = []

    def add(self, common_component_obj):
        self._list.append(common_component_obj)

    def print(self):
        print(f"{self._name}")

        for common_component_obj in self._list:
            common_component_obj.print()


d1 = Directory("first_dr")
d2 = Directory("second_dir")
f1 = File("one.txt")
d2.add(f1)
f2 = File("two.txt")
d1.add(f2)
d1.add(d2)

d1.print()