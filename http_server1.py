# http_server1.py written by Leo Ji (ljd753) and Lukas J. Gladic (ljg766)
# for EECS 340 Winter 2019 with Professor Yan Chen

import sys
import socket
import os

# https://stackoverflow.com/questions/30686701/python-get-size-of-string-in-bytes
def utf8len(s):
    return len(s.encode('utf-8'))

def httpRead(requestMsg):
    print(requestMsg)
    httpParts = requestMsg.split()

    if (httpParts[0] != "GET"):
        sys.exit(101)

    path = httpParts[1]
    filename = path[1:]

    return fileSearch(filename)

def fileSearch(filename):

    # https://stackoverflow.com/questions/11968976/list-files-only-in-the-current-directory
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in files:
        if (f == filename):
            if (f[-5:]==".html" or f[-4]==".htm"):
                fileContent = open(f, "r")
                return (fileContent, 200)
            else:
                return ("", 403)

    return ("", 404)

# Checking if the input is of the right form
if len(sys.argv) != 2:
    sys.exit(-1)

HOST = ""
portRequested = int(sys.argv[1])

# basic server adapted from https://realpython.com/python-sockets/#echo-server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((HOST, portRequested))
s.listen(5)

conn, addr = s.accept()

print('Connected by ', addr)

data = ""

while True:
    data += conn.recv(1024)
    print(data)
    if not data:
        break

print(data)

fileContent, responseCode = httpRead(data)

responseAll == "HTTP/1.0 "

if(responseCode == 403):
    responseAll += "403 Forbidden"
    fileContent = "<h1>403 Forbidden</h1>"
elif(responseCode == 404):
    responseAll += "404 Not Found"
    fileContent = "<h1>404 Not Found</h1>"
else:
    responseAll += "200 OK"

responseAll += "\r\n"
responseAll += "Content-Type: text/html"
responseAll += "\r\n"
responseAll += "Content-Length: "
responseAll += utf8len(fileContent)
responseAll += "\r\n"

responseAll += "\r\n"
responseAll += fileContent
# full response constructed

conn.sendall(fileContent)

conn.close()
s.close()
