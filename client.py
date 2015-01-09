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

        QObject.connect(self, SIGNAL("newTurn"),self.play)

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

            global junk
            junk.hide()

            number = self.socket.recv(2)
            number = int(number[0])
            self.controllerObject.setUserPlayerId(number)
            print "recieved id = ", number

            self.emit(SIGNAL("connected()"))
        except:
            print "Connection failed"

    def waitingStart(self):
        #get info 'bout other players
        for i in xrange(2):
            msg = self.socket.recv(40)
            playerId = int(msg[0])
            odp = (playerId - self.controllerObject.userPlayer.id+3)%3
            playerName = msg[1::]
            self.controllerObject.setRemotePlayerId(odp,playerId)
            self.controllerObject.setRemotePlayerName(odp,playerName)
        #get info 'bout active player
        msg = self.socket.recv(2)
        activePlayer = int( msg [0])
        activePlayer = self.controllerObject.getPlayerById(activePlayer)
        self.controllerObject.setActivePlayer(activePlayer)
        #print "container updated .from waitingStart()"
        self.emit(SIGNAL("newTurn"))

    def waitOtherUserAction(self):
        self.container.update()
        if self.controllerObject.activePlayer != self.controllerObject.userPlayer:
            self.socket.setblocking(0)
            idle = None
            while not idle:
                try:
                    idle = self.socket.recv(10)
                except:
                    pass
                if idle: break
            print "Recieved '%s' from server" % idle
            self.socket.setblocking(1)
            if "turn_ended" in idle:
                self.emit(SIGNAL("turnEnded()"))
                #self.makeRemoteMove()

    def play(self):
        if self.controllerObject.activePlayer !=self.controllerObject.userPlayer:
            print "THAT'S NOT MY TURN NOW"
            self.waitOtherUserAction()
        else: print "IT IS MY TURN"

    def handleInsideChangeTurn(self):
        self.controllerObject.validSquares = []
        self.boardInstance.unselectAll()

        self.socket.send("turn_ended")
        print "Message sended to server = 'turn_ended' "
        print "Now we send to server this: ", self.controllerObject.movement
        for x in self.controllerObject.movement:
            msg = str(x)
            self.socket.send(msg)

        print "Turn ended"
        x = self.controllerObject.players.index(self.controllerObject.activePlayer)
        self.controllerObject.activePlayer = self.controllerObject.players[(x+1)%3]

        self.container.update()
        print "New active Player: %d \n"% self.controllerObject.activePlayer.id

        self.emit(SIGNAL("newTurn"))

    def handleOutsideChangeTurn(self):
        self.makeRemoteMove()

        x = self.controllerObject.players.index(self.controllerObject.activePlayer)
        self.controllerObject.activePlayer = self.controllerObject.players[(x+1)%3]

        self.container.update()

        print "New active Player: ", self.controllerObject.activePlayer.id

        self.emit(SIGNAL("newTurn"))



    def makeRemoteMove(self):
        self.socket.setblocking(1)
        newCoords = list()
        for i in xrange(6):
            newCoord = self.socket.recv(1)
            newCoords.append(int(newCoord))
            print "from makeRemoteMove recieved:", newCoord
        print "Want to move remotely ", newCoords[0:3], " -> ", newCoords[3:6]

        src = self.boardInstance.getData(newCoords[0:3])
        dst = self.boardInstance.getData(newCoords[3:6])

        self.controllerObject.move(src, dst)


        #self.controllerObject.emit(SIGNAL("turnEnded()"))

    def main(self):
        self.container = View()
        self.boardInstance = Board()

        self.container.bindWith(self.boardInstance)
        self.controllerObject = Controller(self.boardInstance)
        QObject.connect(self.controllerObject, SIGNAL("turnEndedByUser"),self.handleInsideChangeTurn)
        QObject.connect(self, SIGNAL("turnEnded()"),self.handleOutsideChangeTurn)


        ## QObject.connect(self.controllerObject, SIGNAL("turnEnded()"),self.container.update)

        self.container.bindWithController(self.controllerObject)

        QObject.connect(self.controllerObject,SIGNAL("changed()"),self.container.update)

        self.container.show()

        self.setup()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    program = Client()
    program.main()
    sys.exit(app.exec_())