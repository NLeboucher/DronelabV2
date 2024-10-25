import asyncio
from fastapi import FastAPI
from typing import Dict
import uvicorn
import time
from contextlib import asynccontextmanager

app = FastAPI()

# Global dictionary to store messages received by UDP server
message_dict: Dict[str, str] = {"zef": "zef"}

class UDPServerProtocol:
    def connection_made(self, transport):
        self.transport = transport
        print("UDP server is ready")

    def datagram_received(self, data, addr):
        message = data.decode()
        print(f"At {time.time()} received {message} from {addr}")

        # Store received message in dictionary with client's address as the key
        message_dict[f"{addr}"] = message

        # Send acknowledgment to the client
        self.transport.sendto(b"Message received", addr)

    def connection_lost(self, exc):
        print("Connection lost")

# Define the UDP server
async def udp_server(host: str, port: int):
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPServerProtocol(), local_addr=(host, port)
    )

# Use lifespan context for startup events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start UDP server
    udp_task = asyncio.create_task(udp_server("127.0.0.1", 9999))
    yield
    # Optionally, you may handle cleanup here if needed
    udp_task.cancel()

app.router.lifespan_context = lifespan

# HTTP Endpoint to get the dictionary of messages
count: int = 1
@app.get("/get_messages")
async def get_messages():
    global count
    count += 1
    return {"messages(" + str(count) + ")": message_dict}

@app.get("/")
async def root():
    return {"message": "UDP Server Running"}

def main(host="0.0.0.0", port=8001):
    uvicorn.run("udpserversidegeneral:app", host=host, port=port)

if __name__ == "__main__":
    main()
