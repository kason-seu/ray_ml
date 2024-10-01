class Dog:
    def __init__(self, name):
        self._name = name


class DogFood:
    def __init__(self, brand, madecity):
        self._brand = brand
        self._madecity = madecity


"""具体的工厂"""


class DogFactory:

    def get_pet(self):
        return Dog("Peiqi")

    def get_food(self):
        return DogFood("金牌狗粮", "中国制造")


"""抽象工厂"""


class PetStore:

    def __init__(self, pet_factory):
        self._pet_factory = pet_factory

    def show(self):
        pet = self._pet_factory.get_pet()
        food = self._pet_factory.get_food()
        print(f"宠物是{pet._name},食物品牌{food._brand}")


pet_store = PetStore(DogFactory())
pet_store.show()
