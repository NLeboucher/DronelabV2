from fastapi.middleware.cors import CORSMiddleware


from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os, sys
import uvicorn
path = os.getcwd()
folders = path.split("/")
if("DronelabV2" in folders):
    path = "/".join(folders[:folders.index("DronelabV2")+1])
    sys.path.insert(0, path)

    print(path)
    from API.logger import Logger
    from API.move import Move, Velocity
    from API.outputdict import OutputDict
    from API.swarmcontrol import SwarmControl
else:
    Exception("Executed from Wrong folder, you need to be in DronelabV2")


app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)
logger = Logger("logD.txt",True)
swarm = SwarmControl
swarm.OpenLinks()
@app.get("/HelloWorld/")
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
async def AllSetSpeed(args_arr: List[Velocity] ): #: OutputDict(List[Velocity],"Drones")
    return swarm.All_StartLinearMotion(args_arr)

@app.post("/All_MoveDistance/")
async def All_MoveDistance(args_arr : List[Move]):
    logger.info(f"MoveDistance {args_arr}")
    return swarm.All_MoveDistance(args_arr)

def main(host="0.0.0.0", port=8000):
    uvicorn.run("mainD:app", host=host, port=port)