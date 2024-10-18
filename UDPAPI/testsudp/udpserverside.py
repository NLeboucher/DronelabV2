import asyncio
from fastapi import FastAPI

app = FastAPI()

async def udp_server(host: str, port: int):
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPServerProtocol(), local_addr=(host, port)
    )

class UDPServerProtocol:
    def connection_made(self, transport):
        self.transport = transport
        print("UDP server is ready")

    def datagram_received(self, data, addr):
        message = data.decode()
        print(f"Received {message} from {addr}")
        self.transport.sendto(b"Message received", addr)

    def connection_lost(self, exc):
        print("Connection lost")

@app.on_event("startup")
async def startup_event():
    # Start UDP server
    asyncio.create_task(udp_server("127.0.0.1", 9999))

@app.get("/")
async def root():
    return {"message": "UDP Server Running"}

def main(host="0.0.0.0", port=8001):

    uvicorn.run("udpserverside:app", host=host, port=port)
if __name__ == "__main__":
    main()