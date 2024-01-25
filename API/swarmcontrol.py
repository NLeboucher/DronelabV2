import time
import cflib.crtp
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.positioning.position_hl_commander import PositionHlCommander
from typing import List
import os
import os, sys
import uvicorn
path = os.getcwd()
folders = path.split("/")
if("DronelabV2" in folders):
    path = "/".join(folders[:folders.index("DronelabV2")+1])
    print("found: ",path)
    from API.logger import Logger
    from API.move import Move, Velocity
    from API.outputdict import OutputDict
    from API.enums.option import Option   
    from API.quad import Quad
    from API.swarm import Swarm
    from motion_commander import MotionCommander
else:
    Exception("Executed from Wrong folder, you need to be in DronelabV2")

from typing import List

debug = True
logger = Logger("log.txt",debug)
#
URIS = {
    'radio://0/28/2M/E7E7E7E703',
    'radio://0/80/2M/E7E7E7E701',
    'radio://0/27/2M/E7E7E7E702',
    'radio://0/80/2M/E7E7E7E7E7',
    # Add more URIs if you want more copters in the swarm
}
DRONES = []
factory = CachedCfFactory(ro_cache='./cache',rw_cache='./cache')
SWARM = Swarm(URIS, factory)
DefaultZSpeed = 0.2
DefaultHeight = 0.3
positions = dict()
commanders = dict()
class SwarmControl:

    def __init__(self, default_height=0.3, default_z_speed=0.2):
        global SWARM,factory, DRONES, commander, DefaultZSpeed, DefaultHeight, positions
        self.DRONES = []
        # SWARM = None
        # factory = None
        self.factory = factory
        DefaultZSpeed = default_height
        DefaultHeight = default_z_speed
        self.positions = dict()
    def get_swarm():
        return SWARM
    
    def OpenLinks(self,):
        global SWARM, URIS, factory, DRONES
        self.DRONES = []
        cflib.crtp.init_drivers()
        logger.info(f"{URIS}")
        
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
        self.DRONES = [ d  for d in SWARM._cfs.keys() if SWARM._cfs[d]]
        logger.info(f"{self.DRONES}")
        SWARM.alt_prepare_estimator()

        return OutputDict(self.DRONES,"URIS").dict

    def CloseLinks(self,):
        #cflib.crtp.init_drivers()
        #factory = CachedCfFactory(ro_cache='./cache',rw_cache='./cache')
        # #SWARM = Swarm(URIS, factory)
        # global SWARM
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
        self.DRONES = [ d for d in SWARM._cfs.keys() if SWARM._cfs[d].is_link_open()]
        return OutputDict(self.DRONES,"URIS").dict

    def Get_All_Drones():
        global DRONES, URIS, factory, SWARM
        return self.DRONES

    def All_Land(self,):
        logger.info(f"Land START")
        logger.info(self.DRONES)
        if(SWARM._is_open):
            # SWARM = Swarm(uris=Quad.activeURIS,factory=factory)

            # SWARM.open_links()
            SWARM.parallel(SwarmControl.Land)
            # SWARM.close_links()
            logger.info(f"Land STOP")
        return [OutputDict(True,"OK").dict for d in self.DRONES]
    def Land(scf):
        # global commanders, DefaultZSpeed
        # commander = PositionHlCommander(crazyflie=scf,default_height=DefaultHeight,controller=PositionHlCommander.CONTROLLER_MELLINGER)
        #commander = MotionCommander(scf,default_height=DefaultHeight)
        commanders[scf].land(DefaultZSpeed)

    def All_TakeOff(self,):
        logger.info(f"All_TakeOff START")
        logger.info(self.DRONES)
        if(SWARM._is_open):
            SWARM.parallel(SwarmControl.Take_off)
            logger.info(f"All_TakeOff STOP")
        return OutputDict(True,"OK").dict
    def Take_off(self,scf,default_height=None):
        global commanders, DefaultZSpeed, DefaultHeight
        # commander = PositionHlCommander(crazyflie=scf,default_height=DefaultHeight,controller=PositionHlCommander.CONTROLLER_MELLINGER)
        commanders[scf] = MotionCommander(scf,default_height=DefaultHeight,isflying=False)
        commanders[scf].take_off(height=default_height,velocity=DefaultZSpeed)

    def All_GetEstimatedPositions(self):
        global a
        logger.info(f"GetEstimatedPosition START")
        logger.info(self.DRONES)
        if(SWARM._is_open):
            # SWARM = Swarm(uris=Quad.activeURIS,factory=factory)
            # SWARM.open_links()

            self.positions = SWARM.get_estimated_positions()


            # self.positions = SWARM.get_estimated_positions()

            logger.info(f"GetEstimatedPosition STOP")
            # SWARM.close_links()
        return OutputDict(self.positions,"Positions").dict
    def altAll_GetEstimatedPositions(self):
        logger.info(f"GetEstimatedPosition START")
        logger.info(self.DRONES)
        if(SWARM._is_open):
            # SWARM = Swarm(uris=Quad.activeURIS,factory=factory)
            # SWARM.open_links()
            
            self.positions = SWARM.alt_get_estimated_positions()


            # self.positions = SWARM.get_estimated_positions()

            logger.info(f"GetEstimatedPosition STOP")
            # SWARM.close_links()
        return OutputDict(self.positions,"Positions").dict
    def All_StartLinearMotion(self, args_arr : List[Velocity]):
        global DRONES, URIS, factory, SWARM
        logger.info(f"All_StartLinearMotion START with {len(args_arr)} args")
        logger.info(self.DRONES)
        if(SWARM._is_open and len(args_arr) == len(self.DRONES)):
            logger.info(f"args_arr{args_arr}, DRONES{self.DRONES}")
            args_dict = {d: a.Export() for (a, d) in zip(args_arr, self.DRONES)}
            logger.info(f"All_StartLinearMotion{args_dict} {Velocity.Import(args_dict[self.DRONES[0]])}")
            SWARM.parallel_safe(SwarmControl.start_linear_motion,args_dict)
            logger.info(f"All_StartLinearMotion STOP")
            # SWARM.close_links()
        return OutputDict(True,"OK").dict
    
    def All_MoveDistance(args_arr : List[Move]):
        global DRONES, URIS, factory, SWARM

        logger.info(f"MoveDistance START")
        logger.info(self.DRONES)
        if(SWARM._is_open and len(args_arr) == len(self.DRONES)):
            # SWARM = Swarm(uris=Quad.activeURIS,factory=factory)
            # SWARM.open_links()
            args_dict = {d: a.Export() for (a, d) in zip(args_arr, self.DRONES)}
            logger.info(f"MoveDistance{args_dict}")
            SWARM.parallel(SwarmControl.move_distance,args_dict)
            logger.info(f"MoveDistance STOP")
            # SWARM.close_links()
        return OutputDict(True,"OK").dict

    def start_linear_motion(scf, *args):
        global commanders, DefaultZSpeed, DefaultHeight
        arg= Velocity.Import(args)
        logger.info(f"start_linear_motion START with {args} so {arg}")

        # logger.info(f"start_linear_motion START")
        # logger.info(f"start_linear_motion with{arg.x, arg.y, arg.z, arg.yaw_rate}")
        commanders[scf].start_linear_motion( velocity_x_m=arg.Vx, velocity_y_m=arg.Vy, velocity_z_m= arg.Vz,rate_yaw=arg.yaw_rate)
        logger.info(f"start_linear_motion STOP")

    def move_distance(scf, *args_dict):
        global commanders
        args= Move.Import(args_dict)
        logger.info(f"start_linear_motion with{args.x, args.y, args.z, args.yaw_rate} for {scf._link_uri}")
        # commanders[scf] = MotionCommander(scf,default_height=DefaultHeight,isflying=True)
        commanders[scf].move_distance(distance_x_m=args.x, distance_y_m=args.y, distance_z_m= args.z,yaw=args.yaw_rate,velocity=args.velocity)

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
            SWARM.parallel(func = func,args_dict=arguments)