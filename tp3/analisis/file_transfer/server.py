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
        self.incoming_filename = 'dwight.jpg'
        self.outgoing_filename = 'thunder.jpg'

    def set_delay(self):
        protocol.ACK_delay = 0.0

    def set_chance(self):
        protocol.ACK_chance = 0.95          
        
    def _connect_socket(self, sock):
        sock.bind((self.server_ip, self.server_port))
        sock.listen()
        sock.accept(timeout=10)

if __name__ == '__main__':
    FileTransferServer().run()