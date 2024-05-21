# -*- coding: utf-8 -*-

"""
Module implementing DeleteNote.
"""

from PyQt5.QtCore import pyqtSlot, QPropertyAnimation, Qt, QPoint, QAbstractAnimation
from PyQt5.QtWidgets import QDialog, QApplication

from Design.PasswordInputDialog_ui import Ui_Dialog


class PasswordInputDialog(QDialog, Ui_Dialog):
    """
    Class documentation goes here.
    """
    def __init__(self, title = "Encrypt Your Note", parent=None):
        super(PasswordInputDialog, self).__init__(parent)
        self.setupUi(self)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        if title:
            self.lblTitle.setText(title)
        self.edtPassword.setFocus()
        self.btnCancel.clicked.connect(self.reject)
        self.btnClose.clicked.connect(self.close)

        
    def vibrate_input(self):
        animation = QPropertyAnimation(self.edtPassword, b"pos")
        original_pos = self.edtPassword.pos()
        
        animation.setDuration(100)
        animation.setLoopCount(2)
        animation.setKeyValueAt(0, original_pos)
        animation.setKeyValueAt(0.25, original_pos + QPoint(5, 0))
        animation.setKeyValueAt(0.5, original_pos - QPoint(5, 0))
        animation.setKeyValueAt(0.75, original_pos + QPoint(5, 0))
        animation.setKeyValueAt(1, original_pos)
        
        animation.start(QAbstractAnimation.DeleteWhenStopped)
        
    @pyqtSlot()
    def on_btnConfirm_clicked(self):
        self.password = self.edtPassword.text()
        if self.password:
            self.accept()
        else:
            self.edtPassword.setFocus()
            self.vibrate_input()