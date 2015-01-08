# -*- coding: utf-8 -*-
__author__ = 'Vladimir Konak'

from PyQt4.QtCore import QObject, SIGNAL

from square import Square


class Board(QObject):
    def __init__(self):
        super(Board, self).__init__()
        self.data = []

    def createSquare(self, containerWidget):
        temp_square = Square()
        temp_square.createButton(containerWidget)

    def createPlayground(self, containerWidget):
        def square_init (a,b,c):
            temp_square = Square()
            temp_square.createButton(containerWidget)
            temp_square.setup(a,b,c)
            return temp_square

        self.data = [[[ square_init (i,j,k) for k in xrange(8)] for j in xrange(4)] for i in xrange(3)]


    def getData(self, t = (0,0,0)):
        return self.data[t[0]][t[1]][t[2]]

    def getSquareCoordinates(self,square):
        for a in xrange(3):
            for b in xrange(4):
                for c in xrange(8):
                    if self.data[a][b][c] == square :
                        return (a,b,c)

    def unselectAll(self):
        for a in range(3):
            for b in range(4):
                for c in range(8):
                    self.data[a][b][c].isHighlighted = False
                    if not self.data[a][b][c].isEmpty(): self.data[a][b][c].figure.unselect()

    def highlight(self, squares):
        for i in squares:
            i.isHighlighted = True

    def __repr__(self):
        return str(self.objectName())