from API.swarmcontrol import SwarmControl
from API.logger import Logger
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os
path = os.getcwd()
path = path.split("/")[::-1][0]
print(path)
if(path == "API"):
    from logger import Logger
    from move import Move
else:
    from API.logger import Logger
    from API.move import Move
app = FastAPI()
logger = Logger("log.txt",False)
swarm = SwarmControl

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.get("/")
async def read_root():
    s = SwarmControl()
    logger.info("root")
    return {"message": "Welcome to the Drone Control API"}

    
@app.post("/items/")
async def create_item(item: Item):
    return item

@app.get("/OpenLinks/")
async def OpenLinks():
    logger.info("OpenLinks")
    return swarm.OpenLinks()

@app.get("/CloseLinks/")
async def CloseLinks():
    logger.info("CloseLinks")
    return swarm.CloseLinks()

@app.get("/takeoff/")
async def Take_off():
    logger.info("takeoff")
    return swarm.All_TakeOff()

@app.get("/land/")
async def Land():
    return swarm.All_Land()

@app.get("/getestimatedpositions/")
async def GetEstimatedPositions():
    return swarm.All_GetEstimatedPositions()
a = Move(radio="radio://0/28/2M/E7E7E7E703",x=0,y=0,z=0,yaw_rate=0,velocity=0)
@app.post("/All_StartLinearMotion/")
async def All_StartLinearMotion(args_arr : List[Move]):
    return swarm.All_StartLinearMotion(args_arr)

@app.post("/All_MoveDistance/")
async def All_MoveDistance(args_arr : List[Move]):
    return swarm.All_MoveDistance(args_arr)


