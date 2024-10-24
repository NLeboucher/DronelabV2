import pygame as pg

from pygame.locals import *

from API.logger import Logger
from API.room import Room

log = Logger("boids.log")

class Vehicle(pg.sprite.Sprite):
    # default image is a li'l white triangle
    # image = pg.Surface((10, 10), pg.SRCALPHA)
    # pg.draw.polygon(image, pg.Color('blue'),
    #                 [(15, 5), (0, 2), (0, 8)])
    image = pg.image.load("logo32x32.png")
    #self.position = pg.Vector2(0,0)
    #self.set_reel_position()
    def __init__(self, position, velocity, min_speed, max_speed,
                 max_force, can_wrap):

        super().__init__()

        # set limits
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.max_force = max_force

        # set position
        dimensions = len(position)
        assert (1 < dimensions < 4), "Invalid spawn position dimensions"

        if dimensions == 2:
            self.position = pg.Vector2(position)
            self.acceleration = pg.Vector2(0, 0)
            self.velocity = pg.Vector2(velocity)
        else:
            self.position = pg.Vector3(position)
            self.acceleration = pg.Vector3(0, 0, 0)
            self.velocity = pg.Vector3(velocity)

        self.heading = 0.0

        self.rect = self.image.get_rect(center=self.position, )#size=self.get_collide_circle()
        self.room = Room()
        # self.collisionBox = self.get_collide_circle()
    

    def get_collide_circle(self):
        """Calculate the radius of a circle that encompasses the vehicle sprite."""
        width, height = self.image.get_size()
        size =(float(width)*3.3, float(height)*3.3)
        return size
    #UPDATE HERE TO CONTROL DRONES
    def update(self, dt, steering):
        self.acceleration = steering * dt

        # enforce turn limit
        _, old_heading = self.velocity.as_polar()
        new_velocity = self.velocity + self.acceleration * dt
        speed, new_heading = new_velocity.as_polar()
        # print("DEBUG : old heading : {} new heading : {}".format(old_heading,new_heading))
        # print("DEBUG : speed : {}".format(speed))
        # if(speed > 0.5):
        #     print("DEBUG : ERROR new velocity : {}".format(new_velocity))
        # else:
        #     print("DEBUG : new velocity : {}".format(new_velocity))
        heading_diff = 180 - (180 - new_heading + old_heading) % 360
        if abs(heading_diff) > self.max_turn:
            if heading_diff > self.max_turn:
                new_heading = old_heading + self.max_turn
            else:
                new_heading = old_heading - self.max_turn

        self.velocity.from_polar((speed, new_heading))

        # enforce speed limit
        speed, self.heading = self.velocity.as_polar()
        if speed < self.min_speed:
            self.velocity.scale_to_length(self.min_speed)

        if speed > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)

        # move
        self.position += self.velocity * dt
        self.set_reel_position()
        if self.can_wrap:
            self.wrap()

        # draw
        self.image = pg.transform.rotate(Vehicle.image, -self.heading)

        if self.debug:
            center = pg.Vector2((50, 50))   

            velocity = pg.Vector2(self.velocity)
            speed = velocity.length()
            velocity += center

            acceleration = pg.Vector2(self.acceleration)
            acceleration += center

            steering = pg.Vector2(steering)
            steering += center

            overlay = pg.Surface((100, 100), pg.SRCALPHA)
            overlay.blit(self.image, center - (10, 10))

            pg.draw.line(overlay, pg.Color('green'), center, velocity, 3)
            pg.draw.line(overlay, pg.Color('red'), center + (5, 0),
                         acceleration + (5, 0), 3)
            pg.draw.line(overlay, pg.Color('blue'), center - (5, 0),
                         steering - (5, 0), 3)
            self.font = pg.font.Font(None, 20)  # Change the font and size as needed
            text_surface = self.font.render(self.name, True, pg.Color('green'))
            text_rect = text_surface.get_rect(center=(50, 50))
            overlay.blit(text_surface, text_rect)
            

            self.image = overlay
            self.rect = overlay.get_rect(center=self.position,size=self.get_collide_circle())
        else:
            self.rect = self.image.get_rect(center=self.position,size=self.get_collide_circle())

    def avoid_edge(self):
        left = self.edges[0] - self.position.x
        up = self.edges[1] - self.position.y
        right = self.position.x - self.edges[2]
        down = self.position.y - self.edges[3]

        scale = max(left, up, right, down)

        if not self.room.is_point_inside(self.position):
            center = (Vehicle.max_x / 2, Vehicle.max_y / 2)
            steering = pg.Vector2(center)
            steering -= self.position*2.8/4
        else:
            steering = pg.Vector2()

        return steering

    # def avoid_edge(self):
    #     left = self.edges[0] - self.position.x
    #     up = self.edges[1] - self.position.y
    #     right = self.position.x - self.edges[2]
    #     down = self.position.y - self.edges[3]

    #     scale = max(left, up, right, down)

    #     if scale > 0:
    #         center = (Vehicle.max_x / 2, Vehicle.max_y / 2)
    #         steering = pg.Vector2(center)
    #         steering -= self.position*2.8/4
    #     else:
    #         steering = pg.Vector2()

    #     return steering

    #TOREMOVE FROM LOGIC
    def wrap(self):
        if self.position.x < 0:
            self.position.x += Vehicle.max_x
        elif self.position.x > Vehicle.max_x:
            self.position.x -= Vehicle.max_x

        if self.position.y < 0:
            self.position.y += Vehicle.max_y
        elif self.position.y > Vehicle.max_y:
            self.position.y -= Vehicle.max_y
    def _math_proportionnal( value, out="reel"):
        match out:
            case "pyg":
                in_min=0 
                in_max=20 
                out_min=0 
                out_max=1000
            case "reel":
                in_min=0 
                in_max=1000 
                out_min=0 
                out_max=20
        return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def set_reel_position(self):
        self.realPosition = pg.Vector2(Vehicle._math_proportionnal(value=self.position.x,out="reel"),Vehicle._math_proportionnal(value=self.position.y,out="reel"))

    def set_pyg_position(self):
        self.position = pg.Vector2(Vehicle._math_proportionnal(value=self.realPosition.x,out="pyg"),Vehicle._math_proportionnal(value=self.realPosition.y,out="pyg"))
    @staticmethod
    def set_screen_boundary(edge_distance_pct):
        info = pg.display.Info()
        Vehicle.max_x = info.current_w
        Vehicle.max_y = info.current_h
        margin_w = Vehicle.max_x * edge_distance_pct / 100
        margin_h = Vehicle.max_y * edge_distance_pct / 100
        Vehicle.edges = [margin_w, margin_h, Vehicle.max_x - margin_w,
                         Vehicle.max_y - margin_h]
        log.info(f"Edges: {Vehicle.edges}, Vehicule max: {Vehicle.max_x},{Vehicle.max_y}, margin: {margin_w},{margin_h}")

    def clamp_force(self, force):
        if 0 < force.magnitude() > self.max_force:
            force.scale_to_length(self.max_force)

        return force
