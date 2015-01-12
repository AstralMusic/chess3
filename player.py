__author__ = 'Vladimir Konak'

from PyQt4.QtCore import QObject, QString
import  default_settings


class Player(QObject):
    def __init__(self, onDeskPosition = 0, name = "user"):
        super(Player, self).__init__()
        self.setup(onDeskPosition, name)

        self.isAlive = True

    def setup(self, onDeskPosition , name):
        self.name = name
        self.id = onDeskPosition
        self.onDeskPosition = onDeskPosition
        self.color = default_settings.grey

    def setColor(self):
        if self.id == 0: self.color = default_settings.player_color_0
        if self.id == 1: self.color = default_settings.player_color_1
        if self.id == 2: self.color = default_settings.player_color_2

class HumanPlayer(Player):
    pass

class NonHumanPlayer(Player):
    pass