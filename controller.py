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
            self.move(self.squareWithSelectedFigure,sender)
            self.emit(SIGNAL("turnEndedByUser"))
        self.emit(SIGNAL("changed()"))

    def move(self, source, destination):
        if destination.figure:
            print "DST player was = " ,destination.figure.player.id
            if destination.figure.type == "KING":
                for eachFigure in self.figuresContainer.grid:
                    if eachFigure.player == destination.figure.player:
                        eachFigure.player = source.figure.player

        srcCoords = self.boardExample.getSquareCoordinates(source)
        dstCoords = self.boardExample.getSquareCoordinates(destination)
        self.movement = srcCoords + dstCoords

        print "SRC player now = " ,source.figure.player.id
        destination.figure = source.figure
        source.figure = None
        print "DST player now = " ,destination.figure.player.id

    """
    def kill(self, source, destination):
        if self.boardExample.getData(destination).figure.type == "KING":
            pass
        self.move(source, destination)


"""