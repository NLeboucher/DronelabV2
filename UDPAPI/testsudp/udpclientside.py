import socket

def udp_client(host: str = "127.0.0.1", port: int = 9999, message: str = ""):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode(), (host, port))
    # response, addr = sock.recvfrom(1024)  # Receive response from server
    # print(f"Server response: {response.decode()}")

if __name__ == "__main__":
    # udp_client("10.1.224.115", 3306, "2U8398U298RH932GYR°GY23")
    udp_client("127.0.0.1", 9999, "Hello it's me")
