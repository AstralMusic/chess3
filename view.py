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

        width = default_settings.window_width
        height = default_settings.window_height
        self.setGeometry(200, 200, width, height)
        self.setWindowTitle('Chess')
        self.setFixedSize(width,height)

        self.menubar = QMenuBar(self)
        self.menubar.setGeometry(QRect(0, 0, self.geometry().width(), 30))
        self.menubar.setObjectName(QString("menubar"))
        self.menu = QMenu(self.menubar)

    def bindWithBoard(self, boardObject):
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
        for a in xrange(3):
            for b in xrange(4):
                for c in xrange(8):
                    currentButton = self.boardExample.getSquare(a,b,c).button
                    #drawing actual square black or white
                    qpainter_object.setPen(QColor(0,0,0))
                    qpainter_object.setBrush(currentButton.color)
                    qpainter_object.drawPolygon(QPolygonF(currentButton.coords))
                    currentButton.paintEvent(QPaintEvent.Paint)

                    if currentButton.square.isHighlighted:
                        qpainter_object.setBrush(currentButton.square.highlightColor)
                        qpainter_object.drawPolygon(QPolygonF(currentButton.coords))


                    if not  currentButton.square.isEmpty():
                        #show selected or nor selected
                        if currentButton.square.figure.isSelected:
                            qpainter_object.setBrush(default_settings.highlight_selected_color)
                            qpainter_object.drawPolygon(QPolygonF(currentButton.coords))

                        #show figure
                        QTextCodec.setCodecForCStrings(QTextCodec.codecForName("UTF-8"))
                        qpainter_object.setPen(currentButton.square.figure.player.color)
                        qpainter_object.drawText(QPolygonF(currentButton.coords).boundingRect().x()+10,\
                                                 QPolygonF(currentButton.coords).boundingRect().y()+55,\
                                                 QString(currentButton.square.figure.__str__()))


        #show which player is active and names
        if self.controllerExample.activePlayer:
            qpainter_object.translate(self.width()/2,self.height()/2)
            qpainter_object.drawText(-300,-300,QString(self.controllerExample.players[1].name))
            qpainter_object.drawText(200,-300,QString(self.controllerExample.players[2].name))
            qpainter_object.drawText(150,350,QString(self.controllerExample.players[0].name))
            qpainter_object.rotate(self.controllerExample.activePlayer.onDeskPosition * 120.)
            qpainter_object.drawPolygon(QPolygonF([QPointF(-150,350),QPointF(150,350), QPointF(0,300) ]))
