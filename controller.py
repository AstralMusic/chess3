__author__ = "Vladimir Konak"
# -*- coding: utf-8 -*-

from player import HumanPlayer, NonHumanPlayer
from figures import Figures
from PyQt4.QtCore import QObject, SIGNAL

class Controller(QObject):
    players = []
    def __init__(self, boardInstance):
        super(Controller, self).__init__()
        #creating players
        self.userPlayer = HumanPlayer()
        self.players.append(self.userPlayer)
        self.players.append(NonHumanPlayer(1))
        self.players.append(NonHumanPlayer(2))
        #bounding with board
        self.boardExample =  boardInstance
        #creating container for all figures
        self.figuresContainer = Figures(boardInstance)
        #creating figures, without putting them on desk yet
        self.figuresContainer.createFigures(self.players)

        self.activePlayer = None
        self.selectedFigure = None
        self.validSquares = iter([None])
        #connecting each squares with handler of click event
        for a in xrange(3):
            for b in xrange(4):
                for c in xrange(8):
                    QObject.connect(self.boardExample.squares[a][b][c],SIGNAL("clicked()"),self.handleClick)

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
                    QObject.connect(self.boardExample.squares[each.onDeskPosition][b][c],SIGNAL("clicked()"),self.handleClick)
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
                self.validSquares = self.figuresContainer.showPossibleMoves\
                    (sender.figure, self.activePlayer)
                self.boardExample.highlight(self.validSquares)
        if sender in self.validSquares:
            #actually move figures on board
            #if res == None then nobody is killed
            #in other case res will get the killed player
            res = self.move(self.squareWithSelectedFigure,sender)
            if res: res.emit(SIGNAL("player_lose"))
            self.emit(SIGNAL("turnEndedByUser"))
        self.emit(SIGNAL("changed()"))

    def move(self, source, destination):
        #if it is any figure on destination square
        if destination.figure:
            if destination.figure.type == "KING":
                #define that this player will emit dieing signal
                screamer = destination.figure.player
                #for each figure on board
                for eachFigure in self.figuresContainer.grid:
                    #if current figure belongs to player, who was killed
                    if eachFigure.player == destination.figure.player:
                        #make this figure belong to player who killed
                        eachFigure.player = source.figure.player
            else: screamer = None
        else: screamer = None
        #self.movement contains info 'boy this move
        #and will be sent to server
        srcCoords = self.boardExample.getSquareCoordinates(source)
        dstCoords = self.boardExample.getSquareCoordinates(destination)
        self.movement = srcCoords + dstCoords
        #applying the move to the board
        destination.figure = source.figure
        source.figure = None
        #if some player was killed
        if screamer: return screamer
        else: return None