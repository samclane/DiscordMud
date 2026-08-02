"""Headless check that middle-mouse-drag pans the WorldFrame."""
import logging
import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PyQt5.QtCore import QEvent, QPointF, Qt
    from PyQt5.QtGui import QMouseEvent
    from PyQt5.QtWidgets import QApplication, QWidget

    from gui import graphics
except ImportError as e:  # no Qt platform libs (bare CI containers)
    raise unittest.SkipTest("Qt unavailable: {}".format(e))

from gamelogic.gamespace import World, Town, MiningIndustry


def mouse(type_, pos, button, buttons):
    return QMouseEvent(type_, QPointF(*pos), button, buttons, Qt.NoModifier)


class PanTest(unittest.TestCase):

    def setUp(self):
        self.app = QApplication.instance() or QApplication([])
        world = World("Testworld", 50, 50)
        world.addTown(Town(5, 3, "Braxton", 53, MiningIndustry()), True)
        self.parent = QWidget()  # held: dropping it deletes the child WorldFrame
        self.parent.logger = logging.Logger("test")
        self.frame = graphics.WorldFrame(self.parent, world)
        self.frame.resize(200, 200)
        self.frame.show()

    def scrollPos(self):
        return self.frame.horizontalScrollBar().value(), self.frame.verticalScrollBar().value()

    def test_middle_drag_pans(self):
        start = self.scrollPos()
        self.frame.mousePressEvent(mouse(QEvent.MouseButtonPress, (150, 150), Qt.MiddleButton, Qt.MiddleButton))
        self.assertEqual(graphics.PointerMode.Drag, self.frame.pointerMode)
        self.frame.mouseMoveEvent(mouse(QEvent.MouseMove, (100, 100), Qt.NoButton, Qt.MiddleButton))
        panned = self.scrollPos()
        self.assertNotEqual(start, panned)

        self.frame.mouseReleaseEvent(mouse(QEvent.MouseButtonRelease, (100, 100), Qt.MiddleButton, Qt.NoButton))
        self.assertEqual(graphics.PointerMode.Normal, self.frame.pointerMode)
        # Hovering after the release must not keep panning.
        self.frame.mouseMoveEvent(mouse(QEvent.MouseMove, (10, 10), Qt.NoButton, Qt.NoButton))
        self.assertEqual(panned, self.scrollPos())


if __name__ == "__main__":
    unittest.main()
