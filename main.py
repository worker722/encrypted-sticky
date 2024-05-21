import pystray
from PIL import Image
import sqlite3
import keyboard
from utils.NoteConfig import NoteConfig
import threading
import sys
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from utils.NoteConfig import NoteConfig
from CustomWidgets.Note import Note
from utils.constants import CHANGE_TYPE
    
class Main():
    def __init__(self):
        self.dbConn = sqlite3.connect("sticky.db")
        self.dbCursor = self.dbConn.cursor()
        self.stickyUis = []
        self.initDB()
        self.tray_thread = threading.Thread(target=self.initTray)
        self.tray_thread.start()
        self.load_db()
        self.render_sticky()

    def initDB(self):
        self.dbCursor.execute("CREATE TABLE IF NOT EXISTS notes(key TEXT, title TEXT, noteText TEXT, backgroundIndex INTEGER, posX INTEGER, posY INTEGER, width INTEGER, height INTEGER, encrypted INTEGER, isVisible INTEGER)")
        
    def initTray(self):
        try:
            keyboard.add_hotkey('alt+a', self.on_show_sticky)
            keyboard.add_hotkey('alt+c', self.on_exit)
            
            image = Image.open("resources/icon.png")
            menu = (
                pystray.MenuItem("Show All (ALT + A)", self.on_show_sticky),
                pystray.MenuItem("Exit", self.on_exit)
            )
            self.trayIcon = pystray.Icon("TrayIcon", image, "Tray Application", menu)

            self.trayIcon.run()
        except:
            pass

    def on_exit(self):
        print("Exiting...")
        self.trayIcon.stop()
        
    
    def load_db(self):
        self.noteConfigs = {}
        
        self.dbCursor.execute('SELECT * FROM notes')
        rows = self.dbCursor.fetchall()
        
        for row in rows:
            config = NoteConfig.fromDBRow(row)
            self.noteConfigs[config.key] = config
            
            
    def save_db(self, config: NoteConfig, isAdd):
        if not config:
            return
        
        if isAdd:
            self.dbCursor.execute("INSERT INTO notes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", config.insertData())
        else:
            self.dbCursor.execute(f"UPDATE notes SET title=?, noteText=?, backgroundIndex=?, posX=?, posY=?, width=?, height=?, encrypted=?, isVisible=? WHERE key='{config.key}'", config.updateData())
        self.dbConn.commit()
            
    
    def onSaveConfig(self, config, type = CHANGE_TYPE.UPDATE):
        if type == CHANGE_TYPE.ADD:
            count = len(self.noteConfigs)
            if count > 8:
                return
            config.title = f"Note Note"
            self.noteConfigs[config.key] = config
            ui = Note(config, self.onSaveConfig)
            self.stickyUis.append(ui)
            ui.raiseToTop()
        elif type == CHANGE_TYPE.UPDATE:
            self.noteConfigs[config.key] = config
        elif type == CHANGE_TYPE.DELETE:
            self.noteConfigs.pop(config.key)
            
        self.save_db(config, type == CHANGE_TYPE.ADD)
        
    def on_show_sticky(self):
        for item in self.stickyUis:
            item.raiseToTop()
        pass
    

    def render_sticky(self):
        app = QApplication(sys.argv)
        # screen = QDesktopWidget().screenGeometry()
        # width = screen.width()

        if len(self.noteConfigs) <= 0:
            conf = NoteConfig.emptyConfig()
            self.onSaveConfig(conf, CHANGE_TYPE.ADD)
        else:
            for key in self.noteConfigs:
                ui = Note(self.noteConfigs[key], self.onSaveConfig)
                self.stickyUis.append(ui)
                ui.raiseToTop()
            
        sys.exit(app.exec_())
            
if __name__ == "__main__":
    Main()