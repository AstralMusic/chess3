# -*- coding: utf-8 -*-
__author__ = "Vladimir Konak"
__name__ = '__main__'

import socket, sys, time

from  PyQt4 import QtGui
from PyQt4.QtCore import QObject, SIGNAL

class Client:
    def __init__(self, sock, addr):
        self.socket = sock
        self.address = addr

    def __call__(self, *args, **kwargs):
        return self.socket


class Server(QObject):
    default_server_address = "92.113.247.161"
    default_server_port = 12345
    def __init__(self):
        super(Server, self).__init__()
        self.address = "localhost"
        self.port = self.default_server_port

    def waitingClients(self):
        listener = socket.socket()
        #for tests assume as localhost
        listener.bind(('',self.port))
        print "test1"
        listener.listen(1)
        print "test2"
        sock, addr = listener.accept()
        print "connected: ", addr
        self.Client1 = Client(sock,addr)
        print "connected: ", self.Client1.address
        name = self.Client1.socket.recv(1024)
        print name
        self.Client1.socket.close()

    def bindClientsWithPlayers(self):
        pass

    def main(self):
        print "is main started?"
        self.waitingClients()


program = Server()
program.main()