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

def accessRequest(enteredUrl, counter):

    # dies on 10
    if (counter > 9):
        print("10 redirects, exiting")
        return ("", 10)

#Parsing through the URL input using the URLparse library.
    exitCode = 0
    o = urlparse(enteredUrl)


    hostTemp = o.netloc.split(":")
    if(len(hostTemp) == 1):
        host = (hostTemp[0], 80)
    elif(len(hostTemp) == 2):
        host = (hostTemp[0], hostTemp[1])
    else:
        print("Entered URL and ports are nonsensical")
        sys.exit(102)

    httpMsg = "GET "

    if(o.scheme == 'https'):
        print ("Attempted to HTTPS")
        sys.exit(403)

    # host = (o.netloc, port)
    print(host)

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
    # print(int(firstLine[9:12]))

    responseCode = int(firstLine[9:12])

    # print(type(responseCode))

    if (responseCode == 301 or responseCode == 302):
        # print(firstLine)
        for line in msgReturn.splitlines():
            loc = line.find("Location: ")
            if (loc != -1):
                # print(loc)
                newUrl = line[10:]
                break
    # elif firstLine.find("302 Moved Temporarily"):
    #     for line in msgReturn.splitlines():
    #         loc = line.find("Location: ")
    #         if (loc != -1):
    #             newUrl = line[10:]
    #             break

    if (responseCode >= 400 and responseCode < 500):
        # print(responseCode)
        exitCode = responseCode

    contentType = msgReturn.find("Content-Type: text/html")
    if(contentType == -1):
        print("Returned type is not text/html")
        sys.exit(101)

    socketObj.close()

    # print(newUrl)
    if(newUrl):
        print("Redirected to: " + newUrl)
        (msgReturn, exitCode) = accessRequest(newUrl, counter + 1)

    return (msgReturn, exitCode)

(msgReturn, exitCode) = accessRequest(enteredUrl , 0)

# from https://stackoverflow.com/questions/4020539/process-escape-sequences-in-a-string-in-python
print(str(msgReturn).decode('string_escape'))

if (int(exitCode) > 0):
    # print(exitCode)
    sys.exit(exitCode)

sys.exit(0)
