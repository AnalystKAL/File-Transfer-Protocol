"""
Name: KAL

Python version: 2.7
Tested on PyCharm and Command Prompt
Test on localhost: Success
"""
import socket
import time
import pickle
import sys

DATA_LENGTH = 4096
DATA_FORMAT = "utf-8"
#HOST = "localhost"  # for demo purposes, the server and client are on the same host
#HOST = socket.gethostname(socket.gethostbyname())
PORT = 5050


class Client:

    def __init__(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        # create a client socket that can allow connections and messages to be sent through
        # AF_INET is an address family(IPv4 addresses)
        # SOCK_STREAM creates a TCP socket. For reliability and in-sequence data
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # connect() takes server ip address and port as parameters.
        self.client_socket.connect((ip_address, port))
        self.connected = True
        # Client able to start communicating with server. Method call to handle data to and from server
        self.handle_server()


    # general method to send and receive data from server
    def handle_server(self):
        # create handshake protocol
        self.client_socket.send("Request : Client requesting connection")
        # receive server ACK
        print self.client_socket.recv(DATA_LENGTH)
        # Receive server connected if successful
        print self.client_socket.recv(DATA_LENGTH)
        # start client loop
        while self.connected:
            command = raw_input("Commands: LIST | RETR [filename] | !DISCONNECT: ")
            # command to disconnect from Server
            if command == "!DISCONNECT":
                self.client_socket.send(command)
                server_disconnection = self.client_socket.recv(DATA_LENGTH)
                print server_disconnection
                self.connected = False
                #print "Disconnecting from server..."
                time.sleep(1)
                print "Goodbye"
            # command to retrieve files from Server
            # command format is RETR [filename]
            # split the message and first segment of string is command and second segment is the filename
            elif command.split()[0] == "RETR":
                self.client_socket.send(command)
                # receive file from server
                filecontents = self.client_socket.recv(DATA_LENGTH * DATA_LENGTH) # 16MB limit
                # if file has server message instead, then display error message
                if filecontents.split()[0] == "Server":
                    print filecontents
                # else proceed to download file from server
                else:
                    self.receive_file(filecontents)
            # command to list all files available on the server
            elif command == "LIST":
                # send LIST command
                self.client_socket.send(command)
                # receive list of files from server
                getlist = self.client_socket.recv(DATA_LENGTH)
                print "_" * 20
                print "\tSERVER Files"
                print "_" * 20
                # iterate over list
                # server sent pickled data so needs to be unpickled with loads in receive_dir method
                try:
                    for line in self.receive_dir(getlist):
                        print "File Name: " + line
                    print "\n"
                except TypeError as err:
                    print "Client Error!"
                    print "More details: {}".format(err)
                    print "Resending LIST request"
                    self.client_socket.recv(DATA_LENGTH*DATA_LENGTH)
                    continue
            # catch any invalid inputs
            else:
                self.client_socket.send(command)
                # server sends invalid input error message
                print self.client_socket.recv(DATA_LENGTH)

    # method to download file for the RETR command
    def receive_file(self, filecontents):
        # use pickle to get file contents
        # file contents sent by server is in list
        # pickle allows object data send and receive

        try:
            end = len(filecontents)
            # user inputs file name that gets saved in their folder
            filename = raw_input("Enter file name for your file: ")

            # use with open for safe file writing operation
            # strip leading spaces from user input
            with open(r".\\ClientFolder\\" + filename.strip(), "wb") as f:
                #f.write(filecontents)
                #progress_bar = ""
                for index, line in enumerate(filecontents):
                    #progress_bar += "|"
                    f.write(line)
                    percents = int(float(index+1) / end * 100)
                    #sys.stdout.write("\rSequence: %d Segment: %s | writing... %d%%" % (index+1, line, percents))
                    #sys.stdout.write("\r%d%%" % percents)
                    progress_bar(index, end, percents, filename)
                    sys.stdout.flush()
            print "\nSuccessfully received file from {}".format(self.ip_address)
            self.client_socket.send("ACK : File received")
        except ValueError as e:
            print "Invalid file type. Details: {}".format(e)
        except IOError as err:
            print "Error: Client opened file while transfer\n More details: %s" % err

    # list all file names sent by server
    def receive_dir(self, directory):
        # receive list of files with pickle loads
        try:
            data = pickle.loads(directory)
            return data
        except Exception as e:
            print "Error: {}".format(e)


def progress_bar(current, total, percents, filename):
    progress_bar_length = 70
    current_progress_bar = int(round(progress_bar_length*current/float(total)))

    progress = '#' * current_progress_bar + '-' * (progress_bar_length - current_progress_bar)

    sys.stdout.write('\r[%s] %s%s ... %s' % (progress, percents, '%', filename))

    # time.sleep(0.00005)


if __name__ == '__main__':

    test_connection = True
    # Loop to let user try again if any errors
    # for example, wrong server address or name
    while test_connection:
        try:
            # Let user connect to the FTP Server
            HOST = raw_input("Please enter server IP Address: ")
            # window = tk.Tk()
            # window.withdraw()
            # HOST = tkSimpleDialog.askstring("host", "Please enter server IP address:")
            # Create client object
            client = Client(HOST, PORT)
            test_connection = False
        # handle user inputs or no server available
        except socket.gaierror as e:
            print "Error! Wrong IP Address or Server Name!\n Server might be down.\nMore details: %s \n" % e
        # handle if server goes down suddenly
        except socket.error as e:
            print "Server does not exist or Server Closed Forcibly!\nMore details: %s \n" % e
        # handle client closing using ^Z command in cmd
        except EOFError as e:
            print "Closing Forcibly"
            test_connection = False
        except TypeError as e:
            print "No ip address given\nMore details: %s" % e
