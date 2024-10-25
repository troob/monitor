# test server
# the server is the listener
# which handles events found by the monitor
# so the monitor is the client

import socket


def my_function_that_handles_data(data):
    print('\n===Handle Data from Client===\n')
    data_str = data.decode()
    print('data_str: ' + str(data_str))

# 'localhost' #
host = '0.0.0.0' #'104.162.31.124'##'10.0.1.97' #socket.gethostbyname(socket.gethostname()) #'127.0.0.1' # router: '10.0.1.2' #computer: '10.0.1.97' # Standard loopback interface address (localhost)
port = 5001 #10000 # Port to listen on (non-privileged ports are > 1023)
print('host: ' + str(host))
# hostname = socket.gethostname()
# dns_resolved_addr = socket.gethostbyname(hostname)
# print('dns_resolved_addr: ' + str(dns_resolved_addr))

# Server Fcn
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((host, port))
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    
    s.listen(5)
    print('Server is listening...')

    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            client_data = conn.recv(1024).decode()
            if not client_data:
                break
            print("Received client_data: " + str(client_data))

            # send data back to client
            # When Monitor Detects New Pick
            server_data = input(' -> ')
            print('Send server_data: ' + str(server_data))
            conn.sendall(server_data.encode()) # send data to the client
            #my_function_that_handles_data(data)

    
