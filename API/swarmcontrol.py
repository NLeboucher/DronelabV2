import time

import cflib.crtp
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.positioning.motion_commander import MotionCommander
from cflib.positioning.position_hl_commander import PositionHlCommander
from typing import List
import os
path = os.getcwd()
path = path.split("/")[::-1][0]
print(path)
if(path == "API"):
    from logger import Logger
    from move import Move
    from outputdict import OutputDict
    from enums.option import Option   
    from quad import Quad
    from swarm import Swarm
else:
    from API.logger import Logger
    from API.move import Move
    from API.outputdict import OutputDict
    from API.enums.option import Option   
    from API.quad import Quad 
    from API.swarm import Swarm
from typing import List

debug = True
logger = Logger("log.txt",debug)
#
URIS = {
    'radio://0/28/2M/E7E7E7E703',
    'radio://0/80/2M/E7E7E7E701',
    'radio://0/27/2M/E7E7E7E702',
    'radio://0/29/2M/E7E7E7E704',
    # Add more URIs if you want more copters in the swarm
}
DRONES = []
SWARM = None
factory = None
commander = None
DefaultZSpeed = 0.2
DefaultHeight = 0.3
positions = dict()
class SwarmControl:

    def __init__(self, default_height=0.3, default_z_speed=0.2):
        DRONES = []
        SWARM = None
        factory = None
        commander = None
        DefaultZSpeed = default_height
        DefaultHeight = default_z_speed
        positions = dict()
    def OpenLinks():
        global SWARM, URIS, factory, DRONES
        DRONES = []
        cflib.crtp.init_drivers()
        factory = CachedCfFactory(ro_cache='./cache',rw_cache='./cache')
        logger.info(f"{URIS}")
        SWARM = Swarm(URIS, factory)
        try:
            SWARM.open_links()

        except Exception as e:
            logger.warning(f"tried open_links connection to swarm {URIS} but:{e}")
        redo =False
        for drone in SWARM._cfs.keys():
            if(SWARM._cfs[drone].is_link_open()):
                logger.info(f"Connected to {drone}")
            else:
                redo = True
                logger.info(f"Failed to connect to {drone}")
                URIS.remove(drone)
        if(redo):
            SWARM.close_links()
            SWARM = Swarm(URIS, factory)
            SWARM.open_links()
        DRONES = [ d  for d in SWARM._cfs.keys() if SWARM._cfs[d]]
        logger.info(f"{DRONES}")
        return OutputDict(DRONES,"URIS").dict

    def CloseLinks():
        #cflib.crtp.init_drivers()
        #factory = CachedCfFactory(ro_cache='./cache',rw_cache='./cache')
        #SWARM = Swarm(URIS, factory)
        global SWARM
        try:
            SWARM.close_links()

        except Exception as e:
            logger.warning(f"tried close_links connection to swarm {URIS} but:{e}")

        logger.info(f"{SWARM._cfs.keys()}")
        for drone in SWARM._cfs.keys():
            if(SWARM._cfs[drone].is_link_open()):
                logger.info(f"Still Connected to {drone}")
            else:
                logger.info(f"Disconnected to {drone}")
        DRONES = [ d for d in SWARM._cfs.keys() if SWARM._cfs[d].is_link_open()]
        return OutputDict(DRONES,"URIS").dict

    def Get_All_Drones():
        global DRONES, URIS, factory, SWARM
        return OutputDict(DRONES,"URIS").dict

    def All_Land():
        logger.info(f"Land START")
        logger.info(DRONES)
        if(SWARM._is_open):
            # SWARM = Swarm(uris=Quad.activeURIS,factory=factory)

            # SWARM.open_links()
            SWARM.parallel(SwarmControl.Land)
            # SWARM.close_links()
            logger.info(f"Land STOP")
        return [OutputDict(True,"OK").dict for d in DRONES]
    def Land(scf):
        global commander, DefaultZSpeed
        # commander = PositionHlCommander(crazyflie=scf,default_height=DefaultHeight,controller=PositionHlCommander.CONTROLLER_MELLINGER)
        #commander = MotionCommander(scf,default_height=DefaultHeight)
        commander.land(DefaultZSpeed)

    def All_TakeOff():
        logger.info(f"TakeOff START")
        logger.info(DRONES)
        if(SWARM._is_open):
            # SWARM = Swarm(uris=Quad.activeURIS,factory=factory)

            # SWARM.open_links()
            SWARM.parallel(SwarmControl.Take_off)
            logger.info(f"TakeOff STOP")
        return OutputDict(True,"OK").dict
            # SWARM.close_links()
    def Take_off(scf):
        global commander
        # commander = PositionHlCommander(crazyflie=scf,default_height=DefaultHeight,controller=PositionHlCommander.CONTROLLER_MELLINGER)
        commander = MotionCommander(scf,default_height=DefaultHeight)
        commander.take_off(height=DefaultHeight,velocity=DefaultZSpeed)

    def All_GetEstimatedPositions():
        global DRONES, URIS, factory, SWARM
        logger.info(f"GetEstimatedPosition START")
        logger.info(DRONES)
        if(SWARM._is_open):
            # SWARM = Swarm(uris=Quad.activeURIS,factory=factory)
            # SWARM.open_links()
            positions = SWARM.get_estimated_positions()
            logger.info(f"GetEstimatedPosition STOP")
            # SWARM.close_links()
        return OutputDict(positions,"Positions").dict
    # def All_GetPositions():
    #     global DRONES, URIS, factory, SWARM
    #     logger.info(f"GetEstimatedPosition START")
    #     logger.info(DRONES)
    #     if(SWARM._is_open):
    #         # SWARM = Swarm(uris=Quad.activeURIS,factory=factory)
    #         # SWARM.open_links()
    #         positions = SWARM.get_estimated_positions()
    #         logger.info(f"GetEstimatedPosition STOP")
    #         # SWARM.close_links()
    #     return OutputDict(positions,"Positions").dict

    # def GetEstimatedPosition(scf):
    #     global DRONES
    #     positions[scf._link_uri] = DRONES[scf._link_uri].get_position()

    # def GetPosition(scf):
    #     commander = PositionHlCommander(crazyflie=scf,default_height=DefaultHeight,controller=PositionHlCommander.CONTROLLER_MELLINGER)
    #     positions[scf._link_uri] = commander.get_position()
    #     return OutputDict(positions,"OK").dict
    
    def All_StartLinearMotion(args_arr : List[Move]):
        global DRONES, URIS, factory, SWARM

        logger.info(f"StartLinearMotion START")
        logger.info(DRONES)
        if(SWARM._is_open and len(args_arr) == len(DRONES)):
            # SWARM = Swarm(uris=Quad.activeURIS,factory=factory)
            # SWARM.open_links()
            args_dict = {d: a for (a, d) in zip(args_arr, DRONES)}
            SWARM.parallel(SwarmControl.start_linear_motion,args_dict)
            logger.info(f"StartLinearMotion STOP")
            # SWARM.close_links()
        return OutputDict(True,"OK").dict
    
    def All_MoveDistance(args_arr : List[Move]):
        global DRONES, URIS, factory, SWARM

        logger.info(f"MoveDistance START")
        logger.info(DRONES)
        if(SWARM._is_open and len(args_arr) == len(DRONES)):
            # SWARM = Swarm(uris=Quad.activeURIS,factory=factory)
            # SWARM.open_links()
            args_dict = {d: a for (a, d) in zip(args_arr, DRONES)}
            SWARM.parallel(SwarmControl.move_distance,args_dict)
            logger.info(f"MoveDistance STOP")
            # SWARM.close_links()
        return OutputDict(True,"OK").dict

    def start_linear_motion(scf, args:Move):
        commander = MotionCommander(scf,default_height=DefaultHeight)
        commander.start_linear_motion( velocity_x_m=args.x, velocity_y_m=args.y, velocity_z_m= args.mz,rate_yaw=args.yaw_rate)

    def move_distance(scf, args_dict:Move):
        commander = MotionCommander(scf,default_height=DefaultHeight)
        commander.move_distance(distance_x_m=args_dict.x, distance_y_m=args_dict.y, distance_z_m= args_dict.z,velocity=args_dict.velocity)

    def Parallelize_safe(func,arguments:dict = {}):
        global DRONES, URIS, factory, SWARM
        logger.info(f"Parallelize START")
        logger.info(Quad.activeURIS)
        if(SWARM.is_open):
            # SWARM = Swarm(uris=Quad.activeURIS,factory=factory)

            # SWARM.open_links()
            SWARM.parallel_safe(func = func,args_dict=arguments)
            # SWARM.close_links()
    def Parallelize(func,arguments:dict = {}):
        global DRONES, URIS, factory, SWARM
        logger.info(f"Parallelize START")
        logger.info(Quad.activeURIS)
        if(SWARM.is_open):
            # SWARM = Swarm(uris=Quad.activeURIS,factory=factory)

            # SWARM.open_links()
            SWARM.parallel(func = func,args_dict=arguments)
            # SWARM.close_links()