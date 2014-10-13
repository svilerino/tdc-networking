#!/usr/bin/python
# coding=utf-8
from scapy.all import *
from time import *
import sys

def main():
	dst_host = sys.argv[1]
	current_ttl=1
	hop_list = []
	hop_rtt = []
	hop_response = []
	hops_limit=30
	timeout_constant=3
	host_reached = False
	
	print "----------------------------------------------------------------------"
	while not(host_reached) and current_ttl<hops_limit:
		#enviando paquete ICMP con ttl incremental en la iteracion actual
		print "TTL: " + str(current_ttl)
		packet=IP(dst=dst_host, ttl=current_ttl)/ICMP()
		time_start = time()
		answered, unanswered = sr(packet, timeout = timeout_constant, verbose = 0)
		time_end = time()
		rtt_time = time_end-time_start
		#print "Rtt for this packet: " + str(round(rtt_time, 2))

		if len(answered) > 0:
			#viendo si el tipo de respuesta es ICMP echo reply
			print "Respuesta obtenida de tipo: " + str(answered.res[0][1].type)
			if answered.res[0][1].type == 0:#echo reply
				hop_list.append(answered.res[0][1].src)
				hop_rtt.append(round(rtt_time, 2))
				hop_response.append("	Echo reply")
				host_reached = True
			elif answered.res[0][1].type == 11:#time exceeded
				#time exceeded, entonces guardo el hop intermedio e incremento el ttl para la proxima iteracion.
				hop_list.append(answered.res[0][1].src)
				hop_rtt.append(round(rtt_time, 2))
				hop_response.append("	Time exceeded")
			else:
				#respuesta de tipo desconocido => hop desconocido
				hop_list.append("*")
				hop_rtt.append(round(rtt_time, 2))
				hop_response.append("	" + str(answered.res[0][1].type))
		else:			
			#no llego respuesta
			print "Se agotaron los " + str(timeout_constant) + " segundos para este pedido."
			#hop desconocido
			hop_list.append("*")
			hop_rtt.append("	Timeout")
			hop_response.append("Timeout")
		
		#incremento el ttl para la proxima iteracion
		current_ttl +=1		
		print "----------------------------------------------------------------------"		
	
	#imprimimos la lista de hops
	print "Traceroute a " + str(dst_host) + " (max " + str(hops_limit) + " hops)"
	print "Hop#		Hop IP 			HOP RTT 		HOP RESPONSE"
	hop_index = 1
	for hop in hop_list:
		print str(hop_index) + "		" + str(hop) + "		" + str(hop_rtt[hop_index-1]) + " 		" + str(hop_response[hop_index-1])
		hop_index+=1

if __name__ == "__main__":
	main()