#!/usr/bin/python
# coding=utf-8

from scapy.all import *
import sys

def main():
	dst_host = sys.argv[1]
	current_ttl=1
	hop_list = []
	hops_limit=30
	host_reached = False
	while not(host_reached) or current_ttl>hops_limit:
		#enviando paquete ICMP con ttl incremental en la iteracion actual
		answered, unanswered = sr(IP(dst=dst_host, ttl=current_ttl)/ICMP())
		
		#viendo si el tipo de respuesta es ICMP echo reply
		if answered.res[0][1].type == 0:#echo reply
			host_reached = True
		elif answered.res[0][1].type == 11:#time exceeded
			#time exceeded, entonces guardo el hop intermedio e incremento el ttl para la proxima iteracion.
			hop_list.append(answered.res[0][1].src)
		else:
			#hop desconocido
			hop_list.append("*")
		
		#incremento el ttl para la proxima iteracion
		current_ttl +=1
	
	#imprimimos la lista de hops
	hop_index = 1
	for hop in hop_list:
		print hop_index, " " + hop
		hop_index+=1

if __name__ == "__main__":
	main()