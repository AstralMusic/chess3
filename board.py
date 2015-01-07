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
        for i in range(3):
            self.data.append([])
            for j in range(4):
                self.data[i].append([])
                for k in range(8):
                    temp_square = Square()
                    temp_square.createButton(containerWidget)
                    temp_square.setup(i,j,k)
                    self.data[i][j].append(temp_square)

    def getData(self, t = (0,0,0)):
        return self.data[t[0]][t[1]][t[2]]

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