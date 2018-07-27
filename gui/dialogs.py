import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QDialogButtonBox, QSpinBox, QComboBox, QHBoxLayout, \
    QVBoxLayout, QCheckBox

from gamelogic import gamespace


class AddWorldDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        nameLabel = QLabel("World &name:")
        self.nameEdit = QLineEdit()
        nameLabel.setBuddy(self.nameEdit)

        widthLabel = QLabel("&Width")
        self.widthEdit = QSpinBox()
        self.widthEdit.setMaximum(100)
        self.widthEdit.setValue(50)
        widthLabel.setBuddy(self.widthEdit)
        heightLabel = QLabel("&Height")
        self.heightEdit = QSpinBox()
        self.heightEdit.setMaximum(100)
        self.heightEdit.setValue(50)
        heightLabel.setBuddy(self.heightEdit)

        okButton = QPushButton("&Ok")
        okButton.setAutoDefault(True)

        cancelButton = QPushButton("&Cancel")
        cancelButton.setDefault(False)

        buttonBox = QDialogButtonBox(Qt.Horizontal)
        buttonBox.addButton(okButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(cancelButton, QDialogButtonBox.ActionRole)

        nameLayout = QHBoxLayout()
        nameLayout.addWidget(nameLabel)
        nameLayout.addWidget(self.nameEdit)

        posLayout = QHBoxLayout()
        posLayout.addWidget(widthLabel)
        posLayout.addWidget(self.widthEdit)
        posLayout.addSpacing(1)
        posLayout.addWidget(heightLabel)
        posLayout.addWidget(self.heightEdit)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(nameLayout)
        mainLayout.addLayout(posLayout)
        mainLayout.addWidget(buttonBox)

        self.setLayout(mainLayout)
        self.setWindowTitle("Create World")
        self.returnData = None
        okButton.clicked.connect(self.onOk)
        cancelButton.clicked.connect(self.reject)
        self.setWindowIcon(QIcon(r"res/icons/dungeon-gate.png"))

    def onOk(self, event):
        self.returnData = gamespace.World(self.nameEdit.text(),
                                          int(self.widthEdit.text()),
                                          int(self.heightEdit.text()))
        self.accept()


class AddTownDialog(QDialog):
    def __init__(self, parent=None, position=None):
        super().__init__(parent)

        nameLabel = QLabel("Town &name:")
        self.nameEdit = QLineEdit()
        nameLabel.setBuddy(self.nameEdit)

        popLabel = QLabel("Population:")
        self.popEdit = QSpinBox()
        self.popEdit.setMaximum(sys.maxsize)
        popLabel.setBuddy(self.popEdit)

        industLabel = QLabel("Industry:")
        self.industList = {sub.Name: sub for sub in gamespace.IndustryType.__subclasses__()}
        self.industCombo = QComboBox()
        self.industCombo.addItems(self.industList.keys())
        industLabel.setBuddy(self.industCombo)

        posXLabel = QLabel("&X Position")
        self.posXEdit = QSpinBox()
        self.posXEdit.setMaximum(parent._world.Width)
        posXLabel.setBuddy(self.posXEdit)
        posYLabel = QLabel("&Y Position")
        self.posYEdit = QSpinBox()
        self.posYEdit.setMaximum(parent._world.Height)
        posYLabel.setBuddy(self.posYEdit)
        if position:
            self.posXEdit.setValue(position[0])
            self.posYEdit.setValue(position[1])

        self.startingCheck = QCheckBox("Starting town?", self)
        if parent._world.StartingTown is None:  # Force first town to be starting town
            self.startingCheck.toggle()
            self.startingCheck.setEnabled(False)

        okButton = QPushButton("&Ok")
        okButton.setAutoDefault(True)

        cancelButton = QPushButton("&Cancel")
        cancelButton.setDefault(False)

        buttonBox = QDialogButtonBox(Qt.Horizontal)
        buttonBox.addButton(okButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(cancelButton, QDialogButtonBox.ActionRole)

        nameLayout = QHBoxLayout()
        nameLayout.addWidget(nameLabel)
        nameLayout.addWidget(self.nameEdit)

        popLayout = QHBoxLayout()
        popLayout.addWidget(popLabel)
        popLayout.addWidget(self.popEdit)

        industLayout = QHBoxLayout()
        industLayout.addWidget(industLabel)
        industLayout.addWidget(self.industCombo)

        posLayout = QHBoxLayout()
        posLayout.addWidget(posXLabel)
        posLayout.addWidget(self.posXEdit)
        posLayout.addSpacing(1)
        posLayout.addWidget(posYLabel)
        posLayout.addWidget(self.posYEdit)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(nameLayout)
        mainLayout.addLayout(popLayout)
        mainLayout.addLayout(industLayout)
        mainLayout.addLayout(posLayout)
        mainLayout.addWidget(self.startingCheck)
        mainLayout.addWidget(buttonBox)

        self.setLayout(mainLayout)
        self.setWindowTitle("Add Town")
        self.returnData = None
        self.isStartingTown = False
        okButton.clicked.connect(self.onOk)
        cancelButton.clicked.connect(self.reject)

    def onOk(self, event):
        self.returnData = gamespace.Town(int(self.posXEdit.value()),
                                         int(self.posYEdit.value()),
                                         self.nameEdit.text(),
                                         int(self.popEdit.text()),
                                         self.industList[self.industCombo.currentText()])
        self.isStartingTown = self.startingCheck.isChecked()
        self.accept()


class AddWildsDialog(QDialog):
    def __init__(self, parent=None, position=None):
        super().__init__(parent)

        nameLabel = QLabel("Wilds &name:")
        self.nameEdit = QLineEdit()
        nameLabel.setBuddy(self.nameEdit)

        posXLabel = QLabel("&X Position")
        self.posXEdit = QSpinBox()
        self.posXEdit.setMaximum(parent._world.Width)
        posXLabel.setBuddy(self.posXEdit)
        posYLabel = QLabel("&Y Position")
        self.posYEdit = QSpinBox()
        self.posYEdit.setMaximum(parent._world.Height)
        posYLabel.setBuddy(self.posYEdit)
        if position:
            self.posXEdit.setValue(position[0])
            self.posYEdit.setValue(position[1])

        okButton = QPushButton("&Ok")
        okButton.setAutoDefault(True)

        cancelButton = QPushButton("&Cancel")
        cancelButton.setDefault(False)

        buttonBox = QDialogButtonBox(Qt.Horizontal)
        buttonBox.addButton(okButton, QDialogButtonBox.ActionRole)
        buttonBox.addButton(cancelButton, QDialogButtonBox.ActionRole)

        nameLayout = QHBoxLayout()
        nameLayout.addWidget(nameLabel)
        nameLayout.addWidget(self.nameEdit)

        posLayout = QHBoxLayout()
        posLayout.addWidget(posXLabel)
        posLayout.addWidget(self.posXEdit)
        posLayout.addSpacing(1)
        posLayout.addWidget(posYLabel)
        posLayout.addWidget(self.posYEdit)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(nameLayout)
        mainLayout.addLayout(posLayout)
        mainLayout.addWidget(buttonBox)

        self.setLayout(mainLayout)
        self.setWindowTitle("Add Town")
        self.returnData = {}
        okButton.clicked.connect(self.onOk)
        cancelButton.clicked.connect(self.reject)

    def onOk(self, event):
        self.returnData = gamespace.Wilds(int(self.posXEdit.text()),
                                          int(self.posYEdit.text()),
                                          self.nameEdit.text())
        self.accept()
