from animal import Animal
class Cat(Animal):
    def __init__(self, name, color):
        # Using super to call the constructor of the parent class (Animal)
        super().__init__(name)
        self.color = color

    def speak(self):
        # Using super to call the speak method of the parent class (Animal)
        super().speak()
        print(f"{self.name} meows")