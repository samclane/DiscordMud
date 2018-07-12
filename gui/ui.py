""" Future home of the PyQt5 GUI """
from PyQt5.QtWidgets import QMainWindow, QFrame, QAction
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon


class MainWindow(QMainWindow):

    def __init__(self, app, world):
        super().__init__()

        self.statusbar = self.statusBar()

        self.world = world
        self.worldFrame = WorldFrame(self)
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

    def __init__(self, parent):
        super().__init__(parent)
