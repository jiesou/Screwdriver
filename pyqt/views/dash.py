from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, 
                           QPushButton, QFileDialog)

from ..components.screw_map import ScrewMap
from ..components.screw_table import ScrewTable
from ..components.screw_counter import ScrewCounter
from ..components.csv_reader import parse_csv, export_csv

from ..units.event_bus import event_bus

class DashView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout(self)
        
        # 左侧控制面板
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 添加导入导出按钮
        btn_layout = QHBoxLayout()
        import_btn = QPushButton("导入CSV")
        import_btn.clicked.connect(self.import_csv)
        export_btn = QPushButton("导出CSV") 
        export_btn.clicked.connect(self.export_csv)
        btn_layout.addWidget(import_btn)
        btn_layout.addWidget(export_btn)
        left_layout.addLayout(btn_layout)
        
        # 添加螺丝表格
        self.screw_table = ScrewTable()
        left_layout.addWidget(self.screw_table)
        
        layout.addWidget(left_panel)
        
        # 添加螺丝地图
        self.screw_map = ScrewMap()
        layout.addWidget(self.screw_map)

    def import_csv(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "选择CSV文件",
            "",
            "CSV Files (*.csv)"
        )
        if filepath:
            try:
                screws = parse_csv(filepath)
                event_bus.import_screws(screws)
            except Exception as e:
                print(f"导入失败: {e}")

    def export_csv(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "保存CSV文件",
            "",
            "CSV Files (*.csv)"
        )
        if filepath:
            try:
                screws = event_bus.export_screws()
                export_csv(filepath, screws)
            except Exception as e:
                print(f"导出失败: {e}")
