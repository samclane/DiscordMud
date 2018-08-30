import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, QStyle, QSplitter

from gui import graphics, logs


def Icon(parent, macro):
    """ Convenience method to easily access default Qt Icons """
    return parent.style().standardIcon(getattr(QStyle, macro))


class MainWindow(QMainWindow):

    def __init__(self, app, world):
        super().__init__()

        self.logger = logging.Logger('MainWindow')

        # Init Statusbar
        self.statusbar = self.statusBar()

        # Init game world object
        self.world = world
        self.worldFrame = graphics.WorldFrame(self, world)
        self.setCentralWidget(self.worldFrame)
        self.worldFrame.msg2Statusbar[str].connect(self.statusbar.showMessage)

        # Init menubar
        resetAct = QAction(Icon(self, 'SP_BrowserReload'), '&Reset Viewport', self)
        resetAct.setStatusTip('Reset the viewport to default view')
        resetAct.triggered.connect(self.worldFrame.resetViewport)

        saveAct = QAction(Icon(self, 'SP_DialogSaveButton'), '&Save World', self)
        saveAct.setStatusTip('Save the world object to a file')
        saveAct.triggered.connect(self.world.saveAsFile)

        exitAct = QAction(Icon(self, 'SP_MessageBoxCritical'), '&Exit', self)
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(app.quit)

        self.menubar = self.menuBar()
        fileMenu = self.menubar.addMenu('&File')
        fileMenu.addAction(saveAct)
        fileMenu.addAction(resetAct)
        fileMenu.addAction(exitAct)

        # Add toolbar
        townAct = QAction(QIcon(r"res/icons/town.png"), 'Add Town', self)
        townAct.setStatusTip("Add a new town to the map.")
        townAct.triggered.connect(lambda e: self.worldFrame.changePointerMode(graphics.PointerMode.AddTown))

        wildsAct = QAction(QIcon(r"res/icons/wild.png"), 'Add Wilds', self)
        wildsAct.setStatusTip("Add a new wild square to the map.")
        wildsAct.triggered.connect(lambda e: self.worldFrame.changePointerMode(graphics.PointerMode.AddWilds))

        self.toolbar = self.addToolBar('Map')
        self.toolbar.addAction(townAct)
        self.toolbar.addAction(wildsAct)

        # Init window and show
        self.setWindowTitle('DiscordMUD - {}'.format(world.Name))
        self.setWindowIcon(QIcon(r"res/icons/dungeon-gate.png"))
        self.showMaximized()
        self.worldFrame.resetViewport()

        log_handler = logs.QPlainTextEditLogger(self)
        splitter1 = QSplitter(Qt.Vertical, self)
        splitter1.addWidget(self.worldFrame)
        splitter1.addWidget(log_handler.widget)
        splitter1.setStretchFactor(1, 0)
        self.setCentralWidget(splitter1)

        self.logger.addHandler(log_handler)

    def update(self):
        super().update()
        self.worldFrame.update()

    def resizeEvent(self, event):
        self.worldFrame.fitInView()
