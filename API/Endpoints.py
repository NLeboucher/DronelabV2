
from fastapi import FastAPI
import math
import time
import json 
import cflib.crtp as crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm

app = FastAPI()
URI1 = "radio://0/80/2M/E7E7E7E701"
URI2 = "radio://0/27/2M/E7E7E7E702"
URI3 = "radio://0/28/2M/E7E7E7E703"
drones={}

@app.get("/") #Root of the API. Used to know if alive
async def root():
    return {"message": "API Running"}

@app.get("/ack") #Used to know if API started properly
async def get_ack():
    #drawGUI()
    print(term.move_y(10 + len(robots)) + term.clear_eol + "Requested ACK")
    return "API ACK"
@app.get("/getDrones")
async def get_drones():

    return robots
@app.post("/move_drone/{uri}/{moveto}")
async def move_drone(moveto: str, uri: str):
    move=Move(moveto)
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