from PyQt5.QtCore import pyqtSignal, QRectF, Qt, QPoint
from PyQt5.QtGui import QBrush, QColor, QPixmap, QPainter, QImage
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
        self.setMouseTracking(True)

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
        super().mouseMoveEvent(event)
        self.update()

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

    def changePointerMode(self, mode):
        self.pointerMode = mode

    def mousePressEvent(self, event):
        if event.buttons() & Qt.MiddleButton:
            self.middleClickEvent(event)
        elif event.buttons() & Qt.LeftButton:
            self.leftClickEvent(event)
        elif event.buttons() & Qt.RightButton:
            self.rightClickEvent(event)
        super().mousePressEvent(event)

    def middleClickEvent(self, event):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
            self.pointerMode = PointerMode.Normal
        else:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.pointerMode = PointerMode.Drag

    def leftClickEvent(self, event):
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

    def rightClickEvent(self, event):
        if self.pointerMode != PointerMode.Normal:
            self.pointerMode = PointerMode.Normal
        self.update()

    def mouseReleaseEvent(self, event):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
            self.pointerMode = PointerMode.Normal
        super().mouseReleaseEvent(event)

    def getBoundingSubrectangle(self, spaces: [Space]) -> QRectF:
        def getTopLeftSpace(spaces):
            minX = min([s.X for s in spaces])
            minY = min([s.Y for s in spaces])
            topLeft = [s for s in spaces if s.X == minX and s.Y == minY][0]
            return topLeft

        def getBottomRightSpace(spaces):
            maxX = max([s.X for s in spaces])
            maxY = max([s.Y for s in spaces])
            botRight = [s for s in spaces if s.X == maxX and s.Y == maxY][0]
            return botRight

        topLeftSpace = getTopLeftSpace(spaces)
        topLeftPix = self.mapFromParent(self._worldview.gridToPix(topLeftSpace.X, topLeftSpace.Y))
        bottomRightSpace = getBottomRightSpace(spaces)
        bottomRightPix = self.mapFromParent(self._worldview.gridToPix(bottomRightSpace.X, bottomRightSpace.Y)) + \
                         QPoint(self._worldview.squareWidth, self._worldview.squareHeight)
        subBoundingRect = QRectF(topLeftPix, bottomRightPix)
        return subBoundingRect

    def saveSubimage(self, spaces: [Space], filename="capture.png"):
        self._scene.clearSelection()
        boundingRect = self.getBoundingSubrectangle(spaces)
        self._scene.setSceneRect(boundingRect)
        pix = QImage(self._scene.sceneRect().size().toSize(), QImage.Format_ARGB32)
        pix.fill(Qt.TransparentMode)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.Antialiasing)
        self._scene.render(painter)
        painter.end()  # Removing will cause silent crash
        pix.save(filename)


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
        self.spritemap['mountain'] = QPixmap(r"res/sprites/mountain.png")
        self.spritemap['base'] = QPixmap(r"res/sprites/base.png")

        self.squareWidth = self.spritemap['dirt'].width()
        self.squareHeight = self.spritemap['dirt'].height()
        self.boundingWidth = self.squareWidth * self.world.Width
        self.boundingHeight = self.squareHeight * self.world.Height

        # Preload mapping from gridworld to GraphicsView
        self.gridToPixMap = [[QPoint(0, 0) for _ in range(self.world.Width)] for _ in range(self.world.Height)]
        rect = self.boundingRect()
        canvasTop = rect.bottom() - self.world.Height * self.squareHeight
        for y in range(self.world.Height):
            for x in range(self.world.Width):
                xcoord, ycoord = rect.left() + x * self.squareWidth, \
                                 canvasTop + y * self.squareHeight
                self.gridToPixMap[y][x] = QPoint(xcoord, ycoord)

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.boundingWidth, self.boundingHeight)

    def gridToPix(self, x: int, y: int) -> QPoint:
        return self.gridToPixMap[y][x]

    def pixToGrid(self, x, y) -> Space:
        rect = self.boundingRect()
        canvasTop = rect.bottom() - self.world.Height * self.squareHeight
        gridx, gridy = (x - rect.left()) // self.squareWidth, \
                       (y - canvasTop) // self.squareHeight
        return self.world.Map[int(gridy)][int(gridx)]

    def paint(self, painter, option, widget):
        for i in range(self.world.Height):
            for j in range(self.world.Width):
                space = self.world.Map[i][j]
                point = self.gridToPix(j, i)
                # Draw terrain
                if space.Terrain.id == SandTerrain.id:
                    painter.drawPixmap(point,
                                       self.spritemap["dirt"])
                if space.Terrain.id == WaterTerrain.id:
                    painter.drawPixmap(point,
                                       self.spritemap["water"])
                if space.Terrain.id == MountainTerrain.id:
                    painter.drawPixmap(point,
                                       self.spritemap["mountain"])
                if isinstance(space, Town):
                    if space.Underwater:
                        painter.setOpacity(.25)
                    if isinstance(space, Base):
                        painter.drawPixmap(point, self.spritemap["base"])
                    else:
                        painter.drawPixmap(point, self.spritemap["town"])
                    painter.setOpacity(1)
                    if self.world.StartingTown == space:
                        painter.drawRect(point.x(), point.y(), self.squareWidth, self.squareHeight)
                if isinstance(space, Wilds):
                    painter.drawPixmap(point, self.spritemap["wild"])

        # Draw PCs
        for player in self.world.Players:
            if player.Location:
                point = self.gridToPix(player.Location.X, player.Location.Y)
                painter.drawPixmap(point, self.spritemap["player"])

        # Draw pointers
        if self.parent.pointerMode != PointerMode.Normal:
            point = self.parent.currentGridPoint
            pixPoint = self.gridToPix(*point)
            painter.setOpacity(.5)
            if self.parent.pointerMode == PointerMode.AddTown:
                painter.drawPixmap(pixPoint, self.spritemap["town"])
            elif self.parent.pointerMode == PointerMode.AddWilds:
                painter.drawPixmap(pixPoint, self.spritemap["wild"])

        if hasattr(self.parent, "currentGridPoint"):  # Draw grid cursor if mouse is on self
            painter.drawRect(
                self.parent.getBoundingSubrectangle(self.world.getAdjacentSpaces(self.parent.currentGridPoint, 0)))
