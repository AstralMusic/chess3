__author__ = 'Vladimir Konak'

from PyQt4.QtCore import QObject, QString
from PyQt4.QtGui import  QColor


class Player(QObject):
    def __init__(self, onDeskPosition = 0, name = "user"):
        super(Player, self).__init__()
        self.setup(onDeskPosition, name)

        self.isAlive = True

    def setup(self, onDeskPosition , name):
        self.name = name
        self.id = onDeskPosition
        self.onDeskPosition = onDeskPosition
        self.color = QColor()

    def setColor(self):
        if self.id == 0: self.color = QColor(120,120,0)
        if self.id == 1: self.color = QColor(120,120,120)
        if self.id == 2: self.color = QColor(0,120,120)

class HumanPlayer(Player):
    pass

class NonHumanPlayer(Player):
    pass