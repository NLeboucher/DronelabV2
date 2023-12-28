import pygame as pg
from random import uniform
from vehicle import Vehicle
from logger import Logger
import math


log = Logger("boids.log")
class Boid(Vehicle):

    # CONFIG
    debug = True
    min_speed = .01
    max_speed = .2
    max_force = 1
    max_turn = 5
    perception = 4000
    crowding = 100
    can_wrap = False
    edge_distance_pct = 5
    name= "default"
    ###############

    def __init__(self,start_pos = None,start_vel = None,min_speed = 0.01,max_speed = 0.2,max_force = 1,can_wrap = False):
        Boid.set_screen_boundary(Boid.edge_distance_pct)
        Boid.min_speed = min_speed
        Boid.max_speed = max_speed
        Boid.max_force = max_force
        Boid.can_wrap = can_wrap

        # Randomize starting position and velocity
        if start_pos is None:
            start_position = pg.math.Vector2(
                uniform(20, Boid.max_x),
                uniform(20, Boid.max_y))
        else:
            start_position = pg.math.Vector2(start_pos[0],start_pos[1])
        if start_vel is None:
            start_velocity = pg.math.Vector2(
                uniform(-1, 1) * Boid.max_speed,
                uniform(-1, 1) * Boid.max_speed)
        else:
            start_velocity = pg.math.Vector2(start_vel[0],start_vel[1])
        
        # start_position = pg.math.Vector2(
        #     uniform(20, Boid.max_x),
        #     uniform(20, Boid.max_y))
        # start_velocity = pg.math.Vector2(
        #     uniform(-1, 1) * Boid.max_speed,
        #     uniform(-1, 1) * Boid.max_speed)

        super().__init__(start_position, start_velocity,
                         Boid.min_speed, Boid.max_speed,
                         Boid.max_force, Boid.can_wrap)

        self.rect = self.image.get_rect(center=self.position)

        self.debug = Boid.debug

    def separation(self, boids):
        steering = pg.Vector2()
        for boid in boids:
            dist = self.position.distance_to(boid.position)
            if dist < self.crowding:
                steering -= (boid.position - self.position)*((dist-self.crowding)**2)/(dist**2)#*math.exp(4-dist/10)#/#(4*dist**3)  #* math.exp(100/dist)
        steering = self.clamp_force(steering)
        return steering/100

    def alignment(self, boids):
        steering = pg.Vector2()
        for boid in boids:
            steering += boid.velocity
        steering /= len(boids)
        steering -= self.velocity
        steering = self.clamp_force(steering)
        return (steering / 17000)

    def cohesion(self, boids):
        steering = pg.Vector2()
        for boid in boids:
            steering += boid.position
        steering /= len(boids)
        steering -= self.position
        steering = self.clamp_force(steering)
        return (steering / 100000)

    def update(self, dt, boids):
        steering = pg.Vector2()

        if (not self.can_wrap):
            steering += self.avoid_edge()

        neighbors = self.get_neighbors(boids)
        if neighbors:

            separation = self.separation(neighbors)
            alignment = self.alignment(neighbors)
            cohesion = self.cohesion(neighbors)

            # DEBUG
            # separation *= 0
            # alignment *= 0
            # cohesion *= 0

            steering += separation + alignment + cohesion
            # for boid in neighbors:
            #     if boid != self:
            #         if pg.sprite.collide_circle(self, boid):
            #             # If there's a collision, change the boid's direction
            #             steering = -steering

        # steering = self.clamp_force(steering)
        
        super().update(dt, steering)

    def get_neighbors(self, boids):
        neighbors = []
        for boid in boids:
            if boid != self:
                dist = self.position.distance_to(boid.position)
                if dist < self.perception:
                    neighbors.append(boid)
        return neighbors
