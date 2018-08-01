import logging

from PyQt5.QtCore import pyqtSignal, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QPixmap
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsObject, QFrame

from gamelogic.gamespace import *
from gui.dialogs import AddTownDialog, AddWildsDialog


class PointerMode:
    Normal = 0
    Drag = 1
    AddTown = 2
    AddWilds = 3


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

        self.logger = parent.logger

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
        try:
            self.currentGridPoint = self._worldview.pixToGrid(ex, ey)
        except IndexError:
            self.currentGridPoint = Space(0, 0, Terrain())
        gridx, gridy = self.currentGridPoint
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
        self.spritemap = dict()
        self.spritemap['dirt'] = QPixmap(r"res/sprites/dirt.png")
        self.spritemap['town'] = QPixmap(r"res/sprites/town.png")
        self.spritemap['wild'] = QPixmap(r"res/sprites/wild.png")
        self.spritemap['player'] = QPixmap(r"res/sprites/player.png")
        self.spritemap['water'] = QPixmap(r"res/sprites/water.png")

    def boundingRect(self) -> QRectF:
        width = self.squareWidth() * self.world.Width
        height = self.squareHeight() * self.world.Height
        return QRectF(0, 0, width, height)

    def gridToPix(self, x, y) -> (int, int):
        rect = self.boundingRect()
        canvasTop = rect.bottom() - self.world.Height * self.squareHeight()
        xcoord, ycoord = rect.left() + x * self.squareWidth(), \
                         canvasTop + y * self.squareHeight()
        return xcoord, ycoord

    def pixToGrid(self, x, y) -> Space:
        rect = self.boundingRect()
        canvasTop = rect.bottom() - self.world.Height * self.squareHeight()
        gridx, gridy = (x - rect.left()) // self.squareWidth(), \
                       (y - canvasTop) // self.squareHeight()
        return self.world.Map[int(gridy)][int(gridx)]

    def squareWidth(self) -> int:
        '''returns the width of one square'''

        return self.spritemap['dirt'].width()

    def squareHeight(self) -> int:
        '''returns the height of one square'''

        return self.spritemap['dirt'].height()

    def paint(self, painter, option, widget):
        # painter.drawTiledPixmap(self.boundingRect(), dirtpix, QPointF(0, 0)) # faster but less precise
        # Draw terrain
        for i in range(self.world.Height):
            for j in range(self.world.Width):
                space = self.world.Map[i][j]
                xcoord, ycoord = self.gridToPix(j, i)

                if isinstance(space.Terrain, SandTerrain):
                    painter.drawPixmap(xcoord, ycoord,
                                       self.spritemap["dirt"])  # TODO Shouldn't have to redraw background every frame
                if isinstance(space.Terrain, WaterTerrain):
                    painter.drawPixmap(xcoord, ycoord,
                                       self.spritemap["water"])
                if isinstance(space, Town):
                    if space.Underwater:
                        painter.setOpacity(.25)
                    painter.drawPixmap(xcoord, ycoord, self.spritemap["town"])
                    painter.setOpacity(1)
                    if self.world.StartingTown == space:
                        painter.drawRect(xcoord, ycoord, self.squareWidth(), self.squareHeight())
                if isinstance(space, Wilds):
                    painter.drawPixmap(xcoord, ycoord, self.spritemap["wild"])

        # Draw PCs
        for player in self.world.Players:
            xcoord, ycoord = self.gridToPix(player.Location.X, player.Location.Y)
            painter.drawPixmap(xcoord, ycoord, self.spritemap["player"])

        # Draw pointers
        if self.parent.pointerMode != PointerMode.Normal:
            point = self.parent.currentGridPoint
            xcoord, ycoord = self.gridToPix(*point)
            painter.setOpacity(.5)
            if self.parent.pointerMode == PointerMode.AddTown:
                painter.drawPixmap(xcoord, ycoord, self.spritemap["town"])
            elif self.parent.pointerMode == PointerMode.AddWilds:
                painter.drawPixmap(xcoord, ycoord, self.spritemap["wild"])
