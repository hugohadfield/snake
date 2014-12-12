import socket
import time


TCP_IP = '127.0.0.1'
TCP_PORT = 8000
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
PLAYER_PORT = int(s.recv(BUFFER_SIZE))
print "received port:", PLAYER_PORT
s.close()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
playernumber = PLAYER_PORT - TCP_PORT
s.connect((TCP_IP, PLAYER_PORT))
s.send(str(playernumber))

while 1:
  # Get the global state
  data = s.recv(BUFFER_SIZE)

  # Process it to create a next move
  s.send(str(playernumber))


s.close()
