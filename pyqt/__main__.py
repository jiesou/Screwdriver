import sys
from PyQt5.QtWidgets import QApplication
from .app import App

app = QApplication(sys.argv)
window = App()
window.show()
sys.exit(app.exec_())