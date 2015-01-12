# -*- coding: utf-8 -*-
__author__ = "Vladimir Konak"

from math import sin, cos, radians

from PyQt4.QtCore import QPointF, Qt
from PyQt4.QtGui import QAbstractButton, QApplication,QPolygonF

import default_settings
black = default_settings.black
white = default_settings.white

class SquareButton(QAbstractButton):
    def __init__(self, squareObject, central_widget):
        self.square = squareObject
        super(SquareButton, self).__init__(central_widget)

    def setGeometry(self, rect):
        super(SquareButton, self).setGeometry(rect)

    def enterEvent(self, *args, **kwargs):
        if not self.square.isEmpty() or self.square.isHighlighted:
            QApplication.setOverrideCursor(Qt.PointingHandCursor)

    def leaveEvent(self, *args, **kwargs):
        if not self.square.isEmpty() or self.square.isHighlighted:
            QApplication.restoreOverrideCursor()

    def paintEvent(self, e):
        pass

    def setup(self, a, b, c):
        #a  = (0..2)
        #b  = (0..3)
        #c  = (0..7)
        d_alpha = 30./4
        square_size = r = 50
        db = 5 - b
        dc = c - 4
        k = 1.16
        self.coords = [
                    QPointF(dc*r,r*(db-(2-abs(dc))*sin(radians(b*d_alpha)))*k),
                    QPointF((dc+1)*r,r*(db-(2-abs(dc+1))*sin(radians(b*d_alpha)))*k),
                    QPointF((dc+1)*r,r*(db-1-(2-abs(dc+1))*sin(radians(b*d_alpha+d_alpha)))*k),
                    QPointF(dc*r,r*(db-1-(2-abs(dc))*sin(radians(b*d_alpha+d_alpha)))*k)
                         ]
        if (b+c)%2: self.color = white
        else: self.color = black

        def rotate(self,theta):
            theta = radians(theta)
            for point in self.coords :
                x = point.x()
                y = point.y()
                point.setX(x*cos(theta) - y*sin(theta))
                point.setY(y*cos(theta) + x*sin(theta))

        def translate(self, dx, dy):
            for point in self.coords :
                point.setX(point.x()+dx)
                point.setY(point.y()+dy)

        rotate(self,a*120.)
        translate(self, 400,400)
        button_geometry = QPolygonF(self.coords).boundingRect()
        self.setGeometry(button_geometry.toRect())
        self.show()