from PySide6 import QtWidgets, QtCore
from typing import Optional

from src.credentials import NullableCredentials

class LoginForm(QtWidgets.QWidget):
    next = QtCore.Signal()
    previous = QtCore.Signal()
    username: QtWidgets.QLineEdit
    password: QtWidgets.QLineEdit
    button: QtWidgets.QPushButton

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, credentials: Optional[NullableCredentials] = None):
        super(LoginForm, self).__init__(parent)

        self.username = QtWidgets.QLineEdit()
        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        policy = QtWidgets.QSizePolicy()
        policy.setRetainSizeWhenHidden(True)

        setUrl = QtWidgets.QPushButton("Change URL")
        setUrl.setSizePolicy(policy)
        setUrl.clicked.connect(lambda : self.previous.emit())

        setUrlInvisible = QtWidgets.QPushButton("Change URL")
        setUrlInvisible.setSizePolicy(policy)
        setUrlInvisible.hide()

        self.button = QtWidgets.QPushButton("Log In.")
        self.button.clicked.connect(self.loginUser)

        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.addRow("Username:", self.username)
        self.formLayout.addRow("Password:", self.password)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignBottom)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(setUrl, alignment=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)
        layout.addStretch()
        layout.addLayout(self.formLayout)
        layout.addWidget(self.button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignTop)
        layout.addStretch()
        layout.addWidget(setUrlInvisible, alignment=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)

        if credentials is not None:
            if credentials.username is not None:
                self.username.setText(credentials.username)
            if credentials.password is not None:
                self.password.setText(credentials.password)

    def loginUser(self):
        self.next.emit()