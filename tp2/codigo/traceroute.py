#!/usr/bin/python
# coding=utf-8
from scapy.all import *
from time import *
from ruta import Ruta
import sys

#constantes
hops_limit=30
timeout_constant=2
zscore_threshold=0.5

def trace(dst_host):	
	ruta=Ruta(dst_host, hops_limit, zscore_threshold)
	current_ttl=1
	host_reached = False
	
	print "----------------------------------------------------------------------"
	while not(host_reached) and current_ttl<=hops_limit:
		#enviando paquete ICMP con ttl incremental en la iteracion actual
		print "TTL: " + str(current_ttl)
		packet=IP(dst=dst_host, ttl=current_ttl)/ICMP()
		answered, unanswered = sr(packet, timeout = timeout_constant, verbose = 0)

		#print "Paquetes contestados recibidos: " + str(len(answered))
		if len(answered) > 0:#verifico que no haya habido timeout, es decir que haya respuesta
			#armo variables para ambos paquetes, el enviado y el recibido con este ttl
			snd=answered.res[0][0]
			rcv=answered.res[0][1]

			#calculo el rtt acumulado(de origen a current_ttl saltos a lo sumo) usando los tiempos de envio 
			#y recepcion de los paquetes
			rtt_time  = 1000 * (rcv.time - snd.sent_time)
			print "Rtt de este request: " + str(round(rtt_time, 2))
			print "Respuesta obtenida de tipo: " + str(rcv.type)

			#chequeo el tipo de paquete recibido
			if rcv.type == 0:#echo reply
				ruta.add_hop(rcv.src, round(rtt_time, 2), "Echo reply")
				host_reached = True
			elif rcv.type == 11:#time exceeded
				#time exceeded, entonces guardo el hop intermedio e incremento el ttl para la proxima iteracion.
				ruta.add_hop(rcv.src, round(rtt_time, 2), "Time exceeded")
			else:
				#respuesta de tipo desconocido => hop desconocido
				ruta.add_hop("*", round(rtt_time, 2), "	" + str(rcv.type))
		else:			
			#no llego respuesta
			print "Se agotaron los " + str(timeout_constant) + " segundos para este pedido."
			#hop desconocido
			ruta.add_hop("\t*", "*", "\t*")

		#incremento el ttl para la proxima iteracion
		current_ttl+=1		
		print "----------------------------------------------------------------------"		
	#calculamos estadisticas y zcores
	ruta.make_statistics()
	return ruta

if __name__ == "__main__":
	dst_host = sys.argv[1]
	ruta = trace(dst_host)	
	ruta.display_trace()
	ruta.plot_map()