# -*- coding: utf-8 -*-
__author__ = "Vladimir Konak"

from PyQt4.QtCore import SIGNAL, SLOT, QString
from PyQt4.QtGui import *

class SetupBox(QWidget):
    def __init__(self):
        super(SetupBox, self).__init__()
        self.setGeometry(400,400,20,20)
        self.setFixedSize(400,150)

        self.gridLayout = QGridLayout(self)
        self.verticalLayout = QVBoxLayout()
        f = QFont()
        f.setPixelSize(26)
        self.label = QLabel(self)
        self.label.setFont(f)
        self.label.setText(QString("Your name"))
        self.textBox = QLineEdit(self)
        self.textBox.setFont(f)
        self.button = QPushButton()
        self.button.setText(QString("Ok"))
        self.verticalLayout.addWidget(self.label)
        self.verticalLayout.addWidget(self.textBox)
        self.verticalLayout.addWidget(self.button)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        QShortcut(QKeySequence("Return"),self).activated.connect(self.button.click)
        self.button.clicked.connect(self.getInfo)

    def getInfo(self):
        self.name = self.textBox.text()
        self.emit(SIGNAL("infoGathered()"))