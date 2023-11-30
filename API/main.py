from API.swarmcontrol import SwarmControl
from API.Logger import Logger
from fastapi import FastAPI
app = FastAPI()
logger = Logger("log.txt",False)
swarm = SwarmControl

@app.get("/")
async def read_root():

    logger.info("API is UP")
    return {"message": "Welcome to the Drone Control API"}

@app.get("/OpenLinks/")
async def OpenLinks():
    return swarm.OpenLinks()

@app.get("/CloseLinks/")
async def CloseLinks():
    return swarm.CloseLinks()

@app.get("/takeoff/")
async def Take_off():
    return swarm.All_TakeOff()

@app.get("/land/")
async def Land():
    return swarm.All_Land()

@app.get("/getestimatedpositions/")
async def GetEstimatedPositions():
    return swarm.All_GetEstimatedPositions()






