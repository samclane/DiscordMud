import pickle

from PyQt5.QtCore import pyqtSignal, QRectF, Qt
from PyQt5.QtGui import QIcon, QBrush, QColor, QPixmap
from PyQt5.QtWidgets import QMainWindow, QAction, QStyle, QGraphicsView, QGraphicsScene, QGraphicsObject, QFrame

from gamelogic.gamespace import *
from gui.dialogs import AddTownDialog, AddWildsDialog


def Icon(parent, macro):
    """ Convenience method to easily access default Qt Icons """
    return parent.style().standardIcon(getattr(QStyle, macro))


class PointerMode:
    Normal = 0
    Drag = 1
    AddTown = 2
    AddWilds = 3


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
        resetAct = QAction(Icon(self, 'SP_BrowserReload'), '&Reset Viewport', self)
        resetAct.setStatusTip('Reset the viewport to default view')
        resetAct.triggered.connect(self.worldFrame.resetViewport)

        saveAct = QAction(Icon(self, 'SP_DialogSaveButton'), '&Save World', self)
        saveAct.setStatusTip('Save the world object to a file')
        saveAct.triggered.connect(lambda e: pickle.dump(self.world, open("world.p", "wb")))

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
        townAct.triggered.connect(lambda e: self.worldFrame.changePointerMode(PointerMode.AddTown))

        wildsAct = QAction(QIcon(r"res/icons/wild.png"), 'Add Wilds', self)
        wildsAct.setStatusTip("Add a new wild square to the map.")
        wildsAct.triggered.connect(lambda e: self.worldFrame.changePointerMode(PointerMode.AddWilds))

        self.toolbar = self.addToolBar('Map')
        self.toolbar.addAction(townAct)
        self.toolbar.addAction(wildsAct)

        # Init window and show
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('DiscordMUD - Backend Manager')
        self.setWindowIcon(QIcon(r"res/icons/dungeon-gate.png"))
        self.show()
        self.worldFrame.resetViewport()

    def update(self):
        super().update()
        self.worldFrame.update()

    def resizeEvent(self, event):
        self.worldFrame.fitInView()


class WorldFrame(QGraphicsView):
    msg2Statusbar = pyqtSignal(str)

    def __init__(self, parent, world):
        super().__init__(parent)
        self._zoom = 0
        self._scene = QGraphicsScene(self)
        self._world = world
        self._worldview = WorldView(self, world)
        self._scene.addItem(self._worldview)
        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)
        self.pointerMode = PointerMode.Normal
        self.setCacheMode(QGraphicsView.CacheBackground)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def fitInView(self, scale=True):
        rect = QRectF(self._worldview.boundingRect())
        if not rect.isNull():
            self.setSceneRect(rect)
            unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            viewrect = self.viewport().rect()
            scenerect = self.transform().mapRect(rect)
            factor = min(viewrect.width() / scenerect.width(),
                         viewrect.height() / scenerect.height())
            self.scale(factor, factor)
            self._zoom = 0

    def resetViewport(self):
        self.fitInView()
        self.update()

    def mouseMoveEvent(self, event):
        point = self.mapToScene(event.x(), event.y())
        ex, ey = point.x(), point.y()
        gridx, gridy = self._worldview.pixToGrid(ex, ey)
        self.currentGridPoint = (gridx, gridy)
        landmark = " "
        players = " "
        if 0 < gridx < self._world.Width and 0 < gridy < self._world.Height:
            space = self._world.Map[gridy][gridx]
            if space in self._world.Towns or space in self._world.Wilds:
                landmark += space.Name
            for p in self._world.Players:
                if p.Location == space:
                    players += p.Name + " "
        self.msg2Statusbar.emit("({}, {}) {} [{}]".format(int(gridx), int(gridy), landmark, players))
        self.update()
        super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 1.25
            self._zoom += 1
        else:
            factor = 0.8
            self._zoom -= 1
        if self._zoom > 0:
            self.scale(factor, factor)
        elif self._zoom == 0:
            self.fitInView()
        else:
            self._zoom = 0

    def update(self):
        super().update()
        self._worldview.update()

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
            self.pointerMode = PointerMode.Normal
        else:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.pointerMode = PointerMode.Drag

    def changePointerMode(self, mode):
        self.pointerMode = mode

    def mousePressEvent(self, event):
        if event.buttons() & Qt.MiddleButton:
            self.toggleDragMode()
        elif event.buttons() & Qt.LeftButton:
            if self.pointerMode == PointerMode.AddTown:
                dialog = AddTownDialog(self, self.currentGridPoint)
                if dialog.exec_():
                    town = dialog.returnData
                    self._world.addTown(town)
                    if dialog.isStartingTown:
                        self._world.StartingTown = town
                self.pointerMode = PointerMode.Normal
            if self.pointerMode == PointerMode.AddWilds:
                dialog = AddWildsDialog(self, self.currentGridPoint)
                if dialog.exec_():
                    self._world.addWilds(dialog.returnData)
                self.pointerMode = PointerMode.Normal
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
            self.pointerMode = PointerMode.Normal
        super().mouseReleaseEvent(event)


