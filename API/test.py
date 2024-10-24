
class Tamere:
    def __init__(self,x = "AAAAA"):
        self.x = x

        print("should be",self.x)
    def __str__(self):
        return self.x
def fonction(x):
    x.x = str(x.x)+'test'
x= Tamere()
print(x)
fonction(x)
print(x)