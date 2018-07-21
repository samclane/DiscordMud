""" Future home of the PyQt5 GUI """
from PyQt5.QtCore import pyqtSignal, Qt, QRectF
from PyQt5.QtGui import QIcon, QImage
from PyQt5.QtWidgets import QMainWindow, QAction, QStyle, QGraphicsView, QGraphicsScene, QGraphicsObject

from gamelogic.gamespace import Town, Wilds


def Icon(parent, macro):
    return parent.style().standardIcon(getattr(QStyle, macro))


class PointerMode:
    Normal = 0
    AddTown = 1
    AddWilds = 2


class MainWindow(QMainWindow):

    def __init__(self, app, world):
        super().__init__()

        # Init Statusbar
        self.statusbar = self.statusBar()

        # Init game world object
        self.world = world
        self.worldFrame = WorldFrame(self, world)
        self.setCentralWidget(self.worldFrame)
        self.worldFrame.msg2Statusbar[str].connect(self.statusbar.showMessage)

        # Init menubar
        exitAct = QAction(Icon(self, 'SP_MessageBoxCritical'), '&Exit', self)
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(app.quit)

        resetAct = QAction(Icon(self, 'SP_BrowserReload'), '&Reset Viewport', self)
        resetAct.setStatusTip('Reset the viewport to default view')
        resetAct.triggered.connect(self.worldFrame.resetViewport)

        self.menubar = self.menuBar()
        fileMenu = self.menubar.addMenu('&File')
        fileMenu.addAction(resetAct)
        fileMenu.addAction(exitAct)

        # Add toolbar
        townAct = QAction(QIcon(r"res/icons/town.png"), 'Add Town', self)
        townAct.setStatusTip("Add a new town to the map.")
        townAct.triggered.connect(self.worldFrame.addTownMode)

        self.toolbar = self.addToolBar('Map')
        self.toolbar.addAction(townAct)

        # Init window and show
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('DiscordMUD - Backend Manager')
        self.show()
        self.worldFrame.resetViewport()

    def update(self):
        super().update()
        self.worldFrame.update()


class WorldFrame(QGraphicsView):
    msg2Statusbar = pyqtSignal(str)

    def __init__(self, parent, world):
        super().__init__(parent)
        self.pointerMode = PointerMode.Normal
        scene = QGraphicsScene(self)
        self.world = world
        self.view = WorldView(self, world)
        scene.addItem(self.view)
        self.setScene(scene)
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)

    def resetViewport(self):
        self.view.resetViewport()

    def mouseMoveEvent(self, event):
        point = self.mapToScene(event.x(), event.y())
        ex, ey = point.x(), point.y()
        gridx, gridy = self.view.pixToGrid(ex, ey)
        self.currentGridPoint = (gridx, gridy)
        landmark = " "
        if 0 < gridx < self.world.Width and 0 < gridy < self.world.Height:
            space = self.world.Map[gridy][gridx]
            if space in self.world.Towns or space in self.world.Wilds:
                landmark += space.Name
        self.msg2Statusbar.emit("({}, {}) {}".format(int(gridx), int(gridy), landmark))
        self.update()

    def update(self):
        super().update()
        self.view.update()

    def addTownMode(self, event):
        self.pointerMode = PointerMode.AddTown


class WorldView(QGraphicsObject):
    msg2Statusbar = pyqtSignal(str)

    def __init__(self, parent, world):
        super().__init__()
        self.parent = parent
        self.world = world
        self.resetViewport()

    def boundingRect(self):
        return QRectF(0, 0, 1000, 1000)

    def resetViewport(self):
        self.scale = 1
        self.panX = 0
        self.panY = 0
        self.update()

    def gridToPix(self, x, y):
        rect = self.boundingRect()
        canvasTop = rect.bottom() - self.world.Height * self.squareHeight()
        xcoord, ycoord = rect.left() + self.panX + x * self.squareWidth(), \
                         canvasTop + self.panY + y * self.squareHeight()
        return xcoord, ycoord

    def pixToGrid(self, x, y):
        rect = self.boundingRect()
        canvasTop = rect.bottom() - self.world.Height * self.squareHeight()
        gridx, gridy = (x - rect.left() - self.panX) // self.squareWidth(), \
                       (y - canvasTop - self.panY) // self.squareHeight()
        return int(gridx), int(gridy)

    def squareWidth(self):
        '''returns the width of one square'''

        return int((self.boundingRect().width() / self.world.Width) * self.scale)

    def squareHeight(self):
        '''returns the height of one square'''

        return int((self.boundingRect().height() / self.world.Height) * self.scale)

    def wheelEvent(self, event):
        self.scale += event.delta() / 2880
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

    def paint(self, painter, option, widget):
        dirtpix = QImage(r"res/sprites/grass.png").scaledToWidth(self.squareWidth()).scaledToHeight(self.squareHeight())
        townpix = QImage(r"res/sprites/town.png").scaledToWidth(self.squareWidth()).scaledToHeight(self.squareHeight())
        wildpix = QImage(r"res/sprites/wild.png").scaledToWidth(self.squareWidth()).scaledToHeight(self.squareHeight())
        playerpix = QImage(r"res/sprites/player.png").scaledToWidth(self.squareWidth()).scaledToHeight(
            self.squareHeight())

        # Draw terrain
        for i in range(self.world.Height):
            for j in range(self.world.Width):
                space = self.world.Map[i][j]
                xcoord, ycoord = self.gridToPix(j, i)

                painter.drawImage(xcoord, ycoord, dirtpix)
                if isinstance(space, Town):
                    painter.drawImage(xcoord, ycoord, townpix)
                if isinstance(space, Wilds):
                    painter.drawImage(xcoord, ycoord, wildpix)

        # Draw PCs
        for player in self.world.Users:
            xcoord, ycoord = self.gridToPix(player.Location.X, player.Location.Y)
            painter.drawImage(xcoord, ycoord, playerpix)

        # Draw pointer
        if self.parent.pointerMode == PointerMode.AddTown:
            point = self.parent.currentGridPoint
            xcoord, ycoord = self.gridToPix(*point)
            painter.setOpacity(.5)
            painter.drawImage(xcoord, ycoord, townpix)
