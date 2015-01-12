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

    #def anySelected(self):
        #if self.selectedFigure: return True
        #else: return False

    def handleClick(self):
        sender =  QObject.sender(QObject())
        if not sender.square.isEmpty():
            if sender.square.figure.player == self.activePlayer and self.activePlayer == self.userPlayer:
                self.boardExample.unselectAll()
                sender.square.figure.select()
                self.squareWithSelectedFigure = sender.square
                self.validSquares = self.figuresContainer.showPossibleMoves\
                    (sender.square.figure, self.activePlayer)
                self.boardExample.highlight(self.validSquares)
        if sender.square in self.validSquares:
            #actually move figures on board
            #if res == None then nobody is killed
            #in other case res will get the killed player
            res = self.move(self.squareWithSelectedFigure,sender.square)
            #if res: res.emit(SIGNAL("player_lose"))
            self.emit(SIGNAL("turnEndedByUser"))
        self.emit(SIGNAL("changed()"))

    def move(self, source, destination):
        #if it is any figure on destination square
        if destination.figure:
            if destination.figure.type == "KING":
                #define that this player will emit dieing signal
                loser = destination.figure.player
                #exclude him from alive players
                loser.isAlive = False
                #for each figure on board
                for eachFigure in self.figuresContainer.grid:
                    #if current figure belongs to player, who was killed
                    if eachFigure.player == loser:
                        #make this figure belong to player who killed
                        eachFigure.player = source.figure.player
            else: loser = None
        else: loser = None
        #self.movement contains info 'boy this move
        #and will be sent to server
        srcCoords = self.boardExample.getSquareCoordinates(source)
        dstCoords = self.boardExample.getSquareCoordinates(destination)
        self.movement = srcCoords + dstCoords
        #applying the move to the board
        destination.figure = source.figure
        source.figure = None
        #if some player was killed, return his instance
        return loser