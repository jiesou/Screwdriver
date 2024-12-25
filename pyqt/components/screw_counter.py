from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class ScrewCounter(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        self.title = QLabel("剩余螺丝")
        self.title.setAlignment(Qt.AlignCenter)
        
        self.count_label = QLabel("0")
        self.count_label.setAlignment(Qt.AlignCenter)
        self.count_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                color: #1890ff;
                padding: 10px;
            }
        """)
        
        layout.addWidget(self.title)
        layout.addWidget(self.count_label)
        
    def update_count(self, count):
        self.count_label.setText(str(count))