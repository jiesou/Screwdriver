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
        # 设置表格属性
        self.setMinimumWidth(400)  # 设置最小宽度
        # 移除 setMaximumWidth 的限制
        
        header = self.horizontalHeader()
        # 改为可调整模式
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        
        
        # 设置列宽
        self.setColumnWidth(0, 50)  # 标签
        self.setColumnWidth(1, 70)  # 状态
        self.setColumnWidth(2, 70)  # X位置
        self.setColumnWidth(3, 70)  # Y位置
        self.setColumnWidth(4, 80)  # 允许偏差

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