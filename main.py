import sys
import random
from typing import List, Optional
from dataclasses import dataclass

from PySide6 import QtCore, QtWidgets, QtGui

@dataclass
class Credentials:
    username: str
    pasword: str

class LoginForm(QtWidgets.QWidget):
    onLogin = QtCore.Signal(Credentials)
    username: QtWidgets.QLineEdit
    password: QtWidgets.QLineEdit
    button: QtWidgets.QPushButton

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super(LoginForm, self).__init__(parent)

        self.username = QtWidgets.QLineEdit()
        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        self.button = QtWidgets.QPushButton("Log In.")
        self.button.clicked.connect(self.loginUser)

        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.addRow("Username:", self.username)
        self.formLayout.addRow("Password:", self.password)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignBottom)

        self.layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.Down, self)
        self.layout.addLayout(self.formLayout)
        self.layout.addWidget(self.button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter | QtCore.Qt.AlignmentFlag.AlignTop)

        # self.setContentsMargins(100, 100, 100, 100)
        # self.setFrameStyle(QtWidgets.QFrame.Shadow.Sunken | QtWidgets.QFrame.Shape.StyledPanel)
        # self.setLineWidth(1)

        # self.setFrameStyle("margin: 5px;")
        # self.setMaximumHeight(self.height() / 2)
        # self.setMargin(self.width() / 2)
        # self.resize(self.sizeHint())
        # self.setFrameShape()
        # self.setFrameStyle(QtCore. QFrame::Panel | QFrame::Raised);

    def loginUser(self):
        self.onLogin.emit(
            Credentials(
                username=self.username.text(),
                pasword=self.password.text()
            )
        )


class Core (QtWidgets.QWidget):
    logout = QtCore.Signal()


class MyApp (QtWidgets.QMainWindow):
    credentials: Optional[Credentials] = None
    login: LoginForm

    def __init__(self):
        super(MyApp, self).__init__()
        self.setWindowTitle("Challenge 1 - Workflow")

        self.login = LoginForm()
        self.login.onLogin.connect(self.setCredentials)
        self.setCentralWidget(self.login)

    @QtCore.Slot(Credentials)
    def setCredentials(self, credentials: Credentials):
        self.credentials = credentials
        print(self.credentials)
        self.login.deleteLater()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyApp()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec())