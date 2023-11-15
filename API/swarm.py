from typing import Union

from fastapi import FastAPI
import math
import time
import json 
import cflib.crtp
from cflib.crazyflie import Crazyflie, syncCrazyflie
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
uris = ["radio://0/80/2M/E7E7E7E701", "radio://0/27/2M/E7E7E7E702", "radio://0/28/2M/E7E7E7E703"]

cflib.crtp.init_drivers(enable_debug_driver=False)

@app.get("/")
async def read_root():
    logger = Logger("log.txt")

    logger.info("API is UP")

    return {"message": "Welcome to the Drone Control API"}


@app.get("/getavailableURIS/")
def getavailableURIS():
        # Initialize the drivers
    global activeuris
    activeuris = []
    # Communicate with each drone using its URI
    for uri in uris:
        t=datetime.now()
        try:
            with syncCrazyflie.SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
                
                activeuris.append(uri)
                logger.info(f"{getavailabledrones.__name__} | {activeuris}")

        except Exception as e:
            logger.warning(f"{getavailabledrones.__name__} | Failed to connect to {uri} due to {e}")
    return activeuris

@app.get("/ActivateAvailableDrones/")
def ActivateAvailableDrones():
    global activeuris
    global activedrones
    # Communicate with each drone using its URI
    logger.info(f"scf opening links with {activeuris}")
    for uri in activeuris:
        t=datetime.now()
        logger.info(f"scf opening link with {uri}")

        try:
            scf = Crazyflie(rw_cache='./cache', link=uri)
            logger.info(f"scf opened link with {uri}")
            
            scf.open_link(uri)
            logger.info(f"scf opened link with {uri}")
            activedrones.append(scf)
        except Exception as e:
            logger.warning(f"Failed to connect to {uri} due to {e}")
            return False
    return activedrones

@app.get("/getavaillabledronespositions")
def getavaillabledronespositions():
        # Initialize the drivers
    # Communicate with each drone using its URI
    for uri in activeuris:
        t=datetime.now()
        logger.info(f"availabale drone Pos {uri}")
        try:
            with syncCrazyflie.SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
                return logpos(scf)
        except Exception as e:
            logger.warning(f"Failed to connect to {uri} due to {e}")
    return None

def logpos(cf):
    current_position = cf.param.get_value('kalman.stateX')  # Assuming 'kalman.stateX' represents the position
    logger.info(f"current_position of {uri}:// {current_position}")
    return current_position

def handle_move_drone(moveto, uri):
    move = Move(moveto)
    try:
        with syncCrazyflie.SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
            with Driver(scf) as drone:
                drone.move_distance(
                    move.distance_x_m,
                    move.distance_y_m,
                    move.distance_z_m,
                    velocity=move.velocity,
                )
        return 1
    except Exception as e:
        return -1

@app.post("/move_drone/{uri}/{moveto}")
async def move_drone_endpoint(moveto: str, uri: str):
    thread = threading.Thread(target=handle_move_drone, args=(moveto, uri))
    thread.start()
    return "Thread started successfully."

@app.post("/move_drones/{uris}/{movetos}")
async def move_drones_endpoint(uriss: str, movetoss: str):
    threads = []
    movetos = movetoss.split(";")

    uris = uriss.split(",")
    logger.info(f"{uris}  {movetos}")

    for moveto, uri in zip(movetos, uris):
        thread = threading.Thread(target=handle_move_drone, args=(moveto, uri))
        threads.append(thread)
        thread.start()
    return "Threads started successfully for all drones."


@app.post("/land_drones/{uris}")
async def land_drones_endpoint(uriss: str, movetoss: str):
    threads = []
    movetos = movetoss.split(";")
    uris = uriss.split(",")
    for moveto, uri in zip(movetos, uris):
        thread = threading.Thread(target=land_drone, args=uri)
        threads.append(thread)
        thread.start()
    return "Threads started successfully for all drones."

@app.post("/land_dronesALT/{uris}")
async def land_drones_endpoint(uriss: str, movetoss: str):
    threads = []
    movetos = movetoss.split(";")
    uris = uriss.split(",")
    for moveto, uri in zip(movetos, uris):
        thread = threading.Thread(target=land_droneALT, args=uri)
        threads.append(thread)
        thread.start()
    return "Threads started successfully for all drones."


def land_drone(uri):
    try:
        with syncCrazyflie.SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
            with Driver(scf) as drone:
                drone.land()
        return 1
    except Exception as e:
        return -1
def land_droneALT(uri):
    cf.commander.send_stop_setpoint()
    # Hand control over to the high level commander to avoid timeout and locking of the Crazyflie
    cf.commander.send_notify_setpoint_stop()

def poshold(cf, t, x, y, z):
    steps = t * 10

    for r in range(steps):
        cf.commander.send_position_setpoint(x, y, 0, z)
        time.sleep(0.1)


def run_sequence(scf, positions):
    cf = scf.cf

    # Number of setpoints sent per second
    fs = 4
    fsi = 1.0 / fs

    for pos in positions:
        x, y, z = pos
        poshold(cf, 2, x, y, z)

    cf.commander.send_stop_setpoint()
    # Hand control over to the high level commander to avoid timeout and locking of the Crazyflie
    cf.commander.send_notify_setpoint_stop()