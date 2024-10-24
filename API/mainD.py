from fastapi.middleware.cors import CORSMiddleware
from threading import Thread, Lock


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

    print("found",path)
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
s = SwarmControl()
s.OpenLinks()
@app.get("/HelloWorld/")
async def read_root():
    global s
    s = SwarmControl()

    logger.info("root")
    return {"message": "Welcome to the Drone Control API"}

@app.get("/OpenLinks/")
async def OpenLinks():
    global s
    logger.info("OpenLinks")
    return s.OpenLinks()
    
@app.get("/CloseLinks/")
async def CloseLinks():
    global s

    logger.info("CloseLinks")
    return s.CloseLinks()

@app.get("/All_TakeOff/")
async def TakeOff():
    global s
    print(s.DRONES)
    logger.info("takeoff")
    return s.All_TakeOff()

@app.get("/All_Land/")
async def AllLand():
    return s.All_Land()

@app.get("/getestimatedpositions/")
async def GetEstimatedPositions(boule: bool = False):
    global s
    # return s.All_GetEstimatedPositions()
    return s.altAll_GetEstimatedPositions() if boule else s.All_GetEstimatedPositions()
    # default the new GetEstimatedPositions to the old one for now later to be deprecated
@app.get("/altgetestimatedpositions/")
async def AltGetEstimatedPositions():
    global s

    return s.altAll_GetEstimatedPositions()

@app.post("/All_StartLinearMotion/")
async def AllSetSpeed(args_arr: List[Velocity] ): #: OutputDict(List[Velocity],"Drones")
    return s.All_StartLinearMotion(args_arr)

@app.post("/All_MoveDistance/")
async def All_MoveDistance(args_arr : List[Move]):
    global s

    logger.info(f"MoveDistance {args_arr}")
    return s.All_MoveDistance(args_arr)

def main(host="0.0.0.0", port=8000):
    uvicorn.run("mainD:app", host=host, port=port, workers=1, limit_concurrency=5000)