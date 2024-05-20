import sys
from PyQt5.QtWidgets import QApplication, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

class MyMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create a button to toggle the drawer
        self.toggle_button = QPushButton("Toggle Drawer")
        self.toggle_button.clicked.connect(self.toggle_drawer)
        layout.addWidget(self.toggle_button)

        # Create a label to display selected color
        self.color_label = QLabel("Selected Color: None")
        layout.addWidget(self.color_label)

        # Create a CDrawer instance with a QLabel as its content
        self.drawer_content = QLabel("Choose a color")
        self.drawer_content.setStyleSheet("background-color: white;")
        self.drawer = CDrawer(stretch=1 / 3, direction=CDrawer.RIGHT, widget=self.drawer_content)
        
    def toggle_drawer(self):
        # Toggle the drawer visibility
        if self.drawer.isVisible():
            self.drawer.hide()
        else:
            self.drawer.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())
