# -*- coding: utf-8 -*-
__author__ = "Vladimir Konak"
#__name__ = '__main__'


import socket, sys, time, threading

from  PyQt4 import QtGui
from PyQt4.QtCore import QObject, QString, SIGNAL

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

        #thread for listening server
        self.idleEvent = threading.Event()
        #connect signals and slots
        QObject.connect(self, SIGNAL("setupSucceed()"),self.connectToServer)
        QObject.connect(self, SIGNAL("newTurn"),self.play)
        QObject.connect(self, SIGNAL("otherUserFinishedTurn"),self.handleOutsideChangeTurn)
        QObject.connect(self, SIGNAL("end_the_game"),self.gameEnded)

    def showSetupDialog(self):
        def takeInfo():
            self.controllerObject.setUserPlayerName(junk.name)
            self.emit(SIGNAL("setupSucceed()"))

        global junk
        junk = SetupBox()
        QObject.connect(junk,SIGNAL('infoGathered()'), takeInfo)
        junk.show()

    def setup(self):
        self.showSetupDialog()

    def connectToServer(self):
        #send name and save own id
        try:
            resCode = self.socket.connect_ex((self.server_addr,self.server_port))
            if resCode: raise BaseException, "Could not connect to server"

            print self.controllerObject.userPlayer.name, "  - sended"
            self.socket.send(self.controllerObject.userPlayer.name)

            number = self.socket.recv(2)
            number = int(number[0])
            self.controllerObject.setUserPlayerId(number)
            print "recieved id = ", number
            waiting = threading.Thread(target=self.waitingStart)
            waiting.start()

            #AWB - animating "waiting box"
            def AWB():
                from time import sleep
                i = 0
                text = "Waiting for others"
                try:
                    while junk:
                        i += 1
                        junk.label2.setText(QString(str(text + "."*((i + 1)%6 + 1))))
                        sleep(0.3)
                except:
                    pass
            animate = threading.Thread(target=AWB)
            animate.start()


        except BaseException, e:
            print "Connection failed. %s" % str(e[0])
            global junk
            del junk
            self.container.close()

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

        global junk
        junk.close()
        del junk

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
                self.emit(SIGNAL("otherUserFinishedTurn"))
            elif "game_ended" in idle:
                #self.emit(SIGNAL("end_the_game"))
                self.app.closeAllWindows()

    def play(self):
        if self.controllerObject.activePlayer !=self.controllerObject.userPlayer:
            print "THAT'S NOT MY TURN NOW"
            idle = threading.Thread(target=self.waitOtherUserAction)
            idle.start()
            print "Idle thread started"
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
        print "Want to move remotely {0} -> {1}".format(newCoords[0:3], newCoords[3:6])
        src = self.boardInstance.getData(newCoords[0:3])
        dst = self.boardInstance.getData(newCoords[3:6])
        self.controllerObject.move(src, dst)

    def gameEnded(self):
        print "Game ended"
        self.app.closeAllWindows()

    def main(self):
        self.app = QtGui.QApplication(sys.argv)
        self.container = View()
        self.boardInstance = Board()

        self.container.bindWith(self.boardInstance)
        self.controllerObject = Controller(self.boardInstance)
        QObject.connect(self.controllerObject, SIGNAL("turnEndedByUser"),self.handleInsideChangeTurn)
        QObject.connect(self.controllerObject, SIGNAL("changed()"),self.container.update)

        self.container.bindWithController(self.controllerObject)
        self.container.show()
        self.setup()

        sys.exit(self.app.exec_())

if __name__ == '__main__':
    program = Client()
    program.main()