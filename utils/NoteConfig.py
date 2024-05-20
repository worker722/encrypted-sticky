import time
from utils.utils import encrypt_message, decrypt_message

class NoteConfig:
    key:str = ''

    noteText:str = ''
    locked:bool = False
    encrypted:bool = False
    isVisible:bool = True

    backgroundIndex:int = 1
    posX:int = 0
    posY:int = 0
    width:int = 300
    height:int = 250
    
    
    def __init__(self):
        pass
        
    @staticmethod
    def fromDBRow(row):
        config = NoteConfig()
        config.key = row[0]
        config.noteText = row[1]
        config.locked = True
        config.backgroundIndex = row[2]
        config.posX = row[3]
        config.posY = row[4]
        config.width = row[5]
        config.height = row[6]
        return config
    
    @staticmethod
    def emptyConfig():
        config = NoteConfig()
        config.key = str(int(time.time() * 1000))
        return config
    
    @staticmethod
    def tmpConfig1():
        config = NoteConfig()
        config.key = str(int(time.time() * 1000))
        config.noteText = ''
        config.locked = False
        config.encrypted = True
        config.isVisible = True
        return config
        
    @staticmethod
    def tmpConfig2():
        config = NoteConfig()
        config.key = str(int(time.time() * 1000))
        config.noteText = ''
        config.locked = False
        config.encrypted = False
        config.isVisible = True
        return config
    

    def __str__(self):
        note = self.noteText
        return f"==============================NOTE CONFIG==============================\nkey={self.key}\nbackground={self.backgroundIndex}\nposX={self.posX}\nposY={self.posY}\nwidth={self.width}\nheight={self.height}\nvisible={self.locked}\nnote={note}\n============================================================\n"
    
    def insertData(self):
        return (self.key, self.noteText, self.backgroundIndex, self.posX, self.posY, self.width, self.height)
    
    
    def setNoteData(self, key, note):
        self.noteText = encrypt_message(note, key)
        return True
    
    def decryptNote(self, key):
        try:
            return decrypt_message(self.noteText, key)
        except:
            return False