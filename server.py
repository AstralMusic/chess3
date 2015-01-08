# -*- coding: utf-8 -*-
__author__ = "Vladimir Konak"
__name__ = '__main__'

import socket, sys, time, random

from  PyQt4 import QtGui
from PyQt4.QtCore import QObject, SIGNAL

class Client:
    def __init__(self, sock, addr):
        self.socket = sock
        self.address = addr

    def setId(self, Id):
        self.id = Id

    def setName(self, name):
        self.name = name

    def inform(self, msg):
        self.socket.send(msg)

    def __call__(self, *args, **kwargs):
        return self.socket


class Server(QObject):
    default_server_address = "92.113.247.161"
    default_server_port = 12345
    def __init__(self):
        super(Server, self).__init__()
        self.address = "127.0.0.1"
        self.port = self.default_server_port

    def waitingClients(self):
        listener = socket.socket()
        self.clients = []
        #for tests assume as localhost
        listener.bind(('',self.port))
        #start listening
        listener.listen(3)
        for i in xrange(3):
            sock, addr = listener.accept()
            print "connected: ", addr

            newClient = Client(sock,addr)
            name = newClient.socket.recv(32)
            #recieved text is wierd, so we need to
            name = name[::2]
            newClient.setName(name)

            newClient.setId(i)
            newClient.inform(str(i))

            self.clients.append(newClient)
            print i, name, type(name)

        listener.close()

    def shoutStart(self):
        #tell every client info about other clients
        activePlayerId = random.randint(0,2)
        for each in self.clients:
            for client in self.clients:
                if not each == client:
                    each.inform(str(str(client.id)+client.name))
                    time.sleep(.025)
            print activePlayerId
            each.inform(str(activePlayerId))


    def bindClientsWithPlayers(self):
        pass

    def main(self):
        try:
            self.waitingClients()
        except:
            print "Connecting with clients failed"
        try:
            self.shoutStart()
        except:
            print "Bad connection"

program = Server()
program.main()