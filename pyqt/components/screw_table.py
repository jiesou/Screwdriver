from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt

class ScrewTable(QTableWidget):
    def __init__(self):
        super().__init__()
        
        # 设置列
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(['序号', '状态', 'X位置(cm)', 'Y位置(cm)', '允许偏差(cm)'])
        
        # 设置表格属性
        self.setMinimumWidth(520)
        self.setMaximumWidth(520)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Fixed)
        
        # 设置列宽
        self.setColumnWidth(0, 60)  # 序号
        self.setColumnWidth(1, 100)  # 状态
        self.setColumnWidth(2, 120)  # X位置
        self.setColumnWidth(3, 120)  # Y位置
        self.setColumnWidth(4, 120)  # 允许偏差

    def update_screws(self, screws):
        self.setRowCount(len(screws))
        
        for row, screw in enumerate(screws):
            # 序号
            self.setItem(row, 0, QTableWidgetItem(str(screw.get('tag', ''))))
            
            # 状态
            status_item = QTableWidgetItem(screw.get('status', '等待中'))
            status_item.setTextAlignment(Qt.AlignCenter)
            if screw.get('status') == '已完成':
                status_item.setBackground(Qt.green)
            elif screw.get('status') == '已定位':
                status_item.setBackground(Qt.yellow)
            self.setItem(row, 1, status_item)
            
            # X位置
            x_pos = QTableWidgetItem(f"{screw['position']['x'] * 100:.1f}")
            x_pos.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 2, x_pos)
            
            # Y位置
            y_pos = QTableWidgetItem(f"{screw['position']['y'] * 100:.1f}")
            y_pos.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 3, y_pos)
            
            # 允许偏差
            offset = QTableWidgetItem(f"{screw['position']['allowOffset'] * 100:.1f}")
            offset.setTextAlignment(Qt.AlignCenter)
            self.setItem(row, 4, offset)