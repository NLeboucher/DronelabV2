from pydantic import BaseModel
class Move(BaseModel):
    radio: str
    x:float
    y:float
    z:float
    yaw_rate:float | None = None
    velocity:float | None = None



