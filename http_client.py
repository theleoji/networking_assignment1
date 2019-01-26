import sys
import socket

if len(sys.argv) != 2:
    exit(-1)

enteredUrl = sys.argv[1]

print(enteredUrl)

host = ("eecs.northwestern.edu", 80)

socketObj = socket.create_connection(host)

socketObj.sendall("GET / HTTP/1.0\r\n\r\n")

msgReturn = socketObj.recv(1024)

socketObj.close()

print(msgReturn)
