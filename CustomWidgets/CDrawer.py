from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QPointF
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget, QApplication


class CDrawer(QWidget):

    LEFT, TOP, RIGHT, BOTTOM = range(4)

    def __init__(self, *args, stretch=1 / 3, direction=0, widget=None, **kwargs):
        super(CDrawer, self).__init__(*args, **kwargs)
        self.setWindowFlags(self.windowFlags(
        ) | Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.animIn = QPropertyAnimation(
            self, duration=500, easingCurve=QEasingCurve.OutCubic)
        self.animOut = QPropertyAnimation(
            self, duration=500, finished=self.onAnimOutEnd,
            easingCurve=QEasingCurve.OutCubic)
        self.animOut.setPropertyName(b'pos')
        self.animOut.setDuration(500)
        self.setStretch(stretch)
        self.direction = direction
        self.alphaWidget = QWidget(
            self, objectName='CDrawer_alphaWidget',
            styleSheet='#CDrawer_alphaWidget{background:rgba(55,55,55,100);}')
        self.alphaWidget.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setWidget(widget)

    def resizeEvent(self, event):
        self.alphaWidget.resize(self.size())
        super(CDrawer, self).resizeEvent(event)

    def mousePressEvent(self, event):
        pos = event.pos()
        if pos.x() >= 0 and pos.y() >= 0 and self.childAt(pos) == None and self.widget:
            if not self.widget.geometry().contains(pos):
                self.animationOut()
                return
        super(CDrawer, self).mousePressEvent(event)

    def show(self):
        super(CDrawer, self).show()
        parent = self.parent().window() if self.parent() else self.window()
        if not parent or not self.widget:
            return
        self.setGeometry(parent.geometry())
        geometry = self.geometry()
        self.animationIn(geometry)

    def animationIn(self, geometry):
        """
        :param geometry:
        """
        if self.direction == self.LEFT:
            # Left drawer
            self.widget.setGeometry(
                0, 0, int(geometry.width() * self.stretch), geometry.height())
            self.widget.hide()
            self.animIn.setStartValue(QPoint(-self.widget.width(), 0))
            self.animIn.setEndValue(QPoint(0, 0))
            self.animIn.start()
            self.widget.show()
        elif self.direction == self.TOP:
            # upper drawer
            self.widget.setGeometry(
                0, 0, geometry.width(), int(geometry.height() * self.stretch))
            self.widget.hide()
            self.animIn.setStartValue(QPoint(0, -self.widget.height()))
            self.animIn.setEndValue(QPoint(0, 0))
            self.animIn.start()
            self.widget.show()
        elif self.direction == self.RIGHT:
            # right drawer
            width = int(geometry.width() * self.stretch)
            self.widget.setGeometry(
                geometry.width() - width, 0, width, geometry.height())
            self.widget.hide()
            self.animIn.setStartValue(QPoint(self.width(), 0))
            self.animIn.setEndValue(
                QPoint(self.width() - self.widget.width(), 0))
            self.animIn.start()
            self.widget.show()
        elif self.direction == self.BOTTOM:
            # lower drawer
            height = int(geometry.height() * self.stretch)
            self.widget.setGeometry(
                0, geometry.height() - height, geometry.width(), height)
            self.widget.hide()
            self.animIn.setStartValue(QPoint(0, self.height()))
            self.animIn.setEndValue(
                QPoint(0, self.height() - self.widget.height()))
            self.animIn.start()
            self.widget.show()

    def animationOut(self):
        """Leave animation
        """
        self.animIn.stop()  # Stop entering animation
        geometry = self.widget.geometry()
        if self.direction == self.LEFT:
            # left drawer
            self.animOut.setStartValue(geometry.topLeft())
            self.animOut.setEndValue(QPoint(-self.widget.width(), 0))
            self.animOut.start()
        elif self.direction == self.TOP:
            # upper drawer
            self.animOut.setStartValue(QPoint(0, geometry.y()))
            self.animOut.setEndValue(QPoint(0, -self.widget.height()))
            self.animOut.start()
        elif self.direction == self.RIGHT:
            # right drawer
            self.animOut.setStartValue(QPoint(geometry.x(), 0))
            self.animOut.setEndValue(QPoint(self.width(), 0))
            self.animOut.start()
        elif self.direction == self.BOTTOM:
            # lower drawer
            self.animOut.setStartValue(QPoint(0, geometry.y()))
            self.animOut.setEndValue(QPoint(0, self.height()))
            self.animOut.start()

    def onAnimOutEnd(self):
        """Leave animation ends
        """
        QApplication.sendEvent(self, QMouseEvent(
            QMouseEvent.MouseButtonPress, QPointF(-1, -1), Qt.LeftButton, Qt.NoButton, Qt.NoModifier))

    def setWidget(self, widget):
        """Set child controls
        :param widget:
        """
        self.widget = widget
        if widget:
            widget.setParent(self)
            self.animIn.setTargetObject(widget)
            self.animOut.setTargetObject(widget)

    def setEasingCurve(self, easingCurve):
        """
        :param easingCurve:
        """
        self.animIn.setEasingCurve(easingCurve)

    def getStretch(self):
        """Get proportion
        """
        return self.stretch

    def setStretch(self, stretch):
        """
        :param stretch:
        """
        self.stretch = max(0.1, min(stretch, 0.9))

    def getDirection(self):
        """
        """
        return self.direction

    def setDirection(self, direction):
        """
        :param direction:
        """
        direction = int(direction)
        if direction < 0 or direction > 3:
            direction = self.LEFT
        self.direction = direction
