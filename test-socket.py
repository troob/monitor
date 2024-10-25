# test sockets
# communicate bt computers via internet

import socket

# How to READ a webpage from a server:
# Create an INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# now connect to the web server on port 80 - the normal http port
url = 'www.python.org'
s.connect((url, 80))

# How to SERVE a webpage to a client:
# First, create a server socket:
# Create an INET, STREAMing socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a well known port
serversocket.bind((socket.gethostname(), 80)) # make public
# become a server socket
serversocket.listen(5) # queue request max 5
# now server socket is listening on port 80

while True:
    # accept connections from outside
    (clientsocket, address) = serversocket.accept()
    # now do something with the clientsocket
    # in this case, pretend this is a threaded server
    ct = client_thread(clientsocket)
    ct.run()

# Must specify when request connection ends

# If do not want to end connection, fixed length message
