import shotgun_api3  # type: ignore
from PySide6 import QtCore
from os import mkdir

from typing import List, Optional, Any

from src.credentials import Credentials


class ShotgridClient:
    sg: Optional[shotgun_api3.Shotgun] = None
    username: Optional[str] = None

    def logout(self):
        if self.sg is None:
            raise Exception("User is not logged in")

        self.sg.close()  # type: ignore
        self.sg = None

    def login(self, url: str, login: str, password: str):
        self.sg = shotgun_api3.Shotgun(url, login=login, password=password)
        self.username = login

    def getAllTasks(self):
        if self.sg is None:
            raise Exception("User is not logged in")

        user = self.sg.find_one(  # type: ignore
            'HumanUser', [['login', 'contains', self.username]])

        if user is None or user.get('id') is None:  # type: ignore
            raise Exception(
                'Could not find a HumanUser with the login: ' + str(self.username))

        filters = [  # type: ignore
            ['task_assignees', 'is', {'type': 'HumanUser', 'id': user['id']}]
        ]

        d: Any = self.sg.find(  # type: ignore
            "Task", filters, fields=['content', 'due_date'],
            order=[
                {'field_name': 'due_date', 'direction': 'asc'}
            ])
        # print(d)
        return d

    def getTask(self, taskId: int) -> Any:
        if self.sg is None:
            raise Exception("User is not logged in")

        task = self.sg.find_one("Task", [['id', 'is', taskId]], fields=[  # type: ignore
                                'sg_versions', 'project'])
        return task  # type: ignore

    def getAllPublishedFiles(self, versionId: int) -> List[Any]:
        if self.sg is None:
            raise Exception("User is not logged in")

        version = self.sg.find_one("Version", [['id', 'is', versionId]],  # type: ignore
                                   fields=['published_files']
                                   )
        return version['published_files']  # type: ignore

    def getFileUrls(self, versionId: int) -> Any:
        if self.sg is None:
            raise Exception("User is not logged in")

        attachments = self.sg.find("Attachment", [['attachment_links', 'is', {'type': 'Version', 'id': versionId}]],  # type: ignore
                                   fields=['this_file']
                                   )

        return list(
            map(lambda attachment: attachment['this_file'], attachments))  # type: ignore

    def downloadFile(self, file: object, location: str):
        if self.sg is None:
            raise Exception("User is not logged in")

        self.sg.download_attachment(file, file_path=location)  # type: ignore

    def createNewVersion(self, taskId: int, projectId: int, versionName: str) -> Any:
        if self.sg is None:
            raise Exception("User is not logged in")

        print(taskId, projectId, versionName)

        return self.sg.create("Version", {  # type: ignore
            'project': {'type': 'Project', 'id': projectId},
            'code': versionName,
            'sg_task': {'type': 'Task', 'id': taskId}
        })

    def uploadFile(self, entityId: int, filepath: str):
        if self.sg is None:
            raise Exception("User is not logged in")

        displayName = filepath.split('/').pop()
        self.sg.upload("Version", entityId, filepath, field_name="sg_uploaded_movie",  # type: ignore
                       display_name=displayName)


class Signals(QtCore.QObject):
    error = QtCore.Signal(Exception)
    result = QtCore.Signal(object)


def buildDir(*dir: str):
    tail = ''
    for name in dir:
        tail += name + '/'
        try:
            mkdir(tail)
        except FileExistsError:
            pass

    return tail


class DownloadAllFiles(QtCore.QRunnable):
    client: ShotgridClient
    taskId: int
    taskName: str
    outDir: str
    signals: Signals

    def __init__(self, client: ShotgridClient, taskId: int, taskName: str, outDir: str) -> None:
        super(DownloadAllFiles, self).__init__()
        self.client = client
        self.taskId = taskId
        self.taskName = taskName
        self.outDir = outDir
        self.signals = Signals()

    @QtCore.Slot()
    def run(self):
        try:
            versions = self.client.getTask(
                self.taskId)['sg_versions']  # type: ignore

            for version in versions:
                files = self.client.getFileUrls(version['id'])
                versionName = version['name']
                dir = buildDir(self.outDir, 'tasks', self.taskName,
                               'versions', versionName)

                for file in files:
                    filename = file['name']
                    filepath = dir + filename
                    self.client.downloadFile(file, filepath)

            self.signals.result.emit(versions)
        except Exception as e:
            self.signals.error.emit(str(e))


class UploadFiles(QtCore.QRunnable):
    client: ShotgridClient
    signals: Signals
    taskId: int
    path: str

    def __init__(self, client: ShotgridClient, taskId: int, path: str) -> None:
        super().__init__()
        self.client = client
        self.signals = Signals()
        self.taskId = taskId
        self.path = path

    @QtCore.Slot()
    def run(self):
        try:
            y = self.client.getTask(self.taskId)
            print(y)

            displayName = self.path.split('/').pop()
            x = self.client.createNewVersion(
                self.taskId, y['project']['id'], displayName)
            print(x)

            self.client.uploadFile(x['id'], self.path)
            self.signals.result.emit(self.path)
        except Exception as e:
            self.signals.error.emit(str(e))


class GetShotGridTasks(QtCore.QRunnable):
    client: ShotgridClient
    signals: Signals

    def __init__(self, client: ShotgridClient) -> None:
        super(GetShotGridTasks, self).__init__()
        self.client = client
        self.signals = Signals()

    @QtCore.Slot()
    def run(self):
        try:
            result = self.client.getAllTasks()
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))


class ShotGridLogin(QtCore.QRunnable):
    client: ShotgridClient
    credentials: Credentials
    signals: Signals

    def __init__(self, client: ShotgridClient, credentials: Credentials) -> None:
        super(ShotGridLogin, self).__init__()
        self.client = client
        self.credentials = credentials
        self.signals = Signals()

    @QtCore.Slot()
    def run(self):
        try:
            self.client.login(
                url=self.credentials.url,
                login=self.credentials.username,
                password=self.credentials.password,
            )
            self.signals.result.emit(None)
        except Exception as e:
            self.signals.error.emit(e)
