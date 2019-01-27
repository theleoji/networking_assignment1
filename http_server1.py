# http_server1.py written by Leo Ji (ljd753) and Lukas J. Gladic (ljg766)
# for EECS 340 Winter 2019 with Professor Yan Chen

import sys
import socket

# Checking if the input is of the right form
if len(sys.argv) != 2:
    sys.exit(-1)

#Storing the inputed URL.
HOST = socket.gethostbyname(socket.gethostname())
portRequested = sys.argv[1]

# basic server adapted from https://realpython.com/python-sockets/#echo-server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((HOST, portRequested))
s.listen()

conn, addr = s.accept()

with conn:
    print('Connected by ', addr)
    while True:
        data = conn.recv(1024)
        if not data:
            break
        conn.sendall(data)