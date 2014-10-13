#!/usr/bin/python
# coding=utf-8
from scapy.all import *
from time import *
import sys

def main():
	dst_host = sys.argv[1]
	current_ttl=1
	hop_list = []
	hops_limit=30
	attempts_number=3
	timeout_constant=4
	host_reached = False

	while not(host_reached) or current_ttl>hops_limit:
		#enviando paquete ICMP con ttl incremental en la iteracion actual
		print ""
		print "--------------------------------------------------------------------------------------------------"
		print ""
		print "ttl de la iteracion actual: " + str(current_ttl)
		packet=IP(dst=dst_host, ttl=current_ttl)/ICMP()
		
		rtt_time=0
		answered_attempts=0
		for attempts in xrange(1,attempts_number):
			time_start = time()
			answered, unanswered = sr(packet, timeout = timeout_constant)
			time_end = time()
			rtt_time += time_end-time_start
			if len(answered)>0:
				answered_attempts+=1
				
		if answered_attempts >0:
			rtt_time=rtt_time/float(answered_attempts)
			print "Rtt for this packet: " + str(rtt_time)

		if len(answered) > 0:
			#viendo si el tipo de respuesta es ICMP echo reply
			#print "response type: " + str(answered.res[0][1].type)
			if answered.res[0][1].type == 0:#echo reply
				hop_list.append(answered.res[0][1].src)
				host_reached = True
			elif answered.res[0][1].type == 11:#time exceeded
				#time exceeded, entonces guardo el hop intermedio e incremento el ttl para la proxima iteracion.
				hop_list.append(answered.res[0][1].src)
			else:
				#respuesta de tipo desconocido => hop desconocido
				hop_list.append("*")
		else:			
			#no llego respuesta
			print "TIMEOUTED REQUEST - timeout=" + str(timeout_constant)
			#hop desconocido
			hop_list.append("*")
		
		#incremento el ttl para la proxima iteracion
		current_ttl +=1
	
	#imprimimos la lista de hops
	print "Traceroute to " + str(dst_host) + " (max " + str(hops_limit) + " hops)"
	hop_index = 1
	for hop in hop_list:
		print hop_index, " " + hop
		hop_index+=1

if __name__ == "__main__":
	main()