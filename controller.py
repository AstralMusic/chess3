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
        #QObject.connect(self, SIGNAL("turnEnded()"),self.turnPass)

    def setActivePlayer(self, player):
        self.activePlayer = player
        self.emit(SIGNAL("changed()"))

    def getPlayerById(self, Id):
        for i in self.players:
            if i.id == Id: return i

    def setUserPlayerName(self, playerName):
        self.userPlayer.name = playerName
    def setUserPlayerId(self, playerId):
        self.userPlayer.id = playerId
        self.userPlayer.setColor()

    def setRemotePlayerName(self, onDeskPosition, playerName):
        self.players[onDeskPosition].name = playerName
    def setRemotePlayerId(self, onDeskPosition, playerId):
        self.players[onDeskPosition].id = playerId
        self.players[onDeskPosition].setColor()


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
            if sender.figure.player == self.activePlayer and self.activePlayer == self.userPlayer:
                self.boardExample.unselectAll()
                sender.figure.select()
                self.squareWithSelectedFigure = sender
                self.validSquares = self.figuresContainer.showPossibleMoves(sender.figure, self.boardExample, self.activePlayer)
                self.boardExample.highlight(self.validSquares)
            if sender in self.validSquares:
                self.kill(self.squareWithSelectedFigure,sender)
                self.emit(SIGNAL("turnEndedByUser"))
        else:
            if sender in self.validSquares:
                self.move(self.squareWithSelectedFigure,sender)
                self.emit(SIGNAL("turnEndedByUser"))
        self.emit(SIGNAL("changed()"))

    def move(self, source, destination):
        srcCoords = self.boardExample.getSquareCoordinates(source)
        dstCoords = self.boardExample.getSquareCoordinates(destination)
        self.movement = srcCoords + dstCoords

        destination.figure = source.figure
        source.figure = None


    def kill(self, source, destination):
        self.move(source, destination)


