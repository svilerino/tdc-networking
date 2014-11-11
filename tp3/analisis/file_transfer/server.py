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


class FileTransferServer(FileTransferBase):

    def __init__(self):
        FileTransferBase.__init__(self)
        self.incoming_filename = 'yo.jpg'

    def set_delay(self):
        handler.ACK_delay = 5

    def set_chance(self):
        handler.ACK_chance = 1          
        
    def _connect_socket(self, sock):
        sock.bind((self.server_ip, self.server_port))
        sock.listen()
        sock.accept(timeout=10)

    def run(self):
        expected_size = len(open(self.incoming_filename).read())
        with Socket() as sock:
            # La conexión del socket queda definida por cada subclase.
            # El cliente se conecta activamente mientras que el servidor se
            # ligará a una dirección determinada y escuchará allí.
            self._connect_socket(sock)
            # Para recibir el archivo, iterar hasta que el tamaño deseado
            # queda totalmente cubierto.
            while len(self.received_bytes) < expected_size:
                # Siendo PTC un protocolo full-duplex, al mismo tiempo también
                # podemos mandar datos a nuestro interlocutor.
                chunk = sock.recv(self.CHUNK_SIZE)
                self.received_bytes += chunk
        self._write_file()        

if __name__ == '__main__':
    FileTransferServer().run()