from PyQt5.QtWidgets import QWidget, QHBoxLayout

from ..components.screw_map import ScrewMap
from ..components.screw_table import ScrewTable
from ..components.screw_counter import ScrewCounter

from ..units.event_bus import event_bus

class DashView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        
        # 左侧控制面板
        left_panel = QWidget()
        left_layout = QHBoxLayout(left_panel)
        
        # 添加螺丝表格
        self.screw_table = ScrewTable()
        left_layout.addWidget(self.screw_table)
        
        # 添加螺丝计数器
        # self.screw_counter = ScrewCounter()
        # left_layout.addWidget(self.screw_counter)
        
        layout.addWidget(left_panel)
        
        # 添加螺丝地图
        self.screw_map = ScrewMap()
        layout.addWidget(self.screw_map)
        