import asyncio
import socket
import json

class UDPServerProtocol:
    # message_dict = null
    def connection_made(self, transport):
        self.transport = transport
        print("UDP server is ready")

    def datagram_received(self, data, addr):
        message = data.decode()
        print(f"Received {message} from {addr}")
        try:
            global message_dict
            # Parse the message as JSON
            message_dict = json.loads(message)

        except json.JSONDecodeError:
            # Handle invalid JSON format
            response = "Error: Invalid message format"
            self.transport.sendto(response.encode(), addr)
        print(f"Parsed {message} from {addr} to {message_dict}")

        return message_dict

    def connection_lost(self, exc):
        print("Connection lost")

class UDPServer:
    async def udp_server(host: str, port: int):
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPServerProtocol(), local_addr=(host, port)
        )
    async def startup_event(port:int = 9999):
        # Start UDP server
        asyncio.create_task(UDPServer.udp_server("127.0.0.1", port=port))

class UDPClient:
    def __init__(self, server_host="127.0.0.1", server_port=9000):
        self.server_address = (server_host, server_port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_message(self, message:str):
        try:
            self.sock.sendto(message.encode('utf-8'), self.server_address)
            data, server = self.sock.recvfrom(4096)
            return data.decode('utf-8')
        except Exception as e:
            return str(e)
    def send_message(self, message:any):
        try:
            self.sock.sendto(json.dumps(message).encode('utf-8'), self.server_address)
            data, server = self.sock.recvfrom(4096)
            return data.decode('utf-8')
        except Exception as e:
            return str(e)