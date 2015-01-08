# -*- coding: utf-8 -*-
__author__ = "Vladimir Konak"
#__name__ = '__main__'


import socket, sys, time

from  PyQt4 import QtGui
from PyQt4.QtCore import QObject, SIGNAL

from view import View
from board import Board
from controller import Controller
from SetupDialog import SetupBox

class Client(QObject):
    default_server_address = "92.113.247.161"
    default_server_port = 12345

    def __init__(self):
        super(Client, self).__init__()
        self.socket = socket.socket()
        self.server_addr = "127.0.0.1"
        self.server_port = self.default_server_port

        QObject.connect(self, SIGNAL("setupSucceed()"),self.connectToServer)
        QObject.connect(self, SIGNAL("connected()"),self.waitingStart)

    def showSetupDialog(self):
        def takeInfo():
            global junk
            self.controllerObject.setUserPlayerName(junk.name)
            self.emit(SIGNAL("setupSucceed()"))
            del junk

        global junk
        junk = SetupBox()
        QObject.connect(junk,SIGNAL('infoGathered()'), takeInfo)
        junk.show()

    def setup(self):
        self.showSetupDialog()

    def connectToServer(self):
        #send name and save own id
        try:
            self.socket.connect((self.server_addr,self.server_port))
            print self.controllerObject.userPlayer.name, "  - sended"
            self.socket.send(self.controllerObject.userPlayer.name)

            number = self.socket.recv(2)
            number = int(number[0])
            self.controllerObject.setUserPlayerId(number)
            print number, type(number)

            self.emit(SIGNAL("connected()"))
        except:
            print "Connection failed"

    def waitingStart(self):
        #get info 'bout other players and start command
        for i in xrange(2):
            msg = self.socket.recv(40)
            print "client.waitingStart() msg = ", msg
            playerId = int(msg[0])
            odp = (playerId - self.controllerObject.userPlayer.id+3)%3
            playerName = msg[1::]
            self.controllerObject.setRemotePlayerId(odp,playerId)
            self.controllerObject.setRemotePlayerName(odp,playerName)
        #get info bout active player
        msg = self.socket.recv(2)
        activePlayer = int( msg [0])
        self.controllerObject.activePlayer = self.controllerObject.getPlayerById(activePlayer)
        print "client.waitingStart() active player = ", self.controllerObject.activePlayer.id
        self.container.update()

    def main(self):

        app = QtGui.QApplication(sys.argv)


        self.container = View()
        self.boardInstance = Board()

        self.container.bindWith(self.boardInstance)
        self.controllerObject = Controller(self.boardInstance)
        self.container.bindWithController(self.controllerObject)

        QObject.connect(self.controllerObject,SIGNAL("changed()"),self.container.update)

        self.container.show()

        self.setup()

        sys.exit(app.exec_())

if __name__ == '__main__':
    program = Client()
    program.main()