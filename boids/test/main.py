from dog import Dog
from cat import Cat
def main():
    # Create instances of the Dog and Cat classes
    my_dog = Dog("Buddy", "Golden Retriever")
    my_cat = Cat("Whiskers", "Gray")

    # Call the speak method of each instance
    my_dog.speak()
    my_cat.speak()

if __name__ == "__main__":
    main()