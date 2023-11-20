from API.Logger import Logger
logger = Logger("log.txt")

class Quad:
    quads = []
    activeURIS = []
    def __init__(self,uri:str,flying=False):
        logger.info(f"Quad {uri} creating with id {uri[len(uri)-1:]}")
        self.flying = flying
        self.uri = uri
        self.id = uri[len(uri)-1:]
        logger.info(f"Went to here")
        self.quads.append(self)
        self.activeURIS.append(uri)
        #self.quads.append(self.id)
        logger.info(f"Quad {self.uri} created")
        self.position = []
        self.speed = []

    