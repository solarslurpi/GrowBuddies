import socket

values_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = '127.0.0.1'
udp_port = 8094
# Set the SO_REUSEADDR socket option
values_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

values_socket.bind((host, udp_port))
while True:
    packet = values_socket.recv(1024)
    # Step 1: Decode the bytes
    decoded_str = packet.decode()
    print(f"{decoded_str}")


