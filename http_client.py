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

    msgReturn = ""

    # msgReturn = socketObj.recv(1024)
    # find Content-Length
    # clLocation = msgReturn.find("Content-Length:")
    # if (clLocation == -1):
    #     sys.exit(-2)

    # manages responses > 1024 bytes
    # borrowed from https://docs.python.org/2/library/socket.html
    while True:
        data = socketObj.recv(1024)
        if not data: break
        msgReturn += data

    # at this point, we have the full HTTP response

    # looking at HTTP response code
    firstLine = msgReturn.splitlines()[0]
    newUrl = ""
    # print(firstLine)
    if firstLine.find("301 Moved Permanently"):
        # print(firstLine)
        for line in msgReturn.splitlines():
            loc = line.find("Location: ")
            if (loc != -1):
                # print(loc)
                newUrl = line[10:]
                break

    elif firstLine.find("302 Moved Temporarily"):
        for line in msgReturn.splitlines():
            loc = line.find("Location: ")
            if (loc != -1):
                newUrl = line[10:]
                break

    socketObj.close()

    # print(newUrl)
    if(newUrl):
        msgReturn = accessRequest(newUrl)

    return msgReturn

print(accessRequest(enteredUrl))
