""" Future home of the PyQt5 GUI """
from PyQt5.QtCore import pyqtSignal, Qt, QRectF
from PyQt5.QtGui import QIcon, QImage, QBrush, QColor
from PyQt5.QtWidgets import QMainWindow, QAction, QStyle, QGraphicsView, QGraphicsScene, QGraphicsObject, QFrame

from gamelogic.gamespace import Town, Wilds
from gui.dialogs import AddTownDialog, AddWildsDialog


def Icon(parent, macro):
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
        if 0 < gridx < self._world.Width and 0 < gridy < self._world.Height:
            space = self._world.Map[gridy][gridx]
            if space in self._world.Towns or space in self._world.Wilds:
                landmark += space.Name
        self.msg2Statusbar.emit("({}, {}) {}".format(int(gridx), int(gridy), landmark))
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
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.pointerMode = PointerMode.Drag

    def changePointerMode(self, mode):
        self.pointerMode = mode

    def mousePressEvent(self, event):
        if self.pointerMode == PointerMode.AddTown:
            dialog = AddTownDialog(self, self.currentGridPoint)
            if dialog.exec_():
                self._world.addTown(dialog.returnData)
            self.pointerMode = PointerMode.Normal
        if self.pointerMode == PointerMode.AddWilds:
            dialog = AddWildsDialog(self, self.currentGridPoint)
            if dialog.exec_():
                self._world.addWilds(dialog.returnData)
            self.pointerMode = PointerMode.Normal


class WorldView(QGraphicsObject):
    msg2Statusbar = pyqtSignal(str)

    def __init__(self, parent, world):
        super().__init__()
        self.parent = parent
        self.world = world
        self.dirtpix = QImage(r"res/sprites/grass.png")
        self.townpix = QImage(r"res/sprites/town.png")
        self.wildpix = QImage(r"res/sprites/wild.png")
        self.playerpix = QImage(r"res/sprites/player.png")

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
        dirtpix = self.dirtpix.scaledToWidth(self.squareWidth()).scaledToHeight(self.squareHeight())
        townpix = self.townpix.scaledToWidth(self.squareWidth()).scaledToHeight(self.squareHeight())
        wildpix = self.wildpix.scaledToWidth(self.squareWidth()).scaledToHeight(self.squareHeight())
        playerpix = self.playerpix.scaledToWidth(self.squareWidth()).scaledToHeight(
            self.squareHeight())

        # Draw terrain
        for i in range(self.world.Height):
            for j in range(self.world.Width):
                space = self.world.Map[i][j]
                xcoord, ycoord = self.gridToPix(j, i)

                painter.drawImage(xcoord, ycoord, dirtpix)  # TODO Shouldn't have to redraw background every frame
                if isinstance(space, Town):
                    painter.drawImage(xcoord, ycoord, townpix)
                if isinstance(space, Wilds):
                    painter.drawImage(xcoord, ycoord, wildpix)

        # Draw PCs
        for player in self.world.Users:
            xcoord, ycoord = self.gridToPix(player.Location.X, player.Location.Y)
            painter.drawImage(xcoord, ycoord, playerpix)

        # Draw pointers
        if self.parent.pointerMode != PointerMode.Normal:
            point = self.parent.currentGridPoint
            xcoord, ycoord = self.gridToPix(*point)
            painter.setOpacity(.5)
            if self.parent.pointerMode == PointerMode.AddTown:
                painter.drawImage(xcoord, ycoord, townpix)
            elif self.parent.pointerMode == PointerMode.AddWilds:
                painter.drawImage(xcoord, ycoord, wildpix)
