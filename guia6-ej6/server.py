import socket
s=socket.socket()
s.bind((socket.gethostname(), 4444))

s.listen(5)
(clientsocket, address) = s.accept()
