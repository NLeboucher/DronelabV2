from animal import Animal
class Dog(Animal):
    def __init__(self, name, breed):
        # Using super to call the constructor of the parent class (Animal)
        super().__init__(name)
        self.breed = breed

    def speak(self):
        # Using super to call the speak method of the parent class (Animal)
        super().speak()
        print(f"{self.name} barks")