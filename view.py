# -*- coding: utf-8 -*-
__author__ = 'Vladimir Konak'

from PyQt4.QtCore import QString, QTextCodec, QRect, QPointF
from PyQt4.QtGui import *
import default_settings

class View(QWidget):


    def __init__(self):
        super(View, self).__init__()

        self.initUI()

    def initUI(self):

        self.setGeometry(200, 200, 800, 800)
        self.setWindowTitle('Chess')
        self.setFixedSize(800,800)

        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, self.geometry().width(), 30))
        self.menubar.setObjectName(QString("menubar"))
        self.menu = QMenu(self.menubar)

    def bindWith(self, boardObject):
        boardObject.createPlayground(self)
        self.boardExample = boardObject

    def bindWithController(self, controllerObject):
        self.controllerExample = controllerObject

    #paint event initiates painting process by creating an instance of QtGui.QPainter class
    def paintEvent(self, e):
        qpainter_object = QPainter()
        myFont = QFont()
        myFont.setPixelSize(44)
        qpainter_object.begin(self)
        qpainter_object.setFont(myFont)
        self.updateView(qpainter_object)
        qpainter_object.end()



    #instructions to update everything, user sees on the screen
    def updateView(self, qpainter_object):
        for a in range(3):
            for b in range(4):
                for c in range(8):
                    current_square = self.boardExample.squares[a][b][c]
                    #drawing actual square black or white
                    qpainter_object.setPen(QColor(0,0,0))
                    qpainter_object.setBrush(current_square.color)
                    qpainter_object.drawPolygon(QPolygonF(current_square.coords))
                    current_square.paintEvent(QPaintEvent.Paint)

                    if current_square.isHighlighted:
                        qpainter_object.setBrush(current_square.highlightColor)
                        qpainter_object.drawPolygon(QPolygonF(current_square.coords))


                    if not  current_square.isEmpty():
                        #show selected or nor selected
                        if current_square.figure.isSelected:
                            qpainter_object.setBrush(default_settings.highlight_selected_color)
                            qpainter_object.drawPolygon(QPolygonF(current_square.coords))

                        #show figure
                        QTextCodec.setCodecForCStrings(QTextCodec.codecForName("UTF-8"))
                        qpainter_object.setPen(current_square.figure.player.color)
                        qpainter_object.drawText(QPolygonF(current_square.coords).boundingRect().x()+10,\
                                                 QPolygonF(current_square.coords).boundingRect().y()+55,\
                                                 QString(current_square.figure.__str__()))


        #show which player is active and names
        if self.controllerExample.activePlayer:
            qpainter_object.drawText(50,100,QString(self.controllerExample.players[1].name))
            qpainter_object.drawText(600,100,QString(self.controllerExample.players[2].name))
            qpainter_object.drawText(600,600,QString(self.controllerExample.players[0].name))

            qpainter_object.translate(400,400)
            qpainter_object.rotate(self.controllerExample.activePlayer.onDeskPosition * 120.)
            qpainter_object.drawPolygon(QPolygonF([QPointF(-150,350),QPointF(150,350), QPointF(0,300) ]))
