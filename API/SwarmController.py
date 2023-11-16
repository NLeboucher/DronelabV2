from typing import Union

from fastapi import FastAPI
import math
import time
import json 
import cflib.crtp
from cflib.crazyflie import Crazyflie, syncCrazyflie
from cflib.crazyflie.swarm import Swarm
from datetime import datetime
from API.Logger import Logger
from API.Move import Move
from cflib.positioning.motion_commander import MotionCommander as Driver
import threading
from typing import List
app = FastAPI()

logger = Logger("log.txt")
activeuris = []
activedrones = []
# Add the appropriate URI(s) of the drone(s) you want to communicate with
uris = "radio://0/80/2M/E7E7E7E701;radio://0/27/2M/E7E7E7E702;radio://0/28/2M/E7E7E7E703"
arguments = {"radio://0/80/2M/E7E7E7E701":"radio://0/80/2M/E7E7E7E701", "radio://0/27/2M/E7E7E7E702":"radio://0/27/2M/E7E7E7E702", "radio://0/28/2M/E7E7E7E703":"radio://0/28/2M/E7E7E7E703"}
cflib.crtp.init_drivers(enable_debug_driver=False)
def UpdateConnection(uri: str):
    global activeuris
    global activedrones
    t=datetime.now()
    logger.info(f"{UpdateConnection.__name__}")
    try:
        with syncCrazyflie.SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
            
            activeuris.append(uri)
            logger.info(f"{UpdateConnection.__name__} | {activeuris}")

    except Exception as e:
        logger.warning(f"{UpdateConnection.__name__} | Failed to connect to {uri} due to {e}")


def Parallelize(func,args :str):
    global activeuris
    global arguments
    Crazyswarm = Swarm(uris=args.split(";"))
    Crazyswarm.parallel_safe(UpdateConnection,args_dict=arguments)
@app.get("/")
async def read_root():
    logger = Logger("log.txt")

    logger.info("API is UP")

    return {"message": "Welcome to the Drone Control API"}


@app.get("/getAvailableURIS/")
def getavailableURIS():
        # Initialize the drivers
    global activeuris
    Parallelize(UpdateConnection,uris)
    return activeuris


@app.get("/takoffAllDrones/")
def takoffAllDrones():
        # Initialize the drivers
    global activeuris
    UpdateConnections()
    return activeuris

@app.get("/moveAllDrones/")
def moveAllDrones():
        # Initialize the drivers
    global activeuris
    UpdateConnections()
    return activeuris