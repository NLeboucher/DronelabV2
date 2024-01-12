from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/")
def read_item():
    uris = "1;2"
    uri = uris.split(";")
    print(uri)
    ret=dict()
    for i in uri:
        ret["Drone_ID"]=i
    return ret


@app.get("/getposition")
def getposition():

    return {"Drone_ID":"1","Position_Drone": [0.1,0.9,65], "Vitesses_Drone": [0.2,1.2,12.0]}

'''
Envoie
{
    "Drone_ID": "string",
    "Position": 0.0,
    "Rotation": true
}
'''
