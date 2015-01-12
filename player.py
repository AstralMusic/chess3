# -*- coding: utf-8 -*-
__author__ = 'Vladimir Konak'

from PyQt4.QtCore import QObject, SIGNAL
import  default_settings


class Player(QObject):
    def __init__(self, onDeskPosition = 0, name = ""):
        super(Player, self).__init__()
        self.onDeskPosition = onDeskPosition
        self.color = default_settings.grey
        self.isAlive = True
        self.isActive = False

    def setColor(self):
        if self.id == 0: self.color = default_settings.player_color_0
        if self.id == 1: self.color = default_settings.player_color_1
        if self.id == 2: self.color = default_settings.player_color_2

    def setName(self, playerName):
        self.name = playerName

    def setId(self, playerId):
        self.id = playerId
        self.setColor()

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
        srcCoords = self.figuresContainer.boardExample.getSquareCoordinates(source)
        dstCoords = self.figuresContainer.boardExample.getSquareCoordinates(destination)
        self.figuresContainer.movement = srcCoords + dstCoords
        #applying the move to the board
        destination.figure = source.figure
        source.figure = None
        #if some player was killed, return his instance
        return loser

    def createFigures(self, figContainer):
        self.figuresContainer = figContainer
        self.figuresContainer.createFigures(self)

class UserPlayer(Player):
    def handleClick(self):
        #if it's not my turn, don't handle click
        if self.isActive:
            sender =  QObject.sender(QObject())
            if not sender.square.isEmpty():
                if sender.square.figure.player == self:
                    self.figuresContainer.boardExample.unselectAll()
                    sender.square.figure.select()
                    self.squareWithSelectedFigure = sender.square
                    self.validSquares = self.figuresContainer.showPossibleMoves\
                        (sender.square.figure, self)
                    self.figuresContainer.boardExample.highlight(self.validSquares)
            if sender.square in self.validSquares:
                #actually move figures on board
                #if res == None then nobody is killed
                #in other case res will get the killed player
                anyLoses = self.move(self.squareWithSelectedFigure,sender.square)
                #was this:
                #if res: res.emit(SIGNAL("player_lose"))
                #changed to this:
                if anyLoses:
                    loser = anyLoses
                    i = loser.id
                    self.socket.send("killed_%dpl" % i)
                    print "Message sended to server = 'killed_%dpl'. " % i
                self.emit(SIGNAL("turnEndedByUser"))
            self.figuresContainer.boardExample.emit(SIGNAL("changed()"))

    #unneeded
    def informServerAboutLoserPlayer(self):
        loser = QObject.sender(QObject())
        i = loser.id
        self.socket.send("killed_%dpl" % i)
        print "Message sended to server = 'killed_%dpl'. " % i


class RemotePlayer(Player):
    def makeRemoteMove(self):
        self.socket.setblocking(1)
        newCoords = list()
        #take six numbers
        for i in xrange(6):
            newCoord = self.socket.recv(1)
            newCoords.append(int(newCoord))
        src = self.boardInstance.getSquare(newCoords[0:3])
        dst = self.boardInstance.getSquare(newCoords[3:6])
        #apply it to the board instance
        #just moves figures on board
        self.controllerObject.move(src, dst)
