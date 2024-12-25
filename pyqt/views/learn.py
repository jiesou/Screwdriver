from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog
from PyQt6.QtCore import QTimer
from ..components.screw_table import ScrewTable
from ..components.screw_map import ScrewMap
from ..components.csv_reader import export_csv
from ..units.event_bus import event_bus
from processor import ProcessorAPI

class LearnView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("学习模式")
        self.processor_api = ProcessorAPI()
        self.screws = []
        self.prev_is_tightening = False

        # 布局
        layout = QVBoxLayout(self)
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始学习")
        self.stop_btn = QPushButton("停止学习")
        self.export_btn = QPushButton("导出学习结果")
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.export_btn)
        layout.addLayout(btn_layout)

        # 表格 & 地图
        self.screw_table = ScrewTable(event_bus.state_updated)
        self.screw_map = ScrewMap(event_bus.state_updated)
        layout.addWidget(self.screw_table)
        layout.addWidget(self.screw_map)

        # 信号
        self.start_btn.clicked.connect(self.start_learning)
        self.stop_btn.clicked.connect(self.stop_learning)
        self.export_btn.clicked.connect(self.export_csv_file)

        # 定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self.collect_data)

    def start_learning(self):
        self.screws.clear()
        self.timer.start(50)  # 20Hz 采样

    def stop_learning(self):
        self.timer.stop()

    def export_csv_file(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "导出学习结果", "", "CSV Files (*.csv)"
        )
        if filepath:
            export_csv(filepath, self.screws)

    def collect_data(self):
        # 获取实时数据
        data = self.processor_api.requirement_analyze()
        position = data["position"]
        is_tightening = data["is_screw_tightening"]

        # 切换到拧紧时记录坐标
        if not self.prev_is_tightening and is_tightening:
            self.screws.append({
                "tag": f"L{len(self.screws)+1}",
                "status": "已定位",
                "position": {
                    "x": position[0],
                    "y": position[1],
                    "allowOffset": 0.05
                }
            })
        self.prev_is_tightening = is_tightening

        # 更新界面
        event_bus.import_screws(self.screws)
