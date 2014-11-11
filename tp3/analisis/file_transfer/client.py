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

class FileTransferClient(FileTransferBase):

    def __init__(self):
        FileTransferBase.__init__(self)
        self.outgoing_filename = 'dwight.jpg'
        
    def _connect_socket(self, sock):
        sock.connect((self.server_ip, self.server_port), timeout=10)

    def run(self):
        to_send = open(self.outgoing_filename).read()
        with Socket() as sock:
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
    FileTransferClient().run()