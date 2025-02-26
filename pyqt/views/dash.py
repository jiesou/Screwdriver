from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, 
                           QPushButton)
from .learn import LearnView

from ..components.screw_map import ScrewMap
from ..components.screw_table import ScrewTable
from ..components.csv_reader import CsvReader
from ..components.ploy import RayVisualizer

from ..units.state_bus import state_bus

class DashView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        
        # 左侧控制面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 添加导入导出按钮
        btn_layout = QHBoxLayout()
        csv_reader = CsvReader()
        btn_layout.addWidget(csv_reader)
        
        # 在按钮布局中添加学习模式按钮
        learn_btn = QPushButton("学习模式（WIP）")
        learn_btn.clicked.connect(self.open_learn_dialog)
        btn_layout.addWidget(learn_btn)
        
        left_layout.addLayout(btn_layout)
        
        # 添加螺丝表格
        self.screw_table = ScrewTable(state_update_on=state_bus.updated)
        left_layout.addWidget(self.screw_table)
        
        layout.addWidget(left_panel)
        
        # 添加螺丝地图
        self.screw_map = RayVisualizer(state_update_on=state_bus.updated)
        layout.addWidget(self.screw_map)

    def open_learn_dialog(self):
        dialog = LearnView(self)
        dialog.exec()
