from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from threading import Thread, Lock

import asyncio
from pydantic import BaseModel
from typing import List
import os, sys
import uvicorn

stop = False
stop_lock = Lock()
path = os.getcwd()
folders = path.split("/")
if("DronelabV2" in folders):
    path = "/".join(folders[:folders.index("DronelabV2")+1])
    sys.path.insert(0, path)

    print("Imported Dependencies from: ",path)
    from UDPAPI.udpserverprotocol import UDPServerProtocol, UDPServer, UDPClient
    from UDPAPI.logger import Logger
    from UDPAPI.move import Move, Velocity
    from UDPAPI.outputdict import OutputDict
    from UDPAPI.swarmcontrol import SwarmControl
else:
    Exception("Executed from Wrong folder: {path}, you need to be in DronelabV2")


class ConnectionManager:
    def __init__(self):
        self._active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self._active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self._active_connections.remove(websocket)

    async def sendCoordinates(self, message: str, websocket: WebSocket):
        for connection in self._active_connections:
            logger.info(f"sendCoordinates: {message}")
            await connection.send_text(message)
        
manager = ConnectionManager()
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)
logger = Logger("logD.txt",True)
s = SwarmControl()
s.OpenLinks()
posThread = None
@app.get("/HelloWorld/")
async def read_root():
    global s
    s = SwarmControl()

    logger.info("root")
    return {"message": "Welcome to the Drone Control API"}

@app.get("/OpenLinks/")
async def OpenLinks():
    global s
    logger.info("OpenLinks")
    ret = s.OpenLinks()
    logger.info(f"OpenLinks: {ret}")
    return ret
    
@app.get("/CloseLinks/")
async def CloseLinks():
    global s

    logger.info("CloseLinks")
    ret = s.CloseLinks()
    return ret

@app.get("/All_TakeOff/")
async def TakeOff():
    global s
    print(s.DRONES)
    logger.info("takeoff")
    ret = s.All_TakeOff()
    return ret

@app.websocket("/ws")
async def websocket_handler(websocket: WebSocket):
    global posThread
    logger.info("websocket_handling")
    # Start the websocket handling in a separate thread
    posThread = Thread(target=posWebsocket, args=(websocket,))
    posThread.start()

@app.get("/All_Land/")
async def AllLand():
    return s.All_Land()
async def posWebsocket(websocket: WebSocket):
    async def connect(websocket: WebSocket):
        await manager.connect(websocket)

    async def disconnect(websocket: WebSocket):
        await manager.disconnect(websocket)

    async def websocket_endpoint(websocket: WebSocket):
        await manager.connect(websocket)
        try:
        # Configure RealSense pipeline
            while True:
                data = await GetEstimatedPositions()
                await manager.sendCoordinates(data, websocket)
        except Exception as e:
            print(e)
        finally:
            await manager.disconnect(websocket)
            print("Websocket closed")

# @app.get("/getestimatedpositions/")
# async def GetEstimatedPositions(boule: bool = False):
#     global s
#     # return s.All_GetEstimatedPositions()
#     ret = s.altAll_GetEstimatedPositions() if boule else s.All_GetEstimatedPositions()
#     logger.info(f"GetEstimatedPositions: {ret}")
#     return ret
#     # default the new GetEstimatedPositions to the old one for now later to be deprecated

@app.get("/getestimatedpositionsUDPstart/")
async def GetEstimatedPositions():
    Thread(target=send_estimated_positions, daemon=True).start()
    return {"status": "Thread started"}

async def send_estimated_positions():
    while True:
        UDPClient.send_message(s.All_GetEstimatedPositions())
        with(stop_lock):
            if stop:
                stop=False
                break

# stop sending estimated positions to the UDP client
@app.get("/getestimatedpositionsUDPstop/")
async def GetEstimatedPositions():
    with(stop_lock):
        if stop:
            stop=False

# send estimated positions to the UDP client
@app.get("/getestimatedpositions/")
async def GetEstimatedPositions():
    global s
    ret = s.All_GetEstimatedPositions()
    return ret

@app.on_event("startup")
async def start_udp_server():
    # Start the UDP server on app startup
    await UDPServer.startup_event(port=9999)

@app.post("/AllSetSpeed/")
async def AllSetSpeed(args_arr: List[Velocity] ): #: OutputDict(List[Velocity],"Drones")
        # 
    return s.All_StartLinearMotion(args_arr)

@app.post("/All_MoveDistance/")
async def All_MoveDistance(args_arr : List[Move]):
    global s

    logger.info(f"MoveDistance {args_arr}")
    return s.All_MoveDistance(args_arr)

def main(host="0.0.0.0", port=8000):
    # workers are set to 1 to avoid conflicts with the RealSense camera
    # https://www.uvicorn.org/settings/#workers
    uvicorn.run("mainD:app", host=host, port=port, workers=1, limit_concurrency=5000)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    print("Starting pose estimation thread")

class MessageHandler:
    def __init__(self, velocity_parser):
        self.velocity_parser = velocity_parser  # Dependency injection for the parser

    def handle_message(self, message: str) -> str:
        try:
            # Parse the incoming message into Velocity objects
            velocities = self.velocity_parser.parse(message)

            # Call the business logic with the parsed velocities
            response = s.All_StartLinearMotion(velocities)
            return f"Success: {response}"

        except ValueError as e:
            # Return an error message if something goes wrong
            return f"Error: {str(e)}"