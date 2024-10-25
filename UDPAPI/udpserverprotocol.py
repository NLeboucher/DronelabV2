import asyncio
import socket
import json
from logger import Logger
from UDPAPI.outputdict import OutputDict

log=Logger("logUDP.txt",True)

class UDPServerProtocol:
    # message_dict = null
    def connection_made(self, transport):
        self.transport = transport
        log.info("UDP server is ready")
        # print("UDP server is ready")

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
        log.info(f"Received {message} from {addr}")
        # print(f"Parsed {message} from {addr} to {message_dict}")

        return message_dict

    def connection_lost(self, exc):
        print("Connection lost")

class UDPServer:
    async def udp_server(host: str, port: int):
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: UDPServerProtocol(), local_addr=(host, port)
        )
        log.info(f"UDP server started at {host}:{port}")
    async def startup_event(port:int = 9999):
        # Start UDP server
        asyncio.create_task(UDPServer.udp_server("127.0.0.1", port=port))

class UDPClient:
    def __init__(self, server_host="127.0.0.1", server_port=9999,timeout = 0.1):
        self.server_address = (server_host, server_port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)

    def send_message(self, message:str):
        print(f"Client sending {message} to {self.server_address}")
        try:
            log.info(f"Client sending {message} to {self.server_address}")
            self.sock.sendto(message.encode('utf-8'), self.server_address)
            data, server = self.sock.recvfrom(4096)
            log.info(f"Client received {data.decode('utf-8')} from {server}")
            return data.decode('utf-8')
        except socket.timeout:
            log.warning("No response received within the timeout period.")
            return ''  # Return an empty string if no response is received

        except Exception as e:
            return str(e)
    def send_message(self, message:OutputDict):
        try:
            log.info(f"Client sending {str(message)} to {self.server_address}")
            self.sock.sendto(json.dumps(message.dict).encode('utf-8'), self.server_address)
            data, server = self.sock.recvfrom(4096)
            log.info(f"Client received {data.decode('utf-8')} from {server}")
            return data.decode('utf-8')
        except Exception as e:
            print(e)
            return str(e)