import os
path = os.getcwd()
path = path.split("/")[::-1][0]
print(path)
if(path == "API"):
    from logger import Logger
else:
    from API.logger import Logger
logger = Logger("log.txt")

class Room():
    range_x = [0,0]
    range_y = [0,0]
    range_z = [0,0]
    def __init__(self,range_x,range_y,range_z,name="Room"):
        self.range_x = range_x
        self.range_y = range_y
        self.range_z = range_z
        self.name = name
        logger.info(f"Room ({name}): created with ranges {range_x} {range_y} {range_z}")
        