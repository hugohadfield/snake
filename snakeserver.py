
# This stuff is specific to the game you want to use
from operator import add
def goup(state,playernumber):
    state[playernumber-1][1] += 1
    return state

def godown(state,playernumber):
    state[playernumber-1][1] -= 1
    return state

def goleft(state,playernumber):
    state[playernumber-1][0] -= 1
    return state

def goright(state,playernumber):
    state[playernumber-1][0] += 1
    return state

MAXPLAYERS = 2
inputs = {
    0:goup,
    1:godown,
    2:goleft,
    3:goright,
}
gamestate = [[0,0],[10,10]]
def updategame(data, playernumber):
    global gamestate
    try:
        clientcommand = int(data)
        if clientcommand in range(0,4):
            gamestate = inputs[clientcommand](gamestate,playernumber)
    except:
        pass




# This stuff is generic for any turn based game
from socket import *
import threading
import time

BUFF = 1024
HOST = '127.0.0.1'
PORT = 8000 
ALIVE = True
PLAYING = False
turncomplete = False
nplayers = 0
turn = 0
lock = threading.Lock()

def connectionhandler(clientsock,addr,currentportnumber):
    print "sending new port to client"
    clientsock.send(str(currentportnumber))
    while 1:
        clientsock.send(str(currentportnumber))
        data = clientsock.recv(BUFF)
        if not data: break
    clientsock.close()
    print addr, "- closed connection" #log on console


def playerhandler(clientsock,addr,playernumber):

    # TODO implement a timeout on the turn to prevent overly time consuming strategies

    global turncomplete

    while ALIVE:
        while PLAYING:
            # Wait for this players turn
            if turn == playernumber and turncomplete == False:
                # Ensure this is the only thread modifying the shared resources
                lock.acquire()

                # Send the latest global state
                clientsock.send(str(gamestate))
                print repr(addr) + ' sent:' + repr(gamestate)

                # Get back a command from the client
                data = clientsock.recv(BUFF)
                if not data: break
                print repr(addr) + ' recv:' + repr(data)

                # Update the global game state according to the command
                updategame(data,playernumber)

                # Send the updated global state
                clientsock.send(str(gamestate))
                print repr(addr) + ' sent:' + repr(gamestate)

                # Signal the end of this go
                turncomplete = True

                # Let everyone else have access again
                lock.release()

    lock.release()
    clientsock.close()
    print addr, "- closed connection" #log on console


if __name__=='__main__':

    # Set up the main socket for initial connection
    connectionADDR = (HOST, PORT)
    serversock = socket(AF_INET, SOCK_STREAM)
    serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversock.bind(connectionADDR)
    serversock.listen(5)
    connectionthreads = []
    playerthreads = []
    playerADDR = []
    global turncomplete

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
        playerthreads.append(threading.Thread(target = playerhandler, args = (clientsock, addr,nplayers)))
        playerthreads[nplayers-1].start()


    # By this point all the players should have connected and been assigned 
    # their own port and a seperate thread should be serving them all
    # ensure all the connection threads are destroyed
    for t in connectionthreads:
        t.join()

    # Here is the main game loop, this will run as long as the game is still 
    # running and everyone is still connected
    PLAYING = True
    while ALIVE:
        active_players = threading.active_count() - 1 # minus one as the main thread counts
        if active_players < MAXPLAYERS:
            ALIVE = False
            PLAYING = False

        # Cycle through players turns, starting with player 1
        for turncounter in range(1,MAXPLAYERS+1):
            turn = turncounter
            lock.acquire()
            turncomplete = False
            lock.release()
            time.sleep(0.1)

        # Wait for some time step
        time.sleep(0.5)


    # All of the threads should see the ALIVE flag shift when a player exits and so should exit
    # Wait for exit of all threads
    for t in playerthreads:
        t.join()

        









