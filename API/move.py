from pydantic import BaseModel
class Move(BaseModel):
    x:float
    y:float
    z:float
    yaw_rate:float | None = None
    velocity:float | None = None
    def Export(self):
        return [self.x,self.y,self.z,self.yaw_rate,self.velocity]
    def Import(moveArr):
        self.x = moveArr[0]
        self.y = moveArr[1]
        self.z = moveArr[2]
        self.yaw_rate = moveArr[3]
        self.velocity = moveArr[4]

class Velocity(BaseModel):
    Vx:float
    Vy:float
    Vz:float
    yaw_rate:float | None = None
    def Export(self):
        return [self.Vx,self.Vy,self.Vz,self.yaw_rate]
    def Import(velocityArr):
        Vx = velocityArr[0]
        Vy = velocityArr[1]
        Vz = velocityArr[2]
        yaw_rate = velocityArr[3]
        return Velocity(Vx=Vx,Vy=Vy,Vz=Vz,yaw_rate=yaw_rate)
