import time
from utils.utils import encrypt_message, decrypt_message
import uuid

class NoteConfig:
    key:str = ''

    title:str = ''
    noteText:str = ''

    backgroundIndex:int = 1
    posX:int = 0
    posY:int = 100
    width:int = 300
    height:int = 280
    locked:bool = False
    encrypted:bool = False
    isVisible:bool = True

    def __init__(self):
        pass
    
    @staticmethod
    def fromDBRow(row):
        config = NoteConfig()
        config.key = row[0]
        config.title = row[1]
        config.noteText = row[2]
        config.backgroundIndex = row[3]
        config.posX = row[4]
        config.posY = row[5]
        config.width = row[6]
        config.height = row[7]
        config.encrypted =  row[7] == 1
        config.isVisible =  row[8] == 1
        config.locked = config.encrypted
        return config
    
    @staticmethod
    def emptyConfig():
        config = NoteConfig()
        config.key = str(uuid.uuid4())
        return config

    def updateData(self):
        return (self.title, self.noteText, self.backgroundIndex, self.posX, self.posY, self.width, self.height, int(self.encrypted), int(self.isVisible))
    
    def insertData(self):
        return (self.key,)+ (self.updateData())
    
    
    def setNoteData(self, key, note):
        self.noteText = encrypt_message(note, key)
        return True
    
    def decryptNote(self, key):
        try:
            return decrypt_message(self.noteText, key)
        except:
            return False