import logging

from PyQt5.QtWidgets import QPlainTextEdit


class QPlainTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()

        self.widget = QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        # self.widget.textCursor().appendPlainText(msg)
        self.widget.appendPlainText(msg)
        self.widget.appendPlainText("\n")

    def write(self, m):
        pass
