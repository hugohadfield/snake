from socket import *
import threading
import time
import signal

nplayers = 0
MAXPLAYERS = 2

lock = Lock()

BUFF = 1024
HOST = '127.0.0.1'# must be input parameter @TODO
PORT = 8000 # must be input parameter @TODO
ALIVE = True

def response(key):
    return 'Server response: ' + key

def connectionhandler(clientsock,addr,currentportnumber):
    print "sending new port to client"
    clientsock.send(str(currentportnumber))
    while 1:
        clientsock.send(str(currentportnumber))
        data = clientsock.recv(BUFF)
        if not data: break
    clientsock.close()
    print addr, "- closed connection" #log on console


def playerhandler(clientsock,addr):
    while ALIVE:
        # Send the latest global state
        data = clientsock.recv(BUFF)
        if not data: break
        print repr(addr) + ' recv:' + repr(data)
        clientsock.send(response(data))
        print repr(addr) + ' sent:' + repr(response(data))
        if "close" == data.rstrip(): break # type 'close' on client console to close connection from the server side
    clientsock.close()
    print addr, "- closed connection" #log on console


if __name__=='__main__':
    connectionADDR = (HOST, PORT)
    serversock = socket(AF_INET, SOCK_STREAM)
    serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversock.bind(connectionADDR)
    serversock.listen(5)
    connectionthreads = []
    playerthreads = []
    playerADDR = []

    # This section accepts connections from a few players and reassigns them ports
    while 1:
        if nplayers >= MAXPLAYERS:
            break
        # Wait for a client to connect to the main port
        serversock = socket(AF_INET, SOCK_STREAM)
        serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serversock.bind(connectionADDR)
        serversock.listen(5)
        print 'waiting for connection... listening on port', PORT
        clientsock, addr = serversock.accept()
        print '...connected from:', addr
        nplayers = nplayers + 1
        currentportnumber = PORT + nplayers
        print "creating a thread to reassign port to: ", str(currentportnumber)
        connectionthreads.append(threading.Thread(target = connectionhandler, args = (clientsock, addr, currentportnumber)))
        connectionthreads[nplayers-1].start()

        # Create a definition of the new socket that the client should connect to. start listening
        playerADDR.append((HOST, currentportnumber))
        serversock = socket(AF_INET, SOCK_STREAM)
        serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        serversock.bind(playerADDR[nplayers-1])
        serversock.listen(5)
        print 'waiting for connection... listening on port', currentportnumber
        clientsock, addr = serversock.accept()
        print '...connected from:', addr
        # spawn a new thread to deal with each player
        playerthreads.append(threading.Thread(target = playerhandler, args = (clientsock, addr)))
        playerthreads[nplayers-1].start()

    # By this point all the players should have connected and been assigned 
    # their own port and a seperate thread should be serving them all
    # ensure all the connection threads are destroyed
    for t in connectionthreads:
        t.join()

    # Here is the main game loop, this will run as long as the game is still 
    # running and everyone is still connected
    while ALIVE:
        active_players = threading.active_count() - 1 # minus one as the main thread counts
        print active_players
        if active_players < MAXPLAYERS:
            ALIVE = False

        # This is where the game should be called to update state
        time.sleep(1)


    # All of the threads should see the ALIVE flag shift when a player exits and so should exit
    # Wait for exit of all threads
    for t in playerthreads:
        t.join()

        









