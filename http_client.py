# http_client.py written by Leo Ji (ljd753) and Lukas J. Gladic (ljg766)
# for EECS 340 Project 1 Winter 2019 with Professor Yan Chen

import sys
import socket
from urlparse import urlparse


# Checking if the input is of the right form
if len(sys.argv) != 2:
    sys.exit(-1)

#Storing the inputed URL.
enteredUrl = sys.argv[1]

# Making sure that the first 7 characters of the URL are "http://"
if(enteredUrl[0:7] != 'http://'):
    print("Does not start with HTTP://")
    sys.exit(500)

# Main function, does most of the assignment
# enteredURL is the URL that was entered by the user
# counter keeps track of how many redirects we have gone through
def accessRequest(enteredUrl, counter):

    # Checks number of redirects, and returns if it is 10 or more
    if (counter > 9):
        print("Reached 10 redirects, exiting")
        return ("", 10)

	# Parsing through the URL input using the URLparse library.
    exitCode = 0
    o = urlparse(enteredUrl)

    # Checks if there is a colon in the parsed URL, and splits the string at the colon
    hostTemp = o.netloc.split(":")
    # If there was no split, use default port 80
    if(len(hostTemp) == 1):
        host = (hostTemp[0], 80)
    # If there was one split, save the port that was typed in
    elif(len(hostTemp) == 2):
        host = (hostTemp[0], hostTemp[1])
    # If there were multipe splits, there is something wrong with the URL
    else:
        print("Entered URL and ports are nonsensical")
        sys.exit(102)

    # Building the GET message
    httpMsg = "GET "

    # Checking if the URL is of the secure variety, and exiting if so
    if(o.scheme == 'https'):
        print ("Attempted to HTTPS")
        sys.exit(403)

    # If a path was not specified, just add a '/' to the message
    if (o.path==""):
        httpMsg += "/"
    # If there was a path, add that to the message instead
    else:
        httpMsg += o.path

    # Finishing the first line of the GET message
    httpMsg += " HTTP/1.0"
    httpMsg += "\r\n"

    # Handles Host: header
    httpMsg += "Host: "
    httpMsg += host[0]
    # If the port isn't the default Port 80, specify the port in the message
    if(host[1] != 80):
        httpMsg += ":"
        httpMsg += host[1]
    # End the message appropiately
    httpMsg += "\r\n\r\n"

    # Creating the socket object using the Python Socket library
    socketObj = socket.create_connection(host)

    # Sending the message using the socket we created
    socketObj.sendall(httpMsg)

    # Intializing the variable to hold the return message
    msgReturn = ""

    # Manages responses > 1024 bytes
    # Borrowed from https://docs.python.org/2/library/socket.html
    while True:
        data = socketObj.recv(1024)
        if not data: break
        msgReturn += data
	# At this point, we have the full HTTP response

    # Splitting the return message up into lines
    firstLine = msgReturn.splitlines()[0]
    # Intializing the newURL varaible
    newUrl = ""

    # The response code is in the same place for every message, so we grab the numerical code
    # We cast it to an int so we can compare it to other numbers
    responseCode = int(firstLine[9:12])

    # Checking if the code is either a temporary or permanent redirect
    if (responseCode == 301 or responseCode == 302):
    	# Check each line in the response for a location line
        for line in msgReturn.splitlines():
            # Store the location of the location text
            loc = line.find("Location: ")
            # If 'Location: ' was in the given line, the response will not be -1
            if (loc != -1):
                # Update newURL with the new URL and break out of the loop
                newUrl = line[10:]
                break

    # If the response code is a 400 code, exit the program with that as the exit code
    if (responseCode >= 400 and responseCode < 500):
        exitCode = responseCode

    # Check if the content type line says text/html
    contentType = msgReturn.find("Content-Type: text/html")
    # If the type is not text/html exit with an error code
    if(contentType == -1):
        print("Returned type is not text/html")
        sys.exit(101)

    # Close the connection
    socketObj.close()

    # If there is a new URL, print a message
    # Attempt to access the new URL and increase the redirect counter by 1
    if(newUrl):
        print("Redirected to: " + newUrl)
        (msgReturn, exitCode) = accessRequest(newUrl, counter + 1)

    # We return the message recieved and exit code
    return (msgReturn, exitCode)

# Actually run the main function using the entered URL and a counter of 0
(msgReturn, exitCode) = accessRequest(enteredUrl , 0)

# Returning the string in a tuple changes some stuff, so we have to decode it,
# and then we print the message to screen.
# Taken from https://stackoverflow.com/questions/4020539/process-escape-sequences-in-a-string-in-python
print(str(msgReturn).decode('string_escape'))

# If the exit code was covered by any of our checks, exit using that code
if (int(exitCode) > 0):
    sys.exit(exitCode)

# If we get here it means we eventually got a 200 OK and we exit with code 0
sys.exit(0)
