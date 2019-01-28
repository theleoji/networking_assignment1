# http_server2.py written by Leo Ji (ljd753) and Lukas J. Gladic (ljg766)
# for EECS 340 Project 1 Winter 2019 with Professor Yan Chen

import sys
import socket
import os
import select
import Queue
import errno


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

# Our response message from http_server1.py made into a function
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
    # ------ At this point we have the full response constructed ------

    # Return the response we created
    return responseAll

# Checking if the input is of the right form
if len(sys.argv) != 2:
    sys.exit(-1)

# Not specifying a host lets us listen on all available IPs
HOST = ""
# Storing the requested port
portRequested = int(sys.argv[1])

# Basic server adapted from https://realpython.com/python-sockets/#echo-server
# Multiconnection server insight and framework adapted from: https://pymotw.com/2/select/
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Almost the same as the previous server, we just set blocking to false to allow multiple connections
s.bind((HOST, portRequested))
s.setblocking(False)
s.listen(5)

# Starting our inbounds and outbounds lists
inbounds = [s]
outbounds= [ ]

# Starting our message queue
message_queues = {}

# Keep the server running until we kill the process
while True:
    # Run this while our inbound list exists
    while inbounds:
        # Storing our inbounds and outbounds after they go through the selector
        readable, writable, exceptional = select.select(inbounds, outbounds, inbounds)

        # For each socket that we are reading from
        for socket in readable:
            # Check if the connection is attempting to connect on the main socket
            if socket is s:
                # Accept the connection and store the sender information
                conn, addr = s.accept()
                # Print our connection message
                print('Connected by ', addr)
                # Make sure the connection is not blocking so we can still accept other connections
                conn.setblocking(False)
                # Add this connetion to the inbounds list
                inbounds.append(conn)

                # Creating a new queue with the message
                message_queues[conn] = Queue.Queue()

            # If the socket is not the main socket, we can do stuff with it
            else:
                # Storing the recieved request
                data = socket.recv(1024)
                # Check if we actually receive something
                if data:
                    # Construct the appropiate response using our functions defined above
                    response = constructResponse(data)
                    # Add our response to the message queues for that socket
                    message_queues[socket].put(response)
                    # Check if our socket is on the outbounds lists
                    if socket not in outbounds:
                        # If it is not, add it to the list
                        outbounds.append(socket)
                    else:
                        # If it is in outbounds, print a closing message
                        print("closing socket", addr)
                        if socket in outbounds:
                            # If it is still in outbounds, we remove the socket from the list
                            outbounds.remove(socket)
                        # Remove the socket from the inbounds list
                        inbounds.remove(socket)
                        # Close the socket
                        socket.close()
                        # Remove the message from the message queue list
                        del message_queues[socket]

        # For each socket that we can send stuff through
        for socket in writable:
            # Try to get a message from the message queue for this socket
            try:
                # Store the message
                next_msg = message_queues[socket].get_nowait()
            # If we get an empty queue exception, handle it
            except Queue.Empty:
                # no messages need to be sent down this socket, so we remove it
                outbounds.remove(socket)
            # If there is no exception, keep going
            else:
                # We were having issues where the whole message payload was not being sent so we found a solution where we
                # track how much we have sent serverside and keep sending until we reach the expected message length
                # Adapted from: https://docs.python.org/2/howto/sockets.html?fbclid=IwAR2hl179EyV3Rp6lT2kH1mi5_IVKjvAhY-O_aOnZJ4cNo_ShFGLPt3jWZMY#socket-howto

                # Initialize the length variable
                totalSent = 0
                # While the total amount sent is less than the whole mmessage, keep doing
                while totalSent < len(next_msg):
                    # Another issue came up for where we got blocking errors because the server kept checking for another response before
                    # there was one, so we just made sure that exception was passed
                    # Borrowed from: https://stackoverflow.com/questions/38419606/socket-error-errno-11-resource-temporarily-unavailable-appears-randomly
                    
                    # Try sending the response message
                    try:
                        # Store what we just sent
                        this_sent = socket.send(next_msg[totalSent:])
                    # If we get the block exception we kept encountering, just ignore it and let it pass
                    except IOError as e:
                        if e.errno == errno.EWOULDBLOCK:
                            pass

                    # If for some reason nothing is sent through the socket, something broke that we have no control over
                    if(this_sent == 0):
                        print("something went wrong with the socket")
                    # Update the total amount of information that we have sent
                    totalSent = totalSent + this_sent

        # For each socket that gave us an exception
        for socket in exceptional:
            # Remove it from the inbounds list
            outbounds.remove(socket)
            # If it made it to the outbounds list, remove it from there too
            if(socket in outbounds):
                outbounds.remove(socket)

            # Close the socket of the connection withan exception
            socket.close()
            # Delete the messages from it from our message queue
            del message_queues[socket]

# If we somehow break out of the loop that is the whole server, close the main socket
s.close()