class WorldView(QGraphicsObject):
    msg2Statusbar = pyqtSignal(str)

    def __init__(self, parent, world):
        super().__init__()
        self.parent = parent
        self.world = world
        self.spritemap = {}
        self.spritemap['dirt'] = QPixmap(r"res/sprites/dirt.png")
        self.spritemap['town'] = QPixmap(r"res/sprites/town.png")
        self.spritemap['wild'] = QPixmap(r"res/sprites/wild.png")
        self.spritemap['player'] = QPixmap(r"res/sprites/player.png")
        self.spritemap['water'] = QPixmap(r"res/sprites/water.png")

    def boundingRect(self):
        return QRectF(0, 0, 1000, 1000)

    def gridToPix(self, x, y):
        rect = self.boundingRect()
        canvasTop = rect.bottom() - self.world.Height * self.squareHeight()
        xcoord, ycoord = rect.left() + x * self.squareWidth(), \
                         canvasTop + y * self.squareHeight()
        return xcoord, ycoord

    def pixToGrid(self, x, y):
        rect = self.boundingRect()
        canvasTop = rect.bottom() - self.world.Height * self.squareHeight()
        gridx, gridy = (x - rect.left()) // self.squareWidth(), \
                       (y - canvasTop) // self.squareHeight()
        return int(gridx), int(gridy)

    def squareWidth(self):
        '''returns the width of one square'''

        return int((self.boundingRect().width() / self.world.Width))

    def squareHeight(self):
        '''returns the height of one square'''

        return int((self.boundingRect().height() / self.world.Height))

    def paint(self, painter, option, widget):
        spritemap = {}
        for key, value in self.spritemap.items():
            spritemap[key] = value.scaled(self.squareWidth(), self.squareHeight(), Qt.KeepAspectRatio)

        # painter.drawTiledPixmap(self.boundingRect(), dirtpix, QPointF(0, 0)) # faster but less precise
        # Draw terrain
        for i in range(self.world.Height):
            for j in range(self.world.Width):
                space = self.world.Map[i][j]
                xcoord, ycoord = self.gridToPix(j, i)

                if isinstance(space.Terrain, SandTerrain):
                    painter.drawPixmap(xcoord, ycoord,
                                       spritemap["dirt"])  # TODO Shouldn't have to redraw background every frame
                if isinstance(space.Terrain, WaterTerrain):
                    painter.drawPixmap(xcoord, ycoord,
                                       spritemap["water"])
                if isinstance(space, Town):
                    painter.drawPixmap(xcoord, ycoord, spritemap["town"])
                    if self.world.StartingTown == space:
                        painter.drawRect(xcoord, ycoord, self.squareWidth(), self.squareHeight())
                if isinstance(space, Wilds):
                    painter.drawPixmap(xcoord, ycoord, spritemap["wild"])

        # Draw PCs
        for player in self.world.Players:
            xcoord, ycoord = self.gridToPix(player.Location.X, player.Location.Y)
            painter.drawPixmap(xcoord, ycoord, spritemap["player"])

        # Draw pointers
        if self.parent.pointerMode != PointerMode.Normal:
            point = self.parent.currentGridPoint
            xcoord, ycoord = self.gridToPix(*point)
            painter.setOpacity(.5)
            if self.parent.pointerMode == PointerMode.AddTown:
                painter.drawPixmap(xcoord, ycoord, spritemap["town"])
            elif self.parent.pointerMode == PointerMode.AddWilds:
                painter.drawPixmap(xcoord, ycoord, spritemap["wild"])
