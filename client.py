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
        self.server_addr = "localhost"
        self.server_port = self.default_server_port


    def showSetupDialog(self):
        def takeInfo():
            global junk
            self.controllerObject.setUserPlayerName = junk.name
            del junk

        global junk
        junk = SetupBox()
        QObject.connect(junk,SIGNAL('infoGathered()'), takeInfo)
        junk.show()

    def setup(self):
        self.showSetupDialog()

    def connectToServer(self):
        #send name and save own id
        self.socket.connect((self.server_addr,self.server_port))
        self.socket.send(self.controllerObject.userPlayer.name)
        pass

    def waitingStart(self):

        #get info 'bout other players and start command
        pass

    def main(self):

        app = QtGui.QApplication(sys.argv)


        self.container = View()
        self.boardInstance = Board()
        self.container.bindWith(self.boardInstance)

        self.controllerObject = Controller(self.boardInstance)

        QObject.connect(self.controllerObject,SIGNAL("changed()"),self.container.update)

        self.container.show()

        self.setup()

        sys.exit(app.exec_())

if __name__ == '__main__':
    program = Client()
    program.main()