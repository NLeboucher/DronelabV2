


import pygame as pg
from random import uniform
from vehicle import Vehicle
from logger import Logger
from boid import Boid
from API.swarmcontrol import SwarmControl
from API.logger import Logger   
import math

log = Logger("boids.log")

class Quad (Boid):
    names = {"Diane", "Gauthier","Etienne", "Noé", "Tom","Thais","Claire","Pelle","Clément",}
    positions = {"Diane":(0.,0.),"Gauthier":(1.,0.),"Etienne":(0.,1.),"Noé":(2.,0.),"Tom":(0.,2.),"Thais":(2.,1.),"Claire":(1.,2.),"Pelle":(2.,2.),"Clément":(3.,0.)}
    SWARM = SwarmControl.get_swarm()
    def __init__(self, position = "", name="default",usedrones = False):
        if(name == "default"):
            self.name = Quad.names.pop()
        if(usedrones):
            self.URI = SwarmControl.URIS.pop()
            self.scf = SwarmControl.get_swarm()._cfs[self.URI]
        super().__init__()
        self.position = pg.Vector2(Quad.positions[self.name][0],Quad.positions[self.name][1])
        #self.position = pg.Vector2(0,0) # need to override the position of the boid at the start also later
        # self.start_position = pg.math.Vector2(
        #     position[0],position[1])
    def update(self, dt, boids):
        super().update(dt,boids)
        speed, new_heading = self.velocity.as_polar()

        log.info(f"DEBUG : {self.name} velocity : {self.position}, speed : {speed}, heading : {new_heading}")
        # 1 getEstimatedPositions
        # 2 set positionsof the boids from the drones estimated positions
        # 3 update the boids
        # 4 set speed of the drones from the boids speed
        # use here also setspeed to set the speed of the drone
    @staticmethod
    def GetEstimatedDronePositions(self):
        ans = SwarmControl.All_GetEstimatedPositions()["Positions"][self.URI]
        self.position = pg.Vector2(ans[0],ans[1])
        super().set_reel_position()
        
        return self.position
    @staticmethod
    def SetDronePositions(self):
        SwarmControl.All_StartLinearMotion(self.posi)



        
        

