__author__ = "Vladimir Konak"
# -*- coding: utf-8 -*-
from PyQt4.QtCore import QObject
from PyQt4.QtGui import QApplication

from figure import Figure
import default_settings

_encoding = QApplication.UnicodeUTF8


class Figures(QObject):
    def __init__(self, boardInstance):
        super(Figures, self).__init__()
        self.boardExample = boardInstance

    def createFigures(self,players):
        self.grid = list()
        for player in players:
            self.grid.extend( [Figure(what, player) for what in ["ROOK","ROOK",
                                                       "KNIGHT","KNIGHT",
                                                       "BISHOP","BISHOP",
                                                       "QUEEN","KING"]+["PAWN"]*8 ]
                        )
        self.putFiguresOnDesk()
    def putFiguresOnDesk(self):
        i = iter(self.grid)
        for a in range(3):
            p = [0,7,1,6,2,5,3,4]
            for c in range(8):
                x = i.next()
                self.boardExample.squares[x.player.onDeskPosition][0][p[c]].figure = x

            for j in range(8):
                x = i.next()
                self.boardExample.squares[x.player.onDeskPosition][1][j].figure = x

    def newPosition(self, position = tuple([int,int,int]), m = 0 , n = 0):
        a = position[0]
        b = position[1]
        c = position[2]
        if not a == self.activePlayer.onDeskPosition:
            m = -m
            n = -n
        newA = ((1 +c/4)*((b+m)/4)+a)%3
        newAalter = ((1 +(c+n)/4)*((b+m)/4)+a)%3
        newB = (b+m)/4*(7-b-m) + (1 - (b+m)/4)*(b+m)
        newC = (c+n)*(1-(b+m)/4) + (b+m)/4*(7-c-n)
        if newC<0 or newC>7: return
        if newA == newAalter: return (newA, newB, newC)
        else: return (newA,newB,newC,newAalter)

    def showPossibleMoves(self,figure, activePlayer):
        pos =  self.getFigurePosition(figure)
        validMoves = []
        self.activePlayer = activePlayer
            
        def checkInDirection(position, dm,dn, recursive = True ):
            print "checkInDirection() entered"
            print "nextSq = boardInstance.getSquare({0}), dx = {1} , dy={2}".format(position,dm,dn)
            coords = self.newPosition(position,dm,dn)
            print "nextSq = boardInstance.getSquare({0})".format(coords)
            try:
                if not coords: raise BaseException, "newPosition() returnd nothing, because of new coords are out of desk."
                if len(coords)>3: aa = [coords[0],coords[3]]
                else: aa = [coords[0]]
                b = coords[1]
                c = coords[2]
                for A in aa:
                    print "nextSq = boardInstance.getSquare((%d, %d, %d))"% (A,b,c)
                    nextSq = self.boardExample.getSquare((A,b,c))
                    if nextSq.isEmpty():
                        validMoves.append(nextSq)
                        if recursive: checkInDirection((A,b,c),dm,dn)
                    elif nextSq.figure.player != self.activePlayer:
                        nextSq.highlightColor = default_settings.highlight_attack_color
                        validMoves.append(nextSq)
            except BaseException, e:
                print "Error: %s" % e

        if figure.type == "PAWN":
            nextPos = self.newPosition(pos, 1, 0)
            nextSq = self.boardExample.getSquare(nextPos)
            if nextSq.isEmpty():
                validMoves.append(nextSq)
                if pos[1]==1 and pos[0]==self.activePlayer.onDeskPosition:
                    sq = self.boardExample.getSquare(self.newPosition(pos,2,0))
                    if sq.isEmpty():
                        validMoves.append(sq)
            for j in [-1,1]:
                nextPos = self.newPosition(pos, 1, j)
                if not nextPos: continue
                if not self.boardExample.getSquare(nextPos).isEmpty():
                    checkInDirection(pos, 1, j, recursive = False)
        elif figure.type == "ROOK":
            checkInDirection(pos,1,0)
            checkInDirection(pos,0,1)
            checkInDirection(pos,-1,0)
            checkInDirection(pos,0,-1)
        elif figure.type == "KNIGHT":
            for i in [-2,-1,1,2]:
                for j in [-2,-1,1,2]:
                    if abs(i)==abs(j): continue
                    checkInDirection(pos, i , j, recursive = False)
        elif figure.type == "BISHOP":
            checkInDirection(pos,1,1)
            checkInDirection(pos,-1,1)
            checkInDirection(pos,1,-1)
            checkInDirection(pos,-1,-1)
        elif figure.type == "QUEEN":
            for i in [-1,0,1]:
                for j in [-1,0,1]:
                    if i==j==0: continue
                    else: checkInDirection(pos, i, j)
        elif figure.type == "KING":
            for i in [-1,0,1]:
                for j in [-1,0,1]:
                    if i==j==0: continue
                    else: checkInDirection(pos, i, j, recursive = False)

        return validMoves

    def getFigurePosition(self, figure):
        for a in range(3):
            for b in range(4):
                for c in range(8):
                    if self.boardExample.squares[a][b][c].figure == figure: return (a,b,c)