import csv
from typing import List, Dict

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog

from ..units.state_bus import state_bus
from ..units.stored_config import stored_config

class CsvReader(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)

        input_csv_bth = QPushButton("导入CSV")
        input_csv_bth.clicked.connect(self.import_csv)
        layout.addWidget(input_csv_bth)

        output_csv_bth = QPushButton("导出CSV")
        output_csv_bth.clicked.connect(self.export_csv)
        layout.addWidget(output_csv_bth)

    def import_csv(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "选择CSV文件",
            "",
            "CSV Files (*.csv)"
        )
        if filepath:
            try:
                screws = parse(filepath)
                stored_config['init_screws'] = screws
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
                screws = state_bus.state.get('screws', [])
                write(filepath, screws)
            except Exception as e:
                print(f"导出失败: {e}")

def parse(filepath: str) -> List[Dict]:
    screws = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            try:
                screws.append({
                    "tag": str(row.get('标签', i+1)),
                    "status": "等待中",
                    "position": {
                        "x": float(row.get('X位置(m)', 0)),
                        "y": float(row.get('Y位置(m)', 0)), 
                        "allowOffset": float(row.get('允许误差', 0.1))
                    }
                })
            except ValueError as e:
                print(f"Error parsing row {i}: {e}")
                continue
    return screws

def write(filepath: str, screws: List[Dict]):
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['标签', 'X位置(m)', 'Y位置(m)', '允许误差'])
        for screw in screws:
            writer.writerow([
                screw['tag'],
                screw['position']['x'],
                screw['position']['y'],
                screw['position']['allowOffset']
            ])
