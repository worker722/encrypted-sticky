from utils.NoteConfig import NoteConfig
from utils.constants import CHANGE_TYPE
from PyQt5.QtWidgets import QApplication
import sys
from CustomWidgets.Note import Note

def onSaveConfig(config : NoteConfig, type = CHANGE_TYPE.UPDATE):
    if type == CHANGE_TYPE.ADD or type == CHANGE_TYPE.UPDATE:
        configs[config.key] = config
    elif type == CHANGE_TYPE.DELETE:
        configs.pop(config.key)

    print("update config")
    # for key in configs:
    #     print(configs[key])


if __name__ == "__main__":
    config1 = NoteConfig.tmpConfig1()
    config2 = NoteConfig.tmpConfig2()
    configs = { config1.key:config1, config2.key:config2 }

    app = QApplication(sys.argv)

    for key in configs:
        ui = Note(configs[key], onSaveConfig)
        ui.show()
        
    sys.exit(app.exec_())
