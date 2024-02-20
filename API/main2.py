import socket
from API.swarmcontrol import SwarmControl
from API.logger import Logger
from API.move import Move
import json

# Initialize your logger and swarm control as before
logger = Logger("log.txt", False)
swarm = SwarmControl()

# Define a simple method to decode incoming messages and perform actions
def handle_message(data, addr):
    try:
        message = json.loads(data.decode('utf-8'))
        command = message.get('command')

        if command == 'OpenLinks':
            logger.info("OpenLinks")
            response = swarm.OpenLinks()
        elif command == 'CloseLinks':
            logger.info("CloseLinks")
            response = swarm.CloseLinks()
        elif command == 'takeoff':
            logger.info("takeoff")
            response = swarm.All_TakeOff()
        elif command == 'land':
            response = swarm.All_Land()
        elif command == 'getestimatedpositions':
            response = swarm.All_GetEstimatedPositions()
        elif command == 'All_StartLinearMotion':
            args_arr = [Move(**move) for move in message.get('args', [])]
            response = swarm.All_StartLinearMotion(args_arr)
        elif command == 'All_MoveDistance':
            args_arr = [Move(**move) for move in message.get('args', [])]
            response = swarm.All_MoveDistance(args_arr)
        else:
            response = {"error": "Unknown command"}

        # Optionally, send a response back to the sender
        # sock.sendto(json.dumps(response).encode('utf-8'), addr)
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        # Optionally, inform the sender about the error
        # sock.sendto(json.dumps({"error": str(e)}).encode('utf-8'), addr)

# Setup UDP server
def udp_server(host='127.0.0.1', port=12345):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((host, port))
        print(f"UDP server listening on {host}:{port}")

        while True:
            data, addr = sock.recvfrom(4096)  # Adjust buffer size as needed
            print(f"Received message from {addr}")
            handle_message(data, addr)

if __name__ == "__main__":
    udp_server()
