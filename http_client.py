import sys
import socket
from urlparse import urlparse

# Checking if the input is of the right form.
if len(sys.argv) != 2:
    sys.exit(-1)

#Storing the inputed URL.
enteredUrl = sys.argv[1]

if(enteredUrl[0:7] != 'http://'):
    print("Does not start with HTTP://")
    sys.exit(500)

#Printing the URL to screen for the user to see.
# print(enteredUrl)

def accessRequest(enteredUrl):
#Parsing through the URL input using the URLparse library.
    o = urlparse(enteredUrl)
    httpMsg = "GET "

    if(o.scheme == 'https'):
        print ("Attempted to HTTPS")
        sys.exit(403)

    host = (o.netloc, 80)

    if (o.path==""):
        httpMsg += "/"
    else:
        httpMsg += o.path

    httpMsg += " HTTP/1.0"
    httpMsg += "\r\n\r\n"

    socketObj = socket.create_connection(host)

    socketObj.sendall(httpMsg)

    msgReturn = socketObj.recv(1024)

    socketObj.close()



print(msgReturn)
