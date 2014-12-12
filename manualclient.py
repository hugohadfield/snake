import socket
import time
import msvcrt

import numpy as np
import matplotlib.pyplot as plt

import cPickle as pickle


# Initial socket settings
TCP_IP = '127.0.0.1'
TCP_PORT = 8000
BUFFER_SIZE = 1024

# Connects, is assigned a new port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
PLAYER_PORT = int(s.recv(BUFFER_SIZE))
print "received port:", PLAYER_PORT
s.close()

# Connects to the new port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
playernumber = PLAYER_PORT - TCP_PORT
s.connect((TCP_IP, PLAYER_PORT))

# The game loop
while 1:

  # Get the global state
  data = s.recv(BUFFER_SIZE)

  # Unpickle it
  gamestate = pickle.loads(data)

  # Print what we recieve
  print gamestate

  # Plot the two snakes
  snake1 =  gamestate[0]
  snake2 =  gamestate[1]

  # Process it to create a next move
  # In this case manual control

  # Try to flush the buffer
  while msvcrt.kbhit():
    msvcrt.getch()
  move = msvcrt.getch()
  if move == 'w':
    s.send(str(0))
  elif move == 's':
    s.send(str(1))
  elif move == 'a':
    s.send(str(2))
  elif move == 'd':
    s.send(str(3))


  # Get the updated global state
  data = s.recv(BUFFER_SIZE)

  # Unpickle it
  gamestate = pickle.loads(data)

  # Print what we recieve
  print gamestate

# Close the socket
s.close()
