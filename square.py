__author__ = 'Vladimir Konak'

import default_settings
from SquareButton import SquareButton

class Square:
    def __init__(self):
        self.figure = None
        self.isSelected = False
        self.color = None
        self.isHighlighted = False
        self.highlightColor = default_settings.highlight_color

    def createButton(self, parent_widget):
        self.button = SquareButton(self, parent_widget)

    def setupButton(self, position = (0,0,0)):
        a = position[0]
        b = position[1]
        c = position[2]
        self.button.setup(a,b,c)

    def isEmpty(self):
        if self.figure == None : return True
        else: return False