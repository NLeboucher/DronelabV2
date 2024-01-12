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
    # Liste étendue des URIs de drones fictifs
    uris_list = ["IP1", "IP2", "IP3", "IP4"]
    return {"URIS": uris_list}

import time
@app.get("/getestimatedpositions/")
async def get_position():
    # Temps écoulé en secondes
    elapsed_time = time.time() % 60  # Utilisez % 60 pour créer une boucle toutes les 60 secondes

    # Simuler différents comportements de déplacement
    # Drone 1 : Mouvement en cercle
    x1 = 5 + math.cos(elapsed_time) * 2
    y1 = 5 + math.sin(elapsed_time) * 2
    z1 = 3
    yaw1 = elapsed_time * 6  # Rotation continue

    # Drone 2 : Mouvement en ligne droite avec boucle
    x2 = 4 + (elapsed_time % 10)  # Boucle toutes les 10 secondes
    y2 = 6
    z2 = 2
    yaw2 = 30

    # Drone 3 : Mouvement vertical
    x3 = 7.2
    y3 = 3.1
    z3 = 3 + math.sin(elapsed_time)  # Oscillation verticale
    yaw3 = 90

    # Drone 4 : Mouvement descendant et ascendant
    x4 = 2.5
    y4 = 1.0
    z4 = 5 - (elapsed_time % 5)  # Descend et remonte toutes les 5 secondes
    yaw4 = 60
# Dictionnaire avec des positions mises à jour sous forme de listes [X, Y, Z]
    exemple_positions = {
        "IP1": [(x1), (y1), (z1)],
        "IP2": [(x2), (y2), (z2)],
        "IP3": [(x3), (y3), (z3)],
        "IP4": [(x4), (y4), (z4)]
    }

    return {"Positions": exemple_positions}

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