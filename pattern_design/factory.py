class Dog:

    def __init__(self, name):
        self._name = name

    def speak(self) -> str:
        return f"{self._name} Wool"


class Cat:

    def __init__(self, name):
        self._name = name

    def speak(self) -> str:
        return f"{self._name} Meow"


def get_pet(pet="dog"):
    pets = dict(dog=Dog("WangCai"), cat=Cat("mmimi"))
    return pets[pet]


dog = get_pet("dog")
print(dog.speak())

cat = get_pet("cat")
print(cat.speak())