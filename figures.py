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
        self.grid = list()

    def createFigures(self, player):
        x = ["ROOK","ROOK",  "KNIGHT","KNIGHT","BISHOP","BISHOP","QUEEN","KING"]+["PAWN"]*8
        self.grid.extend( [Figure(what, player) for what in x])

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
        if a != self.activePlayer.onDeskPosition:
            m = -m
            n = -n
        #CTE - "crossed the edge" flag. can be only 0 or 1
        CTE = (b+m)/4
        newA = ((1 +c/4)*CTE+a)%3
        newA2 = ((1 +(c+n)/4)*CTE+a)%3
        newB = CTE*(7-b-m) + (1 - CTE)*(b+m)
        newC = (c+n)*(1-CTE) + CTE*(7-c-n)
        if newC<0 or newC>7: return
        if newA == newA2: return (newA, newB, newC)
        return (newA,newB,newC,newA2)

    def showPossibleMoves(self,figure, activePlayer):
        pos =  self.getFigurePosition(figure)
        validMoves = []
        self.activePlayer = activePlayer
            
        def checkInDirection(position, dm,dn, recursive = True , previous = (0,0,0)):
            coords = self.newPosition(position,dm,dn)
            try:
                if not coords: raise BaseException, "newPosition() returnd nothing, because of new coords are out of desk."
                if len(coords)>3: aa = [coords[0],coords[3]]
                else: aa = [coords[0]]
                b = coords[1]
                c = coords[2]
                for A in aa:
                    nextSq = self.boardExample.getSquare(A,b,c)
                    if nextSq.isEmpty():
                        prevSq = self.boardExample.getSquare(previous)
                        if nextSq == prevSq:
                            checkInDirection(position,-dm,-dn, previous = position)
                        else: validMoves.append(nextSq)
                        if recursive: checkInDirection((A,b,c),dm,dn, previous = position)
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
                if pos[1]==1:
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