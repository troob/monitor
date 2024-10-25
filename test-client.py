# test client
# the client sends messages to the server
# so the server can take action to handle the event
# so the monitor is the client
# problem is monitor needs to listen for
# external device IPs which it cannot bc it is busy monitoring
# instead try to make monitor server and client will

import socket

# client ip is main so it is known
# need to start off server as client so it can send its ip
# and then become server with known ip
# NEED main monitor device to be server bc single known ip

host = 'localhost' #'10.0.1.97' # The server's hostname or IP address (localhost or device ip)
port = 9988 # The port used by the server

# Client Fcn
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    s.connect((host, port)) # connect to the url domain or ip
    
    # tell server ready to receive new picks
    client_data = ''
    while client_data != 'exit':
        client_data = input(' -> ').decode() # get input
        print('Send client_data: ' + str(client_data.decode()))

        s.sendall(client_data) # send message client ready

        server_data = s.recv(1024).decode() # get response from server with new pick
        print('Received server_data: ' + str(server_data))