# -*- coding: utf-8 -*-

##########################################################
#                 Trabajo Práctico 3                     #
#         Programación de protocolos end-to-end          #
#                                                        # 
#              Teoría de las Comunicaciones              #
#                       FCEN - UBA                       #
#              Segundo cuatrimestre de 2014              #
##########################################################


from base import *
import sys

class FileTransferClient(FileTransferBase):

    def __init__(self):
        FileTransferBase.__init__(self)
        self.outgoing_filename = 'thunder.jpg'

    def _connect_socket(self, sock):
        sock.connect((self.server_ip, self.server_port), timeout=10)

    def run(self, alpha, beta):
        to_send = open(self.outgoing_filename).read()
        with Socket(alpha, beta) as sock:
            # La conexión del socket queda definida por cada subclase.
            # El cliente se conecta activamente mientras que el servidor se
            # ligará a una dirección determinada y escuchará allí.
            self._connect_socket(sock)
            i = 0
            # Para recibir el archivo, iterar hasta que el tamaño deseado
            # queda totalmente cubierto.
            while i < len(to_send):
                # Siendo PTC un protocolo full-duplex, al mismo tiempo también
                # podemos mandar datos a nuestro interlocutor.
                sock.send(to_send[i:i+self.CHUNK_SIZE])
                i += self.CHUNK_SIZE

        
if __name__ == '__main__':
    #parametros 1 y 2 son ip y puerto servidor!!
#    print "Ip Dst:", sys.argv[1], "Port Dst:", sys.argv[2]
    delay_param = float(sys.argv[3])
    pError_param = float(sys.argv[4])    
    alpha_param = float(sys.argv[5])
    beta_param = float(sys.argv[6])    
#    print "Delay:", delay_param, "Probabilidad Error:", pError_param, "ALPHA:", alpha_param, "BETA:", beta_param
    print delay_param, pError_param, alpha_param, beta_param

    fileTransfer = FileTransferClient()
    fileTransfer.set_delay(delay_param)
    fileTransfer.set_chance(1-pError_param)
#    print "RTT", "¦", "RTO"
    fileTransfer.run(alpha_param, beta_param)
    print protocol.retr
