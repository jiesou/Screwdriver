from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

from ..units.state_bus import state_bus

class ScrewCounter(QWidget):
    def __init__(self):
        super().__init__()
        state_bus.updated.connect(self.update_count)

        layout = QHBoxLayout(self)
        
        self.screws_left = QLabel("0")
        self.screws_left.setStyleSheet("""
            QLabel {
                font-size: 48px;
                color: #1890ff;
                padding-right: 5px;
            }
        """)
        layout.addWidget(QLabel("当前剩余螺丝"))
        layout.addWidget(self.screws_left)

        self.products_finished = QLabel("0")
        self.products_finished.setStyleSheet("""
            QLabel {
                font-size: 48px;
                color: #1890ff;
                padding-right: 5px;
            }
        """)
        layout.addWidget(QLabel("已完成产品"))
        layout.addWidget(self.products_finished)
        
    def update_count(self, state):
        self.screws_left.setText(str(state['screw_count']))
        self.products_finished.setText(str(state['products_finished']))