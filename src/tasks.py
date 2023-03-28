from os import getcwd
from typing import Dict
from PySide6 import QtWidgets, QtCore, QtGui

from src.line import QVLine
from src.shotgun import DownloadAllFiles, GetShotGridTasks, ShotGridLogin, ShotgridClient, UploadFiles
from src.toast import Toast
from src.credentials import Credentials


class TaskWidget (QtWidgets.QFrame):
    taskId: int
    taskName: str
    download = QtCore.Signal(int, str, str)
    upload = QtCore.Signal(int, str)

    def __init__(self, taskName: str, dueDate: str, taskId: int) -> None:
        super(TaskWidget, self).__init__()
        self.taskId = taskId
        self.taskName = taskName

        labelWidget = QtWidgets.QLabel("Name: \"" + taskName + "\"")
        dueLabelWidget = QtWidgets.QLabel("Due: " + str(dueDate))

        uploadFileButton = QtWidgets.QPushButton("Upload files")
        uploadFileButton.clicked.connect(self.openFileDialogue)

        downloadAllFilesButton = QtWidgets.QPushButton("Download files")
        downloadAllFilesButton.clicked.connect(self.openDirectoryDialogue)

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(labelWidget, 0, 0)
        layout.addWidget(dueLabelWidget, 1, 0)
        layout.addWidget(QVLine(), 0, 1, 2, 1)
        layout.addWidget(uploadFileButton, 0, 2)
        layout.addWidget(downloadAllFilesButton, 1, 2)

        self.setFixedSize(layout.sizeHint())
        self.setFrameStyle(QtWidgets.QFrame.Shape.Box)

    def openDirectoryDialogue(self):
        cwd = getcwd()
        dir = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Directory Selector", cwd
        )
        self.download.emit(self.taskId, self.taskName, dir)

    def openFileDialogue(self):
        cwd = getcwd()
        file = QtWidgets.QFileDialog.getOpenFileName(  # type: ignore
            self, "File Selector", cwd)
        self.upload.emit(self.taskId, file[0])


class TasksWidget (QtWidgets.QListWidget):
    elements: QtWidgets.QWidget
    download = QtCore.Signal(int, str, str)
    upload = QtCore.Signal(int, str)

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
        item.setFlags(item.flags() & ~(
            QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled))
        self.addItem(item)
        widget = TaskWidget(name, dueDate, id)
        widget.download.connect(self.downloadFiles)
        widget.upload.connect(self.uploadFiles)
        item.setSizeHint(widget.sizeHint())
        self.setItemWidget(item, widget)

    @QtCore.Slot(int, str)
    def downloadFiles(self, id: int, name: str, outDir: str):
        self.download.emit(id, name, outDir)

    @QtCore.Slot(int, str)
    def uploadFiles(self, id: int, path: str):
        self.upload.emit(id, path)


class TasksPage(QtWidgets.QWidget):
    client: ShotgridClient
    threadpool: QtCore.QThreadPool
    successfulLogin = QtCore.Signal(bool)
    tasks: TasksWidget
    stateLabel: QtWidgets.QLabel
    doingIo = False

    def __init__(self):
        super(TasksPage, self).__init__()
        self.client = ShotgridClient()
        self.threadpool = QtCore.QThreadPool()

        title = QtWidgets.QLabel("Shotgrid Client")
        title.setFont(QtGui.QFont("Arial", 25))
        title.setMaximumHeight(50)

        self.stateLabel = QtWidgets.QLabel()
        self.stateLabel.hide()

        self.tasks = TasksWidget()
        self.tasks.download.connect(self.downloadFiles)
        self.tasks.upload.connect(self.uploadFile)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(title, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stateLabel)
        layout.addWidget(self.tasks)

    @QtCore.Slot(int, str)
    def downloadFiles(self, taskId: int, taskName: str, outDir: str):
        if self.doingIo is True:
            return Toast().error("Already performing I/O please wait until the operation is complete before performing another one.")

        self.doingIo = True
        self.stateLabel.setText("Downloading...")
        self.stateLabel.show()

        promise = DownloadAllFiles(self.client, taskId, taskName, outDir)
        promise.signals.result.connect(self.downloadFilesSuccess)
        promise.signals.error.connect(self.downloadFilesFailure)
        self.threadpool.start(promise)  # type: ignore

    @QtCore.Slot(object)
    def downloadFilesSuccess(self):
        self.doingIo = False
        self.stateLabel.hide()
        Toast(self).notify("Download Successful!")

    @QtCore.Slot(Exception)
    def downloadFilesFailure(self, e: Exception):
        self.doingIo = False
        self.stateLabel.hide()
        Toast(self).error("Download Failed: " + str(e))

    @QtCore.Slot(int, str)
    def uploadFile(self, taskId: int, filepath: str):
        if self.doingIo is True:
            return Toast().error("Already performing I/O please wait until the operation is complete before performing another one.")

        self.doingIo = True
        self.stateLabel.setText("Uploading...")
        self.stateLabel.show()

        promise = UploadFiles(self.client, taskId, filepath)
        promise.signals.result.connect(self.uploadFilesSuccess)
        promise.signals.error.connect(self.uploadFilesFailure)
        self.threadpool.start(promise)  # type: ignore

    @QtCore.Slot(object)
    def uploadFilesSuccess(self):
        self.doingIo = False
        self.stateLabel.hide()
        Toast(self).notify("Upload Successful!")

    @QtCore.Slot(Exception)
    def uploadFilesFailure(self, e: Exception):
        self.doingIo = False
        self.stateLabel.hide()
        Toast(self).error("Upload Failed: " + str(e))

    def loginUser(self, credentials: Credentials):
        promise = ShotGridLogin(
            self.client,
            credentials
        )
        self.stateLabel.setText("Logging in.")
        self.stateLabel.show()
        promise.signals.result.connect(self.loginSuccess)
        promise.signals.error.connect(self.loginFailed)
        self.threadpool.start(promise)  # type: ignore

    @QtCore.Slot(object)
    def loginSuccess(self):
        self.stateLabel.setText("Login Successful.\nFetching current tasks.")
        promise = GetShotGridTasks(self.client)
        promise.signals.result.connect(self.getTasksSuccess)
        promise.signals.error.connect(self.getTasksFailed)
        self.threadpool.start(promise)  # type: ignore

    @QtCore.Slot(Exception)
    def loginFailed(self, e: Exception):
        Toast(self).error("Could not log in: " + str(e))
        self.stateLabel.hide()
        self.successfulLogin.emit(False)

    @QtCore.Slot(object)
    def getTasksSuccess(self, result: object):
        self.stateLabel.setText("Retrieved tasks.")
        self.successfulLogin.emit(True)

        if not isinstance(result, list):
            raise Exception()

        for task in result:  # type: ignore
            if not isinstance(task, Dict):
                raise Exception()

            name: str = task["content"]
            dueDate: str = task['due_date']
            id: int = task['id']
            self.tasks.addTask(name, dueDate, id)

        self.stateLabel.hide()

    @QtCore.Slot(Exception)
    def getTasksFailed(self, e: Exception):
        Toast(self).error("Could not get tasks: " + str(e))
        self.stateLabel.hide()
        self.successfulLogin.emit(False)
