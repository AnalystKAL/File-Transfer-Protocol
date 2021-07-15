"""
Name: Krishal Arunkumar Lad

Python version: 2.7
Tested on PyCharm and Command Prompt
Test on localhost: Success
"""
import socket
import threading
import os
import pickle

SERVER_FOLDER_PATH = r".\\serverfolder" # server directory
SERVER_PORT = 5050
#SERVER_ADDRESS = "localhost"    # for demo purposes uses localhost
hostname = socket.gethostbyname_ex(socket.gethostname()) # get all available IP Addresses used by host
DATA_LENGTH = 4096
DATA_FORMAT = "utf-8"


class Server:

    def __init__(self, ip_address, port):

        self.ip_address = ip_address

        # create a server socket with IPv4 addressing and TCP socket connection
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # socket bind method accepts a tuple of ip address and port
        server_tuple = (ip_address, port)
        self.server_socket.bind(server_tuple)   # creates a socket at port for the specified ip address
        self.server_socket.listen(3)    # allows incoming connections
        self.start()    # start method is initialized

    def start(self):

        print "[{}]Server has started".format(self.ip_address)
        # create an endless loop to always accept client connection requests

        while True:
            # client_connection is a client socket object. Used to send and receive data
            # client_address is the ip address and port of the client
            client_connection, client_address = self.server_socket.accept()

            # create a new thread for each client and initialize handle_client method
            thread = threading.Thread(target=self.handle_client, args=(client_connection, client_address))

            # start this particular client thread
            thread.start()

            # shows how many clients are connected to the server
            # threading.active_count method includes server thread so we subtract one
            print "\n[Clients Connected] {}".format(threading.active_count() - 1)

    # main method to client requests
    def handle_client(self, connection, address):
        # receive client connection request - handshake protocol
        print "Client[{}] ".format(address[0]) + str(connection.recv(DATA_LENGTH))
        # send connection to client
        self.send_data(connection, "[FTP 100] ACK : Initializing Connection")
        # print on command line that a new client connected
        print "Server : [FTP 200][New Connection Established][{}]".format(address[0])

        # send connection successful to client
        self.send_data(connection, "Server : [FTP 200] You are now connected")
        connected = True

        # endless while loop to check for client commands
        # command !DISCONNECT closes connection to client and stops the loop
        while connected:
            try:
                # receive commands from client
                command = connection.recv(DATA_LENGTH)
                if command:
                    print "Client[{}]{}".format(address[0], command)

                    # command LIST sends list of file names to clients
                    if command == "LIST":
                        print "Server : [FTP 212] Directory status requested"
                        # store list of files stored in server directory
                        file_dir = os.listdir(SERVER_FOLDER_PATH)

                        # pickle the list
                        data = pickle.dumps(file_dir)

                        # send the data to client which will unpickle the data
                        self.send_data(connection, data)


                    # command RETR sends file to client
                    # command options: RETR [filename]
                    elif command.split()[0] == "RETR":  # check first word of command

                        # try loop to catch file name not given error
                        try:
                            # get file name which is the second word in the command
                            filename = command.split()[1]

                            # if filename exists in the server directory
                            if filename in os.listdir(SERVER_FOLDER_PATH):
                                # send file method that sends the file as a string
                                self.send_file(connection, address, filename)

                            # if file not found in directory send error message to client
                            else:
                                print "Server : [FTP 550] File not found"
                                self.send_data(connection, "Server : [FTP 550] File not found")

                        #catch error of client not giving filename
                        except IndexError as e:
                            # FTP 501 - parameter errors
                            print "Server : [FTP 501] File name not given!"
                            self.send_data(connection, "Server : [FTP 501] File name not given!")

                    # Allows client to disconnect from server safely
                    elif command == "!DISCONNECT":
                        print "Server : [FTP 231] Client {} logging out from server".format(address[0])
                        # User logs out
                        self.send_data(connection, "Server: [FTP 231] You requested disconnection from server")
                        print "Server : Client[{}] logged out".format(address[0])
                        # terminate connection
                        connected = False


                    # catch invalid inputs by client
                    else:
                        print "Server : [FTP 202]"
                        self.send_data(connection, "Server: Invalid command. [FTP 202] ")
            # catch sudden disconnections by client
            except:
                connection.close()
                break

    # use try and except to catch any errors in sending data
    def send_data(self, connection, data):
        try:
            connection.sendall(data)
        except:
            print "Server error: Unable to send data"

    # send file to client
    def send_file(self, connection, addr, filename):
        file_contents = ""
        # use with keyword to safely read file
        # append all lines in file to file_contents list
        with open(r".\\serverfolder\\" + filename.strip(), "rb") as f:
            file_contents = f.read() # get all file contents
        self.send_data(connection, file_contents)
        ACK = connection.recv(DATA_LENGTH)
        if ACK.split()[0] == "ACK":
            print "[ACK] received. Successfully sent " + filename + " to {}".format(addr[0])
            print "Server : [FTP 226]"


if __name__ == '__main__':
    print "-" * 80
    print "\tWelcome to FTP Server by Krishal Lad"
    print "\tlocalhost for same pc demonstration"
    print "\tPrivate IP address available by the Router"
    print "\tPublic IP Address available by the ISP/Organization"
    print "\tPublic/Private IP Address will be used for PC to PC demonstration"
    print "-" * 80
    # list with localhost by default
    available_ip_address = ["localhost"]
    # add all ip addresses available to the server host to the list
    for num in range(len(hostname[2])):
        available_ip_address.append(hostname[2][num])
    # show user all ip addresses available to create server
    print "\nAvailable IP Addresses for FTP Server"
    for index, line in enumerate(available_ip_address):
        print "IP Address:  " + line
    print ""
    test_connection = True
    # loop until a successful server has been made
    while test_connection:
        try:
            # choose server by user(just for demo purposes)
            # to test for localhost or 2 pc demo
            server_address = raw_input("Choose Server IP Address: ")
            SERVER_ADDRESS = server_address.strip()
            # create server object
            server = Server(SERVER_ADDRESS, SERVER_PORT)
            test_connection = False
        except socket.gaierror as e:
            print "Socket error: %s" % e
    


