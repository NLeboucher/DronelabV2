from typing import Union

from fastapi import FastAPI
import math
import time
import json 
import cflib.crtp
from cflib.crazyflie import Crazyflie, syncCrazyflie
from datetime import datetime
from Logger import Logger
from Move import Move
from cflib.positioning.motion_commander import MotionCommander as Driver
import threading
from typing import List
app = FastAPI()


#python -m uvicorn swarm:app --host 0.0.0.0 --port 8000

activeuris = []

logger = Logger("log.txt")
# Add the appropriate URI(s) of the drone(s) you want to communicate with
uris = ["radio://0/80/2M/E7E7E7E701", "radio://0/27/2M/E7E7E7E702", "radio://0/28/2M/E7E7E7E703"]
activeuris = []

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Drone Control API"}


@app.get("/items/")
def getavailabledrones():
        # Initialize the drivers
    cflib.crtp.init_drivers(enable_debug_driver=False)
    activeuris = []
    # Communicate with each drone using its URI
    for uri in uris:
        t=datetime.now()
        try:
            with syncCrazyflie.SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
                
                activeuris.append(uri)
        except Exception as e:
            logger.warning(f"Failed to connect to {uri} due to {e}")
    return activeuris

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
    for moveto, uri in zip(movetos, uris):
        thread = threading.Thread(target=handle_move_drone, args=(moveto, uri))
        threads.append(thread)
        thread.start()
    return "Threads started successfully for all drones."

@app.get("/OpenLinks/")
async def open_links():
    # Vous pouvez personnaliser la liste des URIs ici selon vos besoins
    uris_list = ["IP1"]
    return {"URIS": uris_list}

@app.get("/getposition/")
async def get_position():
    # Remplacez ceci par la logique réelle pour récupérer les positions des drones
    # Ici, je vais retourner un exemple de données statiques
    exemple_positions = {
        "IP1": {"X": "1.0", "Y": "2.0", "Z": "3.0", "yaw": "45.0"}
        
    }
    return {"position": exemple_positions}

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