""" Future home of the PyQt5 GUI """
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon, QPainter, QImage
from PyQt5.QtWidgets import QMainWindow, QFrame, QAction

from gamelogic.gamespace import Town, Wilds


class MainWindow(QMainWindow):

    def __init__(self, app, world):
        super().__init__()

        self.statusbar = self.statusBar()

        self.world = world
        self.worldFrame = WorldFrame(self, world)
        self.setCentralWidget(self.worldFrame)
        self.worldFrame.msg2Statusbar[str].connect(self.statusbar.showMessage)

        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(app.quit)

        resetAct = QAction(QIcon('none.png'), '&Reset', self)
        resetAct.setStatusTip('Reset the viewport to default view')
        resetAct.triggered.connect(self.worldFrame.resetViewport)

        self.menubar = self.menuBar()
        fileMenu = self.menubar.addMenu('&File')
        fileMenu.addAction(resetAct)
        fileMenu.addAction(exitAct)

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('DiscordMUD - Backend Manager')
        self.show()


class WorldFrame(QFrame):
    msg2Statusbar = pyqtSignal(str)

    def __init__(self, parent, world):
        super().__init__(parent)
        self.world = world

        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

        self.resetViewport()

    def resetViewport(self):
        self.scale = 1
        self.panX = 0
        self.panY = 0
        self.update()

    def gridToPix(self, x, y):
        rect = self.contentsRect()
        canvasTop = rect.bottom() - self.world.Height * self.squareHeight()
        xcoord, ycoord = rect.left() + self.panX + x * self.squareWidth(), \
                         canvasTop + self.panY + y * self.squareHeight()
        return xcoord, ycoord

    def pixToGrid(self, x, y):
        rect = self.contentsRect()
        canvasTop = rect.bottom() - self.world.Height * self.squareHeight()
        gridx, gridy = (x - rect.left() - self.panX) // self.squareWidth(), \
                       (y - canvasTop - self.panY) // self.squareHeight()
        return gridx, gridy

    def squareWidth(self):
        '''returns the width of one square'''

        return int((self.contentsRect().width() // self.world.Width / 2) * self.scale)

    def squareHeight(self):
        '''returns the height of one square'''

        return int((self.contentsRect().height() // self.world.Height) * self.scale)

    def paintEvent(self, event):
        painter = QPainter(self)

        dirtpix = QImage(r"res/grass.png").scaledToWidth(self.squareWidth()).scaledToHeight(self.squareHeight())
        townpix = QImage(r"res/town.png").scaledToWidth(self.squareWidth()).scaledToHeight(self.squareHeight())
        wildpix = QImage(r"res/wild.png").scaledToWidth(self.squareWidth()).scaledToHeight(self.squareHeight())
        playerpix = QImage(r"res/player.png").scaledToWidth(self.squareWidth()).scaledToHeight(self.squareHeight())

        for i in range(self.world.Height):
            for j in range(self.world.Width):
                space = self.world.Map[i][j]
                xcoord, ycoord = self.gridToPix(j, i)

                painter.drawImage(xcoord, ycoord, dirtpix)
                if isinstance(space, Town):
                    painter.drawImage(xcoord, ycoord, townpix)
                if isinstance(space, Wilds):
                    painter.drawImage(xcoord, ycoord, wildpix)

        for player in self.world.Users:
            xcoord, ycoord = self.gridToPix(player.Location.X, player.Location.Y)
            painter.drawImage(xcoord, ycoord, playerpix)

    def wheelEvent(self, event):
        self.scale += event.angleDelta().y() / 2880
        print(self.scale)
        self.update()

    def keyPressEvent(self, event):
        key = event.key()
        xresolution = self.squareWidth()
        yresolution = self.squareHeight()

        if key == Qt.Key_Left:
            self.panX += xresolution
        elif key == Qt.Key_Right:
            self.panX -= xresolution
        elif key == Qt.Key_Down:
            self.panY -= yresolution
        elif key == Qt.Key_Up:
            self.panY += yresolution
        else:
            super().keyPressEvent(event)

        self.update()

    def mouseMoveEvent(self, event):
        ex, ey = event.x(), event.y()
        gridx, gridy = self.pixToGrid(ex, ey)
        self.msg2Statusbar.emit("({}, {})".format(int(gridx), int(gridy)))
        self.update()
