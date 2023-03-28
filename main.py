from dataclasses import asdict
import sys
import json
from typing import Optional
from PySide6 import QtCore, QtWidgets
from src.credentials import Credentials, NullableCredentials

from src.login import LoginForm
from src.tasks import TasksPage
from src.toast import Toast
from src.url import ShotgridUrl


class Window(QtWidgets.QMainWindow):
    shotgridUrlForm: ShotgridUrl
    login: LoginForm
    tasksWidget: TasksPage
    frames: QtWidgets.QStackedLayout

    def __init__(self, credentials: Optional[NullableCredentials]):
        super(Window, self).__init__()
        self.createWidgets(credentials)

        if credentials is None or credentials.url is None:
            return

        self.advance()

        if credentials.password is None or credentials.username is None:
            return

        self.loginUser()

    def createWidgets(self, credentials: Optional[NullableCredentials]):
        self.setWindowTitle("Challenge 1 - Workflow")

        self.shotgridUrlForm = ShotgridUrl(credentials)
        self.shotgridUrlForm.next.connect(self.advance)

        self.login = LoginForm(credentials=credentials)
        self.login.previous.connect(self.backtrack)
        self.login.next.connect(self.loginUser)

        self.tasks = TasksPage()

        self.frames = QtWidgets.QStackedLayout()
        self.frames.addWidget(self.shotgridUrlForm)
        self.frames.addWidget(self.login)
        self.frames.addWidget(self.tasks)

        holder = QtWidgets.QWidget()
        holder.setLayout(self.frames)
        self.setCentralWidget(holder)

    def getCredentials(self):
        return Credentials(
            url=self.shotgridUrlForm.url.text(),
            username=self.login.username.text(),
            password=self.login.password.text()
        )

    def saveCredentials(self):
        with open(".config.json", 'w') as file:
            file.write(
                json.dumps(
                    asdict(
                        self.getCredentials())))

    @QtCore.Slot()
    def loginUser(self):
        self.advance()

        self.tasks.successfulLogin.connect(self.backtrackOnFailure)
        self.tasks.loginUser(self.getCredentials())

    @QtCore.Slot(bool)
    def backtrackOnFailure(self, success: bool):
        self.tasks.successfulLogin.disconnect(self.backtrackOnFailure)
        if not success:
            return self.backtrack()

        self.saveCredentials()

    @QtCore.Slot()
    def advance(self):
        index = self.frames.currentIndex()
        if index >= self.frames.count() - 1:
            return Toast(self).error("Cannot go further forward")

        self.frames.setCurrentIndex(index + 1)

    @QtCore.Slot()
    def backtrack(self):
        index = self.frames.currentIndex()
        if index <= 0:
            return Toast(self).error("Cannot go further backward")

        self.frames.setCurrentIndex(index - 1)


def loadConfig():
    open(".config.json", 'a')   # Hack to create file if it doesn't exist
    with open('.config.json', 'r') as file:
        userConfigFile = file.read()

    if len(userConfigFile) <= 2:
        return None

    try:
        userConfigJson = json.loads(userConfigFile)
    except:
        return None

    url = userConfigJson.get('url')
    username = userConfigJson.get('username')
    password = userConfigJson.get('password')

    return NullableCredentials(url, username, password)


if __name__ == "__main__":
    config = loadConfig()
    app = QtWidgets.QApplication([])

    widget = Window(config)
    widget.resize(840, 620)
    widget.show()

    sys.exit(app.exec())
