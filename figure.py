__author__ = 'Vladimir Konak'
# -*- coding: utf-8 -*-


from PyQt4.QtCore import QObject, QString, SIGNAL

class Figure(QObject):
    def __init__(self, type, player):
        super(Figure, self).__init__()
        self.isSelected = False
        self.type = type
        self.player = player

    def __delete__(self, instance):
        if self.type == "KING":
            self.emit(SIGNAL("playerLost()"))

    def select(self):
        self.isSelected = True

    def unselect(self):
        self.isSelected = False

    def __str__(self):
        if self.type == "PAWN":
            return QString("♟")
        elif self.type == "ROOK":
            return QString("♜")
        elif self.type == "KNIGHT":
            return QString("♞")
        elif self.type == "BISHOP":
            return QString("♝")
        elif self.type == "QUEEN":
            return QString("♛")
        elif self.type == "KING":
            return QString("♚")

