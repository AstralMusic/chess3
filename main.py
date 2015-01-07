__author__ = 'Vladimir Konak'

import sys

from  PyQt4 import QtGui
from PyQt4.QtCore import QObject, SIGNAL

from view import View
from board import Board
from controller import Controller


def main():

    app = QtGui.QApplication(sys.argv)

    container = View()
    boardInstance = Board()
    container.bindWith(boardInstance)

    manager = Controller(boardInstance)

    QObject.connect(manager,SIGNAL("changed()"),container.update)

    container.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()