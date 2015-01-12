# -*- coding: utf-8 -*-
__author__ = "Vladimir Konak"

from player import UserPlayer, RemotePlayer
from figures import Figures
from PyQt4.QtCore import QObject, SIGNAL

class Controller(QObject):
    players = []
    def __init__(self, boardInstance):
        super(Controller, self).__init__()
        #bounding with board
        self.boardExample =  boardInstance
        #creating container for all figures
        self.figuresContainer = Figures(boardInstance)

        #creating players
        self.userPlayer = UserPlayer()
        self.players.append(self.userPlayer)
        self.players.append(RemotePlayer(onDeskPosition = 1))
        self.players.append(RemotePlayer(onDeskPosition = 2))

        #bind with figures
        for player in self.players:
            player.createFigures(self.figuresContainer)
        self.figuresContainer.putFiguresOnDesk()

        #creating figures, without putting them on desk yet
        #self.figuresContainer.createFigures(self.players)

        self.activePlayer = None
        self.selectedFigure = None
        self.validSquares = iter([None])
        #connecting each squares with handler of click event
        for a in xrange(3):
            for b in xrange(4):
                for c in xrange(8):
                    #QObject.connect(self.boardExample.getSquare(a,b,c).button,SIGNAL("clicked()"),self.handleClick)
                    #when user player is ready to handle event on the board uncomment following and comment previous
                    QObject.connect(self.boardExample.getSquare(a,b,c).button,SIGNAL("clicked()"),self.userPlayer.handleClick)

    def setActivePlayer(self, player):
        self.activePlayer = player
        self.activePlayer.isActive = True
        self.emit(SIGNAL("changed()"))

    def getPlayerById(self, Id):
        for i in self.players:
            if i.id == Id: return i
