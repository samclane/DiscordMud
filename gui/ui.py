""" Future home of the PyQt5 GUI """
from PyQt5.QtWidgets import QMainWindow, QFrame, QAction
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QPainter, QImage

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
        self.menubar = self.menuBar()
        fileMenu = self.menubar.addMenu('&File')
        fileMenu.addAction(exitAct)

        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('DiscordMUD - Backend Manager')
        self.show()


class WorldFrame(QFrame):
    msg2Statusbar = pyqtSignal(str)

    def __init__(self, parent, world):
        super().__init__(parent)
        self.world = world

        self.scale = 1

    def squareWidth(self):
        '''returns the width of one square'''

        return (self.contentsRect().width() // self.world.Width) * self.scale

    def squareHeight(self):
        '''returns the height of one square'''

        return (self.contentsRect().height() // self.world.Height) * self.scale

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.contentsRect()

        dirtpix = QImage(r"res/grass.png").scaledToWidth(self.squareWidth()).scaledToHeight(self.squareHeight())
        townpix = QImage(r"res/town.png").scaledToWidth(self.squareWidth()).scaledToHeight(self.squareHeight())
        wildpix = QImage(r"res/wild.png").scaledToWidth(self.squareWidth()).scaledToHeight(self.squareHeight())
        playerpix = QImage(r"res/player.png").scaledToWidth(self.squareWidth()).scaledToHeight(self.squareHeight())

        canvasTop = rect.bottom() - self.world.Height * self.squareHeight()

        for i in range(self.world.Height):
            for j in range(self.world.Width):
                space = self.world.Map[i][j]
                xcoord, ycoord = rect.left() + j * dirtpix.width(), canvasTop + i * dirtpix.height()

                painter.drawImage(xcoord, ycoord, dirtpix)
                if isinstance(space, Town):
                    painter.drawImage(xcoord, ycoord, townpix)
                if isinstance(space, Wilds):
                    painter.drawImage(xcoord, ycoord, wildpix)

        for player in self.world.Users:
            xcoord, ycoord = rect.left() + player.Location.X * dirtpix.width(), canvasTop + player.Location.Y * dirtpix.height()
            painter.drawImage(xcoord, ycoord, playerpix)

    def wheelEvent(self, event):
        self.scale += event.angleDelta().y() / 2880
        self.update()
