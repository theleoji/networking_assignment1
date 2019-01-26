import sys
import socket
from urlparse import urlparse

# Checking if the input is of the right form.
if len(sys.argv) != 2:
    exit(-1)

#Storing the inputed URL.
enteredUrl = sys.argv[1]

#Printing the URL to screen for the user to see.
print(enteredUrl)

#Parsing through the URL input using the URLparse library.
o = urlparse(enteredUrl)

host = ("eecs.northwestern.edu", 80)

socketObj = socket.create_connection(host)

socketObj.sendall("GET / HTTP/1.0\r\n\r\n")

msgReturn = socketObj.recv(1024)

socketObj.close()

print(msgReturn)
