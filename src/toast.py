from PySide6 import QtWidgets

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