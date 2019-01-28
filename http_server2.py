# http_server1.py written by Leo Ji (ljd753) and Lukas J. Gladic (ljg766)
# for EECS 340 Project 1 Winter 2019 with Professor Yan Chen

import sys
import socket
import os
import select
import Queue
import errno

# https://pymotw.com/2/select/

# Returns the size of a string in bytes
# Borrowed from: https://stackoverflow.com/questions/30686701/python-get-size-of-string-in-bytes
def utf8len(s):
    return len(s.encode('utf-8'))

# Function to read the request message and get the important information from it
def httpRead(requestMsg):
    # Breaking up the request message string into lines
    httpParts = requestMsg.split()

    # If it is not a GET message, we quit with an exit code
    if (httpParts[0] != "GET"):
        sys.exit(101)

    # Get the path line from the GET message
    path = httpParts[1]
    # Get the specific filename
    filename = path[1:]

    # Run our file search function on the name an return the results
    return fileSearch(filename)

# Function to find the given file in the current directory
def fileSearch(filename):
	# Populating a list of all the files in the current directory
    # Borrowed from: https://stackoverflow.com/questions/11968976/list-files-only-in-the-current-directory
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    # Running the loop over all the files we found
    for f in files:
    	# Checking if the current file matches the one we are looking for
        if (f == filename):
        	# Checking if the file is .html or .htm
            if (f[-5:]==".html" or f[-4]==".htm"):
            	# Reading the file and copying its' contents
                fileObj = open(f, "r")
                fileContent = fileObj.read()
                # Return the file and the 200 code
                return (fileContent, 200)
            # If the file is not .html or .htm we cannot return it and send an empty string and 403 code
            else:
                return ("", 403)
    # If we get here, the file was not in the directory so we return an empty string and 404 code
    return ("", 404)

def constructResponse(data):
    # Get the file content and proper response code based on the request string
    fileContent, responseCode = httpRead(data)

    # Start building the response message
    responseAll = "HTTP/1.0 "

    # If the code was 403, update the file content and server response
    if(responseCode == 403):
        responseAll += "403 Forbidden"
        fileContent = "<h1>403 Forbidden</h1>"
    # If the code was 404, update the strings appropiately
    elif(responseCode == 404):
        responseAll += "404 Not Found"
        fileContent = "<h1>404 Not Found</h1>"
    # Otherwise the request must have been fine and we update the server message accordingly
    else:
        responseAll += "200 OK"

    # Constructing the rest of the server response message
    responseAll += "\r\n"
    responseAll += "Content-Type: text/html"
    responseAll += "\r\n"
    responseAll += "Content-Length: "
    # Using the method we found to get the correct byte length of html we are sending
    responseAll += str(utf8len(fileContent))
    responseAll += "\r\n"

    responseAll += "\r\n"
    # Appending the actual payload onto the response message
    responseAll += fileContent
    # At this point we have the full response constructed

    # Printing response on server side for debugging
    # print(responseAll)

    return responseAll

# Checking if the input is of the right form
if len(sys.argv) != 2:
    sys.exit(-1)

# Not specifying a host lets us listen on all available IPs
HOST = ""
# Storing the requested port
portRequested = int(sys.argv[1])

# Basic server adapted from https://realpython.com/python-sockets/#echo-server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((HOST, portRequested))
s.setblocking(False)
s.listen(5)

inbounds = [s]
outbounds= [ ]

message_queues = {}

while True:
    while inbounds:
        readable, writable, exceptional = select.select(inbounds, outbounds, inbounds)

        for socket in readable:
            if socket is s:
                conn, addr = s.accept()
                print('Connected by ', addr)
                conn.setblocking(False)
                inbounds.append(conn)

                message_queues[conn] = Queue.Queue()

            else:
                data = socket.recv(1024)
                if data:
                    response = constructResponse(data)
                    message_queues[socket].put(response)
                    if socket not in outbounds:
                        outbounds.append(socket)
                    else:
                        print("closing socket", addr)
                        if socket in outbounds:
                            outbounds.remove(socket)
                        inbounds.remove(socket)
                        socket.close()
                        del message_queues[socket]

        for socket in writable:
            try:
                next_msg = message_queues[socket].get_nowait()
                print next_msg
            except Queue.Empty:
                # no messages need to be sent down this socket
                outbounds.remove(socket)
            else:
                totalSent = 0
                while totalSent < len(next_msg):
                    # https://stackoverflow.com/questions/38419606/socket-error-errno-11-resource-temporarily-unavailable-appears-randomly
                    try:
                        this_sent = socket.send(next_msg[totalSent:])
                    except IOError as e:
                        if e.errno == errno.EWOULDBLOCK:
                            pass

                    if(this_sent == 0):
                        print("something went wrong with the socket")
                    totalSent = totalSent + this_sent

        for socket in exceptional:
            outbounds.remove(socket)
            if(socket in outbounds):
                outbounds.remove(socket)

            socket.close()
            del message_queues[socket]

s.close()
