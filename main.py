from enum import Enum
import sys
import json
from typing import Optional, Dict

from PySide6 import QtCore, QtWidgets, QtGui
from src.credentials import Credentials, NullableCredentials

from src.shotgun import DownloadAllFiles, ShotgridClient, ShotGridLogin, GetShotGridTasks

class Toast(QtWidgets.QWidget):
    def error(self, text: str):
        dlg = QtWidgets.QMessageBox(self)
        dlg.setText(text)
        dlg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Close)
        dlg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        dlg.exec()

    def notify(self, text: str):
        dlg = QtWidgets.QMessageBox(self)
        dlg.setText(text)
        dlg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Close)
        dlg.setIcon(QtWidgets.QMessageBox.Icon.Information)
        dlg.exec()

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

    

class QVLine(QtWidgets.QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

class TaskWidget (QtWidgets.QFrame):
    taskId: int
    download = QtCore.Signal(int, str)

    def __init__(self, taskName: str, dueDate: str, taskId: int) -> None:
        super(TaskWidget, self).__init__()
        self.taskId = taskId

        labelWidget = QtWidgets.QLabel("Name: \"" + taskName + "\"")
        dueLabelWidget = QtWidgets.QLabel("Due: " + dueDate)
        uploadNewVersionButton = QtWidgets.QPushButton("Upload files")
        downloadAllFilesButton = QtWidgets.QPushButton("Download files")
        downloadAllFilesButton.clicked.connect(lambda: self.download.emit(self.taskId, taskName))

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(labelWidget, 0, 0)
        layout.addWidget(dueLabelWidget, 1, 0)
        layout.addWidget(QVLine(), 0, 1, 2, 1)
        layout.addWidget(uploadNewVersionButton, 0, 2)
        layout.addWidget(downloadAllFilesButton, 1, 2)

        self.setFixedSize(layout.sizeHint())

        self.setFrameStyle( QtWidgets.QFrame.Shape.Box )

class TasksWidget (QtWidgets.QListWidget):
    elements: QtWidgets.QWidget
    download = QtCore.Signal(int, str)

    def __init__(self):
        super(TasksWidget, self).__init__()
        self.viewport().setBackgroundRole(QtGui.QPalette.ColorRole.Window)
        self.setFlow(self.Flow.LeftToRight)
        self.setWrapping(True)
        self.setMovement(self.Movement.Static)

        self.setResizeMode(self.ResizeMode.Adjust)

        self.setHorizontalScrollMode(self.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollMode(self.ScrollMode.ScrollPerPixel)
        self.setSpacing(4)

        self.setFrameStyle(QtWidgets.QFrame.Shape.NoFrame)

    def addTask(self, name: str, dueDate: str, id: int):
        item = QtWidgets.QListWidgetItem()
        item.setFlags(item.flags() & ~(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled))
        self.addItem(item)
        widget = TaskWidget(name, dueDate, id)
        widget.download.connect(self.downloadFiles)
        item.setSizeHint(widget.sizeHint())
        self.setItemWidget(item, widget)

    @QtCore.Slot(int, str)
    def downloadFiles(self, id: int, name: str):
        self.download.emit(id, name)

class TasksPage(QtWidgets.QWidget):
    client: ShotgridClient
    threadpool: QtCore.QThreadPool
    successfulLogin = QtCore.Signal(bool)
    tasks: TasksWidget

    def __init__(self):
        super(TasksPage, self).__init__()
        self.client = ShotgridClient()
        self.threadpool = QtCore.QThreadPool()

        self.tasks = TasksWidget()
        self.tasks.download.connect(self.downloadFiles)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.tasks)

    def loginUser(self, credentials: Credentials):
        promise = ShotGridLogin(
                self.client, 
                credentials
            )
        promise.signals.result.connect(self.loginSuccess)
        promise.signals.error.connect(self.loginFailed)
        self.threadpool.start(promise) # type: ignore

    @QtCore.Slot(int, str)
    def downloadFiles(self, taskId: int, taskName: str):
        print("Downloading...")
        promise = DownloadAllFiles(self.client, taskId, taskName)
        promise.signals.result.connect(self.downloadFilesSuccess)
        promise.signals.error.connect(self.downloadFilesFailure)
        self.threadpool.start(promise)  # type: ignore
    
    QtCore.Slot(int)
    def downloadFilesSuccess(self, result: object):
        Toast(self).notify("Download Successful" + str(result))

    QtCore.Slot(int)
    def downloadFilesFailure(self, e: Exception):
        Toast(self).error("Download Failed: " + str(e))

    @QtCore.Slot(object)
    def loginSuccess(self):
        print("Login Successful")
        promise = GetShotGridTasks(self.client)
        promise.signals.result.connect(self.getTasksSuccess)
        promise.signals.error.connect(self.getTasksFailed)
        self.threadpool.start(promise)  # type: ignore

    @QtCore.Slot(Exception)
    def loginFailed(self, e: Exception):
        Toast(self).error("Could not log in: " + str(e))
        self.successfulLogin.emit(False)

    @QtCore.Slot(object)
    def getTasksSuccess(self, result: object):
        print("Successfully retrieved tasks: " + str(result))
        self.successfulLogin.emit(True)

        if not isinstance(result, list):
            raise Exception()
            
        for task in result: # type: ignore
            if not isinstance(task, Dict):
                raise Exception()

            name: str = task["content"]
            dueDate: str = task['due_date']
            id: int = task['id']
            for _ in range(10):
                self.tasks.addTask(name, dueDate, id)

    @QtCore.Slot(Exception)
    def getTasksFailed(self, e: Exception):
        Toast(self).error("Could not get tasks: " + str(e))
        self.successfulLogin.emit(False)


class AppState(Enum):
    URL = 0
    LOGIN = 1
    APP = 2


class MyApp (QtWidgets.QMainWindow):
    shotgridUrlForm: ShotgridUrl
    login: LoginForm
    tasksWidget: TasksPage
    state: AppState
    frames: QtWidgets.QStackedLayout

    def __init__(self, credentials: Optional[NullableCredentials]):
        super(MyApp, self).__init__()
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

        if credentials is not None:
            if credentials.url is None:
                return

            # Go from URL page to Login Page
            self.advance()

            if credentials.password is None or credentials.username is None:
                return

            self.loginUser()
            
    def backtrackOnFailure(self, success: bool):
        self.tasks.successfulLogin.disconnect(self.backtrackOnFailure)
        if not success:
            self.backtrack()

    @QtCore.Slot()
    def loginUser(self):
        self.advance()

        credentials = Credentials(
            url=self.shotgridUrlForm.url.text(),
            username=self.login.username.text(),
            password=self.login.password.text()
        )
        self.tasks.successfulLogin.connect(self.backtrackOnFailure)
        self.tasks.loginUser(credentials)
        
    def advance(self):
        index = self.frames.currentIndex()
        if index >= self.frames.count() - 1:
            return Toast(self).error("Cannot go further forward")

        self.frames.setCurrentIndex(index + 1)

    def backtrack(self):
        index = self.frames.currentIndex()
        if index <= 0:
            return Toast(self).error("Cannot go further backward")

        self.frames.setCurrentIndex(index - 1)

def loadConfig():
    open(".config.json", 'a')
    with open('.config.json', 'r') as file:
        userConfigFile = file.read()

    userConfig: Optional[NullableCredentials] = None
    if len(userConfigFile) > 0:
        userConfigJson = json.loads(userConfigFile)

        url = userConfigJson.get('url')
        username = userConfigJson.get('username')
        password = userConfigJson.get('password')

        userConfig = NullableCredentials( url, username, password )
    
    return userConfig

if __name__ == "__main__":
    config = loadConfig()
    app = QtWidgets.QApplication([])

    widget = MyApp(config)
    widget.resize(840, 620)
    widget.show()

    sys.exit(app.exec())