from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

class ScrewTable(QTableWidget):
    def __init__(self, state_update_on):
        super().__init__()
        state_update_on.connect(self.update_state)
        
        # 设置列
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(['标签', '状态', 'X位置(cm)', 'Y位置(cm)', '允许偏差(cm)'])
        
        # 设置表格属性
        self.setMinimumWidth(520)
        self.setMaximumWidth(820)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # 设置列宽
        self.setColumnWidth(0, 10)  # 标签
        self.setColumnWidth(1, 100)  # 状态
        self.setColumnWidth(2, 140)  # X位置
        self.setColumnWidth(3, 140)  # Y位置
        self.setColumnWidth(4, 150)  # 允许偏差

    def update_state(self, state):
        screws = state.get('screws', [])

        self.setRowCount(len(screws))
        
        for row, screw in enumerate(screws):
            # 标签
            self.setItem(row, 0, QTableWidgetItem(str(screw.get('tag', ''))))
            
            # 状态
            status_item = QTableWidgetItem(screw.get('status', '等待中'))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if screw.get('status') == '已完成':
                status_item.setBackground(QColor(Qt.GlobalColor.green))
            elif screw.get('status') == '已定位':
                status_item.setBackground(QColor(Qt.GlobalColor.yellow))
            self.setItem(row, 1, status_item)
            
            # X位置
            x_pos = QTableWidgetItem(f"{screw['position']['x'] * 100:.1f}")
            x_pos.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(row, 2, x_pos)
            
            # Y位置
            y_pos = QTableWidgetItem(f"{screw['position']['y'] * 100:.1f}")
            y_pos.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(row, 3, y_pos)
            
            # 允许偏差
            offset = QTableWidgetItem(f"{screw['position']['allowOffset'] * 100:.1f}")
            offset.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(row, 4, offset)