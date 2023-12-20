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
    from move import Move, Velocity
else:
    from API.logger import Logger
    from API.move import Move, Velocity
app = FastAPI()
logger = Logger("log.txt",False)
swarm = SwarmControl

@app.get("/")
async def read_root():
    s = SwarmControl()
    logger.info("root")
    return {"message": "Welcome to the Drone Control API"}

@app.get("/OpenLinks/")
async def OpenLinks():
    logger.info("OpenLinks")
    return swarm.OpenLinks()

@app.get("/CloseLinks/")
async def CloseLinks():
    logger.info("CloseLinks")
    return swarm.CloseLinks()

@app.get("/All_TakeOff/")
async def TakeOff():
    logger.info("takeoff")
    return swarm.All_TakeOff()

@app.get("/All_Land/")
async def AllLand():
    return swarm.All_Land()

@app.get("/getestimatedpositions/")
async def GetEstimatedPositions():
    return swarm.All_GetEstimatedPositions()

@app.post("/All_StartLinearMotion/")
async def AllSetSpeed(args_arr : List[Velocity]):
    return swarm.All_StartLinearMotion(args_arr)

@app.post("/All_MoveDistance/")
async def All_MoveDistance(args_arr : List[Move]):
    return swarm.All_MoveDistance(args_arr)


