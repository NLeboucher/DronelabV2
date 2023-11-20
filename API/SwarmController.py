from fastapi import FastAPI

import math
import time
import json 
import cflib
from cflib.crazyflie import Crazyflie, syncCrazyflie
from cflib.crazyflie.swarm import Swarm
from datetime import datetime
from API.Logger import Logger
from API.Move import Move
from API.outputdict import OutputDict
from API.enums.option import Option   
from API.Param import ParamExample
from cflib.positioning.motion_commander import MotionCommander as Driver
from cflib.positioning.position_hl_commander import PositionHlCommander as PositionHlCommander
from cflib.crazyflie.param import Param
from cflib.crazyflie.localization import Localization
from API.quad import Quad
import threading
from typing import List

app = FastAPI()

logger = Logger("log.txt")
activequads = []
default_height = 0.3
# Add the appropriate URI(s) of the drone(s) you want to communicate with
uris = "radio://0/80/2M/E7E7E7E701;radio://0/27/2M/E7E7E7E702;radio://0/28/2M/E7E7E7E703"
cflib.crtp.init_drivers(enable_debug_driver=False)
Crazyswarm = Swarm(uris=uris.split(";"))
@app.get("/")
async def read_root():

    logger.info("API is UP")
    return {"message": "Welcome to the Drone Control API"}


@app.get("/getAvailableURIS/")
def getavailableURIS():
        # Initialize the drivers
    logger.info(f"{getavailableURIS.__name__} START")

    Parallelize(getavailableuri)
    logger.info(f"{getavailableURIS.__name__} | Quad : {Quad.quads}")

    ret = [a.id for a in Quad.quads]
    logger.info(f"{getavailableURIS.__name__} | Quads : {ret}")
    logger.info(f"{getavailableURIS.__name__} STOP")
    return  OutputDict(ret,"URIS").dict

def getavailableuri(scf):
    logger.info(f"{getavailableuri.__name__} START")
    try:
        #scf.open_link()
        if(scf.is_link_open()):
            logger.info(f"{getavailableuri.__name__} connected to {scf._link_uri}")
            scf.close_link()
            logger.info(f"{getavailableuri.__name__} stopped connection to {scf._link_uri}")
    
            temp = Quad(str(scf._link_uri),False)

            logger.info(f"{getavailableuri.__name__} | temp created")
            logger.info(f"{getavailableuri.__name__} | {Quad.quads}")
        else:
            logger.info(f"{getavailableuri.__name__} |  {scf._link_uri} | {False}")
        

    except Exception as e:
        logger.warning(f"{getavailableuri.__name__} | Exception on {scf._link_uri} due to {e} ")


def SpeedLinearMotion(uri: str, speedx: float,speedy: float,speedz: float, rate_yaw = 0.0):
    t=datetime.now()
    logger.info(f"{SpeedMove.__name__} | {uri} | {speed}")
    try:
        with syncCrazyflie.SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
            with Driver(scf, default_height=default_height) as driver:
                driver.start_linear_motion(speedx, speedy, speedz,rate_yaw)
                time.sleep(1)
                driver.stop()
                logger.info(f"{SpeedMove.__name__} | {uri} | {speed}")

    except Exception as e:
        logger.warning(f"{SpeedMove.__name__} | Failed to connect to {uri} due to {e}")


def SpeedMoveToRelativePoint(uri: str, x: float, y: float, z: float, speed:float):
    t=datetime.now()
    logger.info(f"{SpeedMoveToPoint.__name__} | {uri} | {speed}")
    try:
        with syncCrazyflie.SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
            with Driver(scf, default_height=default_height) as driver:
                driver.move_distance(x, y, z, velocity=speed)
                time.sleep(1)
                driver.stop()
                logger.info(f"{SpeedMoveToRelativePoint.__name__} | {uri} | {speed}")

    except Exception as e:
        logger.warning(f"{SpeedMoveToPoint.__name__} | Failed to connect to {uri} due to {e}")
def SpeedMoveToAbsolutePoint(uri: str,speed:float, x: float,y: float,z: float):
    t=datetime.now()
    logger.info(f"{SpeedMoveToPoint.__name__} | {uri} | {speed}")
    try:
        with syncCrazyflie.SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
            with PositionHlCommander(scf, default_height=default_height) as driver:
                driver.go_to(x, y, z, velocity=speed)
                logger.info(f"{SpeedMoveToAbsolutePoint.__name__} | {uri} | {speed} | {x}, {y}, {z}")

    except Exception as e:
        logger.warning(f"{SpeedMoveToPoint.__name__} | Failed to connect to {uri} due to {e}")


# TODO 
def SendEmergencyStop(uri: str):
    cf = Crazyflie()
    cf.open_link(uri)
    localization = Localization(cf)
    localization.send_emergency_stop()
    cf.close_link()



def Parallelize(func,arguments:dict = {}):
    global uris
    global Crazyswarm
    logger.info(Quad.activeURIS)
    if(Quad.activeURIS!=[]):
        Crazyswarm.parallel_safe(func = func,args_dict=arguments)
    else:
        logger.info(f"Parallelize looking for URIS : {uris}")
        Crazyswarm.reset_estimators()
        Crazyswarm.parallel_safe(func = getavailableuri,args_dict=arguments)


def _RightURIs(uri:str):
    u = uri.split(";")
    return[_RightURI(us) for us in u if us in Quad.quads]
    return None

def _RightURI(uri:str):
    for a in Quad.quads:
        if a.uri[len(a.uri)-1] == uri:
            return a
    return None

@app.get("/takoffAllDrones/")
def takoffAllDrones():
        # Initialize the drivers
    logger.info(f"{takoffAllDrones.__name__} START")
    Parallelize(takeoff)
    logger.info(f"{takoffAllDrones.__name__} STOP")
    return Quad.quads

def takeoff(scf):
    scf.open_link()
    driver = Driver(scf.cf, default_height=default_height)
    logger.info(f"{takeoff.__name__} | driver started for {scf._link_uri}")

    logger.info(f"{takeoff.__name__} | {scf._link_uri} | {driver}")
    driver.take_off()

@app.get("/landAllDrones/")
def landAllDrones():
        # Initialize the drivers
    logger.info(f"{landAllDrones.__name__} START")
    Parallelize(land)
    logger.info(f"{landAllDrones.__name__} STOP")
    return Quad.quads

def land(scf):
    scf.open_link()
    driver = Driver(scf.cf, default_height=default_height)
    logger.info(f"{land.__name__} | driver started for {scf._link_uri}")

    logger.info(f"{land.__name__} | {scf._link_uri} | {driver}")
    driver.land()
    scf.close_link()


@app.get("/getFullPositions/")
def GetFullPositions():
    Parallelize(GetFullPosition)
    ret = [a.position for a in Quad.quads]
    logger.info(f"{GetFullPositions.__name__} | {ret}")
    logger.info(f"{GetFullPositions.__name__} STOP")
    return  OutputDict(ret,"Positions").dict
@app.get("/getXYZPositions/")
def GetXYZPositions():
    Parallelize(GetPosition)
    return [q.position for q in Quad.quads]

def GetPosition(scf):
    scf.open_link()
    driver = PositionHlCommander(scf.cf, default_height=default_height)
    q = Quad.quads[Quad.activeURIS.index(scf._link_uri)]
    q.position = driver.get_position()
    logger.info(f"{GetPosition.__name__} | {scf._link_uri} | {q.position}")
    return q.position

def GetPositionCallback(name, value):
    logger.info(f"{GetPositionCallback.__name__} | {name} | {value}")
    

    # scf.open_link()
    # with PositionHlCommander(scf, default_height=default_height) as driver:
    #     q = Quad.quads[Quad.activeURIS.index(scf._link_uri)]
    #     q.position = driver.get_position()
    #     logger.info(f"{SpeedMoveToAbsolutePoint.__name__} | {scf._link_uri} | {q.position}")
    #     return q.position




def GetFullPosition(scf,quarternion :Option = Option.intermediate):
    scf.open_link()
        # Assuming the parameter names for x, y, z, roll, pitch, and yaw

    match quarternion:
        case Option.full:
            parameter_names = ['stateEstimate.x', 'stateEstimate.y', 'stateEstimate.z',
                        'stateEstimate.roll', 'stateEstimate.pitch', 'stateEstimate.yaw',
                        'stateEstimate.qx', 'stateEstimate.qy', 'stateEstimate.qz', 'stateEstimate.qw',
                        'stateEstimate.x', 'stateEstimate.y', 'stateEstimate.z',]
        case Option.intermediate:
            parameter_names = ['kalman.stateX', 'kalman.stateY', 'kalman.stateZ',
                        'kalman.q0', 'kalman.q1', 'kalman.q2', 'kalman.q3']
        case Option.short:
            parameter_names = ['kalman.stateX', 'kalman.stateY', 'kalman.stateZ']
        case Option.none:
            parameter_names = ['kalman.stateX', 'kalman.stateY', 'kalman.stateZ',
                        'stabilizer.roll', 'stabilizer.pitch', 'stabilizer.yaw',
                        'kalman.q0', 'kalman.q1', 'kalman.q2', 'kalman.q3']

    # Log the parameters
    logger.info(f"{GetFullPosition.__name__} | {scf._link_uri} | {parameter_names}")


    pe = ParamExample(scf._link_uri)

    # The Crazyflie lib doesn't contain anything to keep the application
    # alive, so this is where your application should do something. In our
    # case we are just waiting until we are disconnected.
    while pe.is_connected:
        time.sleep(1)


    # Retrieve values for each parameter
    
    #stabilizer.roll 	  	LOG_FLOAT 	Estimated roll Note: Same as stateEstimate.roll.
    #stabilizer.pitch 	  	LOG_FLOAT 	Estimated pitch Note: Same as stateEstimate.pitch.
    #stabilizer.yaw 	  	LOG_FLOAT 	Estimated yaw Note: same as stateEstimate.yaw.
    #kalman.stateX 	  	LOG_FLOAT 	State position in the global frame x.
    #kalman.stateY 	  	LOG_FLOAT 	State position in the global frame y.
    #kalman.stateZ 	  	LOG_FLOAT 	State position in the global frame z.
    #kalman.q0 	  	LOG_FLOAT 	Estimated Attitude quarternion w.
    #kalman.q1 	  	LOG_FLOAT 	Estimated Attitude quarternion x.
    #kalman.q2 	  	LOG_FLOAT 	Estimated Attitude quarternion y.
    #kalman.q3 	  	LOG_FLOAT 	Estimated Attitude quarternion z.
    #Display the position array
    #stateEstimate.vx 	Core 	LOG_FLOAT 	The velocity of the Crazyflie in the global reference frame, X [m/s].
    #stateEstimate.vy 	Core 	LOG_FLOAT 	The velocity of the Crazyflie in the global reference frame, Y [m/s].
    #stateEstimate.vz 	Core 	LOG_FLOAT 	The velocity of the Crazyflie in the global reference frame, Z [m/s].
    '''.git/
    stateEstimate.x 	Core 	LOG_FLOAT 	The estimated position of the platform in the global reference frame, X [m].
    stateEstimate.y 	Core 	LOG_FLOAT 	The estimated position of the platform in the global reference frame, Y [m].
    stateEstimate.z 	Core 	LOG_FLOAT 	The estimated position of the platform in the global reference frame, Z [m].
    stateEstimate.vx 	Core 	LOG_FLOAT 	The velocity of the Crazyflie in the global reference frame, X [m/s].
    stateEstimate.vy 	Core 	LOG_FLOAT 	The velocity of the Crazyflie in the global reference frame, Y [m/s].
    stateEstimate.vz 	Core 	LOG_FLOAT 	The velocity of the Crazyflie in the global reference frame, Z [m/s].
    stateEstimate.ax 	Core 	LOG_FLOAT 	The acceleration of the Crazyflie in the global reference frame, X [Gs].
    stateEstimate.ay 	Core 	LOG_FLOAT 	The acceleration of the Crazyflie in the global reference frame, Y [Gs].
    stateEstimate.az 	Core 	LOG_FLOAT 	The acceleration of the Crazyflie in the global reference frame, without considering gravity, Z [Gs].
    stateEstimate.roll 	Core 	LOG_FLOAT 	Attitude, roll angle [deg].
    stateEstimate.pitch 	Core 	LOG_FLOAT 	Attitude, pitch angle (legacy CF2 body coordinate system, where pitch is inverted) [deg].
    stateEstimate.yaw 	Core 	LOG_FLOAT 	Attitude, yaw angle [deg].
    stateEstimate.qx 	Core 	LOG_FLOAT 	Attitude as a quaternion, x.
    stateEstimate.qy 	Core 	LOG_FLOAT 	Attitude as a quaternion, y.
    stateEstimate.qz 	Core 	LOG_FLOAT 	Attitude as a quaternion, z.
    stateEstimate.qw 	Core 	LOG_FLOAT 	Attitude as a quaternion, w.
    '''
