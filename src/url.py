from PySide6 import QtCore, QtWidgets
from typing import Optional

from src.credentials import NullableCredentials

class ShotgridUrl(QtWidgets.QWidget):
    next = QtCore.Signal()

    url: QtWidgets.QLineEdit
    nextButton: QtWidgets.QPushButton

    def __init__(self, credentials: Optional[NullableCredentials]):
        super(ShotgridUrl, self).__init__()

        instructions = QtWidgets.QLabel("What is your Shotgrid sub domain?")
        url = (credentials and credentials.url) or "https://.shotgrid.autodesk.com/"
        self.url = QtWidgets.QLineEdit(url)
        self.url.textEdited.connect(self.textChanged)
        self.url.setCursorPosition(8)
        if credentials is not None and credentials.url is not None:
            self.url.setStyleSheet("border: 1px solid darkgreen; border-radius: 4px;")
        # self.url.setMaximumWidth(800)

        self.nextButton = QtWidgets.QPushButton("Log In")
        self.nextButton.clicked.connect(self.click)
        policy = QtWidgets.QSizePolicy()
        policy.setRetainSizeWhenHidden(True)
        self.nextButton.setSizePolicy(policy)
        if (credentials and credentials.url) is None:
            self.nextButton.hide()

        hiddenElement = QtWidgets.QPushButton("Log In")
        hiddenElement.setSizePolicy(policy)
        hiddenElement.hide()

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.nextButton, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        layout.addStretch()
        layout.addWidget(instructions, alignment=QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignBottom)
        # self.layout.addSpacing(10)
        layout.addWidget(self.url, alignment=QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignTop)
        layout.addStretch()
        layout.addWidget(hiddenElement, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

    def textChanged(self, text: str):
        t = text.strip()
        if t.endswith(".shotgrid.autodesk.com/") and t.startswith('https://') and t.find(" ") == -1:
            self.url.setStyleSheet("border: 1px solid darkgreen; border-radius: 4px;")
            self.nextButton.setVisible(True)
        else:
            self.url.setStyleSheet("border: 1px solid darkred; border-radius: 4px;")
            self.nextButton.setVisible(False)

    def click(self):
        self.next.emit()