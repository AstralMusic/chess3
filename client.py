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
            server_msg = None
            while not server_msg:
                try:
                    server_msg = self.socket.recv(10)
                except:
                    pass
                if server_msg: break
            print "Recieved '%s' from server" % server_msg
            self.socket.setblocking(1)
            if "turn_ended" in server_msg:
                self.emit(SIGNAL("otherUserFinishedTurn"))
            elif "killed" in server_msg:
                loserId = int(server_msg[7])
                self.controllerObject.players[loserId].isAlive = False
                #self.emit(SIGNAL("newTurn"))
                #self.emit(SIGNAL("otherUserFinishedTurn"))
                self.waitOtherUserAction()
            elif "game_ended" in server_msg:
                #self.emit(SIGNAL("end_the_game"))
                self.app.closeAllWindows()

    def play(self):
        if self.controllerObject.activePlayer !=self.controllerObject.userPlayer:
            print "THAT'S NOT MY TURN NOW"
            idle = threading.Thread(target=self.waitOtherUserAction)
            idle.start()
        else: print "IT IS MY TURN"

    def changeActivePlayer(self):
        x = self.controllerObject.players.index(self.controllerObject.activePlayer)
        if self.controllerObject.players[(x+1)%3].isAlive:
            self.controllerObject.activePlayer = self.controllerObject.players[(x+1)%3]
        else: self.controllerObject.activePlayer = self.controllerObject.players[(x+2)%3]

    def handleInsideChangeTurn(self):
        self.controllerObject.validSquares = []
        self.boardInstance.unselectAll()

        self.socket.send("turn_ended")
        print "Message sended to server = 'turn_ended' "
        for x in self.controllerObject.movement:
            msg = str(x)
            self.socket.send(msg)
        self.changeActivePlayer()
        self.container.update()

        self.emit(SIGNAL("newTurn"))

    def handleOutsideChangeTurn(self):
        self.makeRemoteMove()
        self.changeActivePlayer()
        self.container.update()
        self.emit(SIGNAL("newTurn"))

    def makeRemoteMove(self):
        self.socket.setblocking(1)
        newCoords = list()
        for i in xrange(6):
            newCoord = self.socket.recv(1)
            newCoords.append(int(newCoord))
        src = self.boardInstance.getData(newCoords[0:3])
        dst = self.boardInstance.getData(newCoords[3:6])
        self.controllerObject.move(src, dst)

    def gameEnded(self):
        print "Game ended"
        self.app.closeAllWindows()

    def playerLost(self):
        loser = QObject.sender(QObject())
        loser.isAlive = False
        i = loser.id
        self.socket.send("killed_%dpl" % i)
        print "Message sended to server = 'killed_%dpl'. " % i
        time.sleep(0.025)


    def main(self):
        self.app = QtGui.QApplication(sys.argv)
        self.container = View()
        self.boardInstance = Board()

        self.container.bindWith(self.boardInstance)
        self.controllerObject = Controller(self.boardInstance)
        QObject.connect(self.controllerObject, SIGNAL("turnEndedByUser"),self.handleInsideChangeTurn)
        QObject.connect(self.controllerObject, SIGNAL("changed()"),self.container.update)
        for i in xrange(3):
            QObject.connect(self.controllerObject.players[i],SIGNAL("player_lose"), self.playerLost)

        self.container.bindWithController(self.controllerObject)
        self.container.show()
        self.setup()

        sys.exit(self.app.exec_())

if __name__ == '__main__':
    program = Client()
    program.main()