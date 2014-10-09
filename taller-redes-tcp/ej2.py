import socket

for i in xrange(1, 65536):
	try:
		if socket.getservbyname(socket.getservbyport(i)) != i :
			print socket.getservbyport(i)
	except:
		pass
