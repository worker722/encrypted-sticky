import pystray
from PIL import Image
import sqlite3
import keyboard
from utils.NoteConfig import NoteConfig
import threading

import sys
from PyQt5.QtWidgets import QApplication, QWidget
from utils.NoteConfig import NoteConfig
from enum import Enum
from CustomWidgets.Note import Note
from PyQt5.QtCore import QThread
from utils.constants import CHANGE_TYPE
    
class Main():
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.dbConn = sqlite3.connect("sticky.db")
        self.dbCursor = self.dbConn.cursor()
        
        self.stickyUis = []
        
        self.initDB()
        self.tray_thread = threading.Thread(target=self.initTray)
        self.tray_thread.start()
        self.load_db()
        self.render_sticky()

    def initDB(self):
        self.dbCursor.execute("""CREATE TABLE IF NOT EXISTS notes(
            key TEXT,
            noteText TEXT,
            backgroundIndex INTEGER,
            posX INTEGER,
            posY INTEGER,
            width INTEGER,
            height INTEGER)""")
        
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
        self.app.exit()
        
    
    def load_db(self):
        self.noteConfigs = {}
        
        self.dbCursor.execute('SELECT * FROM notes')
        rows = self.dbCursor.fetchall()
        
        for row in rows:
            config = NoteConfig.fromDBRow(row)
            self.noteConfigs[config.key] = config
            
        if len(self.noteConfigs) <= 0:
            conf = NoteConfig.emptyConfig()
            self.noteConfigs = { conf.key: conf }
            
    def save_db(self):
        # config = NoteConfig("!")
        # self.dbCursor.execute("INSERT INTO notes VALUES (?, ?, ?, ?, ?, ?, ?)", config.insertData())
        # self.dbConn.commit()
        pass
    
    def onSaveConfig(self, key, config, type = CHANGE_TYPE.UPDATE):
        print(key, config, type)
        # with open(db_name, "w") as file:
        #     if type == CHANGE_TYPE.ADD or type == CHANGE_TYPE.UPDATE:
        #         configs[key] = config
        #     elif type == CHANGE_TYPE.DELETE:
        #         configs.pop(key)
        
        #     resString = ""
            
        #     for key in configs:
        #         resString += configs[key].__str__()

        #     file.write(resString)

    def on_show_sticky(self):
        # for item in self.stickyUis:
        print("raise")
            # item.raise_()
        pass

    def render_sticky(self):
        for key in self.noteConfigs:
            ui = Note(key, self.noteConfigs[key], self.onSaveConfig)
            ui.show()
            # self.stickyUis.append(ui)
            ui.raise_()
            

    
if __name__ == "__main__":
    Main()