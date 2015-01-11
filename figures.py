__author__ = "Vladimir Konak"
# -*- coding: utf-8 -*-

from PyQt4.QtCore import QObject, QString
from PyQt4.QtGui import QApplication, QColor

from figure import Figure

_encoding = QApplication.UnicodeUTF8


class Figures(QObject):
    grid = []
    def __init__(self):
        super(Figures, self).__init__()

    def createFiguresForPlayer(self,player):

        self.grid.extend( [Figure(what, player) for what in ["ROOK","ROOK",
                                                       "KNIGHT","KNIGHT",
                                                       "BISHOP","BISHOP",
                                                       "QUEEN","KING"]+["PAWN"]*8 ]
                        )

    def putFiguresOnDesk(self, boardExample):
        i = iter(self.grid)
        for a in range(3):
            p = [0,7,1,6,2,5,3,4]
            for c in range(8):
                x = i.next()
                boardExample.data[x.player.onDeskPosition][0][p[c]].figure = x

            for j in range(8):
                x = i.next()
                boardExample.data[x.player.onDeskPosition][1][j].figure = x
        self.boardExample = boardExample

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

    def showPossibleMoves(self,figure,boardInstance, activePlayer):
        pos =  self.getFigurePosition(figure)
        a = pos[0]
        b = pos[1]
        c = pos[2]
        validMoves = []
        self.activePlayer = activePlayer

        def recurs(position, dm,dn):
            try:
                np = self.newPosition(position,dm,dn)
                if len(np)>3: aa = np[3]
                else: aa = None
                current = boardInstance.getData(np)
                if current.isEmpty():
                    validMoves.append(current)
                    recurs(np,dm,dn)
                elif current.figure.player != self.activePlayer:
                    current.highlightColor = QColor(255,0,0)
                    validMoves.append(current)
                if aa:
                    npAlter = (aa,np[1],np[2])
                    current2 = boardInstance.getData(npAlter)
                    if current2.isEmpty():
                        validMoves.append(current2)
                        recurs(npAlter,dm,dn)
                    elif current2.figure.player != self.activePlayer:
                        current2.highlightColor = QColor(255,0,0)
                        validMoves.append(current2)
            except:
                pass

        def nonrecurs(position,dm , dn):
            try:
                np = self.newPosition(position,dm,dn)
                if len(np)>3: aa = np[3]
                else: aa = None
                current = boardInstance.getData(np)
                if current.isEmpty():
                    validMoves.append(current)
                elif current.figure.player != self.activePlayer:
                    current.highlightColor = QColor(255,0,0)
                    validMoves.append(current)
                if aa:
                    npAlter = (aa,np[1],np[2])
                    current2 = boardInstance.getData(npAlter)
                    if current2.isEmpty():
                        validMoves.append(current2)
                    elif current2.figure.player != self.activePlayer:
                        current2.highlightColor = QColor(255,0,0)
                        validMoves.append(current2)
            except:
                pass

        if figure.type == "PAWN":
            nonrecurs(pos, 1, 0)#FIX THIS
            if pos[1]==1 and pos[0]==self.activePlayer.onDeskPosition:
                nonrecurs(pos, 2, 0)#AND THIS
            for j in [-1,1]:
                nextPos = self.newPosition(pos, 1, j)
                if not nextPos: continue
                if not boardInstance.getData(nextPos).isEmpty():
                    nonrecurs(pos, 1, j)
        elif figure.type == "ROOK":
            recurs(pos,1,0)
            recurs(pos,0,1)
            recurs(pos,-1,0)
            recurs(pos,0,-1)
        elif figure.type == "KNIGHT":
            for i in [-2,-1,1,2]:
                for j in [-2,-1,1,2]:
                    if abs(i)==abs(j): continue
                    nonrecurs(pos, i , j)
        elif figure.type == "BISHOP":
            recurs(pos,1,1)
            recurs(pos,-1,1)
            recurs(pos,1,-1)
            recurs(pos,-1,-1)
        elif figure.type == "QUEEN":
            for i in [-1,0,1]:
                for j in [-1,0,1]:
                    if i==j==0: continue
                    else: recurs(pos, i, j)
        elif figure.type == "KING":
            for i in [-1,0,1]:
                for j in [-1,0,1]:
                    if i==j==0: continue
                    else: nonrecurs(pos, i, j)

        return validMoves

    def getFigurePosition(self, figure):
        for a in range(3):
            for b in range(4):
                for c in range(8):
                    if self.boardExample.data[a][b][c].figure == figure: return (a,b,c)