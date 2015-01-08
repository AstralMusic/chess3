__author__ = "Vladimir Konak"
# -*- coding: utf-8 -*-

from player import HumanPlayer, NonHumanPlayer
from figures import Figures
from PyQt4.QtCore import QObject, SIGNAL, SLOT

class Controller(QObject):
    players = []
    def __init__(self, boardInstance):
        super(Controller, self).__init__()
        self.boardExample =  boardInstance
        self.figuresContainer = Figures()

        self.userPlayer = HumanPlayer()
        self.players.append(self.userPlayer)
        self.players.append(NonHumanPlayer(1))
        self.players.append(NonHumanPlayer(2))

        self.activePlayer = None
        self.selectedFigure = None
        self.validSquares = iter([None])

        self.createFigures()
        QObject.connect(self, SIGNAL("turnEnded()"),self.turnPass)

    def getPlayerById(self, Id):
        for i in self.players:
            if i.id == Id: return i

    def setUserPlayerName(self, playerName):
        self.userPlayer.name = playerName
    def setUserPlayerId(self, playerId):
        self.userPlayer.id = playerId

    def setRemotePlayerName(self, onDeskPosition, playerName):
        self.players[onDeskPosition].name = playerName
    def setRemotePlayerId(self, onDeskPosition, playerId):
        self.players[onDeskPosition].id = playerId


    def createFigures(self):
        for each in self.players:
            self.figuresContainer.createFiguresForPlayer(each)
            for b in range(4):
                for c in range(8):
                    QObject.connect(self.boardExample.data[each.onDeskPosition][b][c],SIGNAL("clicked()"),self.handleClick)
        self.figuresContainer.putFiguresOnDesk(self.boardExample)

    def anySelected(self):
        if self.selectedFigure: return True
        else: return False

    def handleClick(self):
        sender =  QObject.sender(QObject())
        if not sender.isEmpty():
            if sender.figure.player == self.activePlayer:
                self.boardExample.unselectAll()
                sender.figure.select()
                self.squareWithSelectedFigure = sender
                self.validSquares = self.figuresContainer.showPossibleMoves(sender.figure, self.boardExample, self.activePlayer)
                self.boardExample.highlight(self.validSquares)
            if sender in self.validSquares:
                self.kill(self.squareWithSelectedFigure,sender)
        else:
            if sender in self.validSquares:
                self.move(self.squareWithSelectedFigure,sender)
        self.emit(SIGNAL("changed()"))

    def move(self, source, destination):
        destination.figure = source.figure
        source.figure = None
        self.emit(SIGNAL("turnEnded()"))

    def kill(self, source, destination):
        destination.figure = source.figure
        source.figure = None
        self.emit(SIGNAL("turnEnded()"))

    def turnPass(self):
        print "Turn ended"
        x = self.players.index(self.activePlayer)
        self.activePlayer = self.players[(x+1)%3]
        self.validSquares = []
        self.boardExample.unselectAll()
