# -*- coding: utf-8 -*-

"""
Module implementing Note.
"""

from PyQt5.QtCore import pyqtSlot, Qt, QTextStream, QFile
from PyQt5.QtWidgets import QWidget, QSizeGrip, QFileDialog, QDialog
from PyQt5.QtGui import QFont, QTextCharFormat, QTextDocumentFragment, QTextListFormat, QIcon, QPainter

from Design.Note_ui import Ui_Note
from CustomWidgets.CDrawer import CDrawer
from CustomWidgets.NoteMenu import NoteMenu
from CustomWidgets.DeleteNoteDialog import DeleteNote
from CustomWidgets.PasswordInputDialog import PasswordInputDialog
from utils.NoteConfig import NoteConfig
from utils.utils import debounce
from utils.constants import CHANGE_TYPE
    
class Note(QWidget, Ui_Note):
    def __init__(self, config, onSaveConfig, parent=None):
        super(Note, self).__init__(parent)
        self.setupUi(self)
        self.newCount = 1
        self.onSaveConfig = onSaveConfig
        self.cryptPassword = None
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.Tool)
        self.initUI(config)
        
        
        def moveWindow(event):
            if event.buttons() == Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.dragPos)
                self.dragPos = event.globalPos()
                event.accept()

        def mouseReleaseEvent(event):
            self.config.posX = self.pos().x()
            self.config.posY = self.pos().y()
            self.updatedConfig()
                
        def mouseDoubleClickEvent(event):
            self.toggleVisible()

        self.frame_title.mouseMoveEvent = moveWindow
        self.frame_title.mouseReleaseEvent = mouseReleaseEvent
        self.frame_title.mouseDoubleClickEvent = mouseDoubleClickEvent
        self.textBrowser.textChanged.connect(self.onTextChanged)
        self.pushButton_lock.clicked.connect(self.toggleLock)

        self.sizegrip = QSizeGrip(self.frame_grip)
        self.sizegrip.setStyleSheet(
            "QSizeGrip { width: 10px; height: 10px; margin: 5px }")
        self.sizegrip.setToolTip("Resize Window")

    def raiseToTop(self):
        # it for always on top
        # self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()
        self.raise_()
        self.activateWindow()
    
    @debounce(2)
    def onChangeConfig(self, _CHANGE):
        print(self.config.key, _CHANGE)
        self.onSaveConfig(self.config, _CHANGE)
    
    def initUI(self, _conf: NoteConfig):
        self.config = _conf
        self.lblTitle.setText(_conf.title)
        self.setBackground(_conf.backgroundIndex)
        self.setGeometry(_conf.posX, _conf.posY, _conf.width, _conf.height)
        self.changeVisibleStatus(_conf.isVisible)
        self.changeLockStatus(_conf.locked)

    def changeVisibleStatus(self, isVisible):
        self.config.isVisible = isVisible
        self.textBrowser.setVisible(isVisible)
        self.frame_buttom.setVisible(isVisible)
    
    def changeLockStatus(self, isLocked):
        self.config.locked = isLocked
        if isLocked:
            self.pushButton_lock.setIcon(QIcon(':/resources/lock.svg'))
        else:
            self.pushButton_lock.setIcon(QIcon(':/resources/unlock.svg'))
        self.changeVisibleStatus(not isLocked)
        
    def toggleVisible(self):
        isVisible = not self.config.isVisible
        if isVisible and self.config.encrypted and self.config.locked:
            self.toggleLock()
            return
        self.changeVisibleStatus(isVisible)
            
    def inputPassword(self, title):
        pwdDlg = PasswordInputDialog(title, self)
        result = pwdDlg.exec_()
        if result == QDialog.DialogCode.Accepted:
            return (pwdDlg.password, True)
        else:
            return ("", False)
        
    def toggleLock(self):
        if self.config.encrypted:
            if self.config.locked:
                password, ok = self.inputPassword("Decrypt Your Note")
                print(password, ok)
                if ok and password:
                    note = self.config.decryptNote(password)
                    if note != False:
                        self.cryptPassword = password
                        self.textBrowser.setHtml(note)
                        self.pushButton_lock.setIcon(QIcon(':/resources/unlock.svg'))
                    else:
                        print("invalid password")
                        return
                else:
                    print("canceled or wrong password")
                    return
            else:
                self.cryptPassword = None
                pass
            isLocked = not self.config.locked
            self.changeLockStatus(isLocked)
        else:
            password, ok = self.inputPassword("Encrypt Your Note")
            if ok and password:
                self.cryptPassword = password
                self.config.encrypted = True
                self.config.setNoteData(password, self.config.noteText)
                self.changeLockStatus(True)

    def updatedConfig(self):
        if self.onChangeConfig:
            self.onChangeConfig(CHANGE_TYPE.UPDATE)
    
    def onTextChanged(self):
        text = self.textBrowser.toHtml().replace("\n", "")
        
        if self.config.encrypted:
            self.config.setNoteData(self.cryptPassword, text)
        else:
            self.config.noteText = text
        self.updatedConfig()
        
    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    @pyqtSlot()
    def on_pushButton_add_clicked(self):
        config = NoteConfig.emptyConfig()
        config.posY = self.config.posY + self.newCount * 40
        config.posX = int(max(self.config.posX + self.newCount * 30, 0))
        self.newCount += 1
        self.onSaveConfig(config, CHANGE_TYPE.ADD)

    @pyqtSlot()
    def on_pushButton_menu_clicked(self):
        """
        Slot documentation goes here.
        """
        if not hasattr(self, 'topDrawer'):
            self.topDrawer = CDrawer(self, stretch=0.5, direction=CDrawer.TOP)
            self.noteMenu = NoteMenu(self.topDrawer)
            self.noteMenu.index_signal.connect(self.setBackground)
            self.noteMenu.index_signal.connect(self.topDrawer.animationOut)
            self.noteMenu.pushButton_delete.clicked.connect(self.deleteNote)
            self.noteMenu.pushButton_delete.clicked.connect(self.topDrawer.animationOut)
            self.topDrawer.setWidget(self.noteMenu)
        self.topDrawer.show()

    def deleteNote(self):
        deleteNote = DeleteNote(self)
        deleteNote.delete_signal.connect(self.setClosed)
        deleteNote.exec_()

    def setClosed(self, closed):
        if closed:
            self.onChangeConfig(CHANGE_TYPE.DELETE)
            self.close()

    def setBackground(self, colorIndex):
        # colorIndex -= 1
        # self.frame_title.setStyleSheet("background-color: rgb({});".format(self.titleColor[colorIndex]))
        # self.textBrowser.setStyleSheet("border:none;font: 14pt \"MingLiU-ExtB\";background-color: rgb({});"
        #                                .format(self.buttomColor[colorIndex]))
        # self.frame_buttom.setStyleSheet("background-color: rgb({});".format(self.buttomColor[colorIndex]))
        #
        # for i in ["add", "menu", "close", "bold", "italic", "list", "picture", "strikethrough", "underscore"]:
        #     btn = getattr(self, "pushButton_{}".format(i))
        #     btn.setStyleSheet("QPushButton{{border:none;}}QPushButton:hover{{background: rgb({0});}}QPushButton:checked{{background: rgb({1});}}"
        #                       .format(self.hoverColor[colorIndex], self.hoverColor[colorIndex]))

        file = QFile(":/resources/qss/{}.qss".format(colorIndex))
        file.open(QFile.ReadOnly)
        ts = QTextStream(file)
        ts.setCodec("utf-8")
        styles = ts.readAll()
        self.setStyleSheet(styles)
        self.config.backgroundIndex = colorIndex
        self.updatedConfig()

    @pyqtSlot()
    def on_pushButton_close_clicked(self):
        """
        Close Window
        """
        self.close()
    
    @pyqtSlot(bool)
    def on_pushButton_bold_clicked(self, checked):
        """
        @param checked DESCRIPTION
        @type bool
        """
        if checked:
            self.textBrowser.setFontWeight(QFont.Bold)
        else:
            self.textBrowser.setFontWeight(QFont.Normal)
    
    @pyqtSlot(bool)
    def on_pushButton_italic_clicked(self, checked):
        """
        斜体
        
        @param checked DESCRIPTION
        @type bool
        """
        self.textBrowser.setFontItalic(checked)

    
    @pyqtSlot(bool)
    def on_pushButton_underscore_clicked(self, checked):
        """
        @param checked DESCRIPTION
        @type bool
        """
        self.textBrowser.setFontUnderline(checked)
    
    @pyqtSlot(bool)
    def on_pushButton_strikethrough_clicked(self, checked):
        """
        Slot documentation goes here.
        
        @param checked DESCRIPTION
        @type bool
        """
        self.textBrowser.setFontStrikeOut(checked)
    
    @pyqtSlot(QTextCharFormat)
    def on_textBrowser_currentCharFormatChanged(self, format):
        """
        Slot documentation goes here.
        
        @param format DESCRIPTION
        @type QTextCharFormat
        """
        if format.fontWeight() == QFont.Bold:
            self.pushButton_bold.setChecked(True)
        else:
            self.pushButton_bold.setChecked(False)

        self.pushButton_italic.setChecked(format.fontItalic())
        self.pushButton_underscore.setChecked(format.fontUnderline())
    
    @pyqtSlot(bool)
    def on_pushButton_list_clicked(self, checked):
        """
        @param checked DESCRIPTION
        @type bool
        """
        if checked:
            format = QTextListFormat()
            format.setStyle(QTextListFormat.ListDisc)
            self.textBrowser.textCursor().insertList(format)

    
    @pyqtSlot()
    def on_pushButton_picture_clicked(self):
        """
        """
        imgName, imgType = QFileDialog.getOpenFileName(self, "Open", "",
                                                       "*.jpg;;*.jpeg;;*.png;;*.bmp;;*.gif;;All Files(*.jpg;*.jpeg;*.png;*.bmp;*.gif)")
        fragment = QTextDocumentFragment.fromHtml("<img src = '{}'>".format(imgName))
        self.textBrowser.textCursor().insertFragment(fragment)
