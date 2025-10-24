from PyQt6.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QVBoxLayout, QHBoxLayout, QPushButton,
                             QApplication, QDoubleSpinBox)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

from pyqt.units.types import State

from ..units.state_bus import state_bus
from ..units.types import State
from ..units.stored_config import stored_config
import copy


class ScrewTable(QWidget):
    def __init__(self, state_update_on):
        super().__init__()
        state_update_on.connect(self.update_state)

        # layout
        main_layout = QVBoxLayout(self)

        btn_layout = QHBoxLayout()
        self.add_button = QPushButton("+ 添加螺丝")
        self.delete_button = QPushButton("X 删除选中")
        self.delete_button.hide()  # 初始隐藏
        # 防止点击删除按钮时焦点离开表格，导致选中状态丢失
        self.delete_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        btn_layout.addWidget(self.add_button)
        btn_layout.addWidget(self.delete_button)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # table
        self.table = QTableWidget()
        main_layout.addWidget(self.table)

        # 设置列
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['标签', '状态', 'X位置(cm)', 'Y位置(cm)', '允许偏差(cm)'])

        self.table.setMinimumWidth(400)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows) # 整行选中

        # 设置列宽
        self.table.setColumnWidth(0, 50)  # 标签
        self.table.setColumnWidth(1, 70)  # 状态
        self.table.setColumnWidth(2, 70)  # X位置
        self.table.setColumnWidth(3, 70)  # Y位置
        self.table.setColumnWidth(4, 80)  # 允许偏差

        # signals
        self.table.itemChanged.connect(self.on_item_changed)
        # 当任意单元格被选中/取消选中时，切换删除按钮可见性
        self.table.itemSelectionChanged.connect(lambda:
            self.delete_button.setVisible(bool(self.table.selectionModel().selectedIndexes()))
        )
        self.add_button.clicked.connect(self.add_row)
        self.delete_button.clicked.connect(self.delete_selected_rows)

    def update_state(self, state: State):
        """Populate table from incoming state. This is programmatic and must
        not trigger persisting back to the state bus.
        """
        # 避免在用户正在编辑时覆盖输入
        focus_widget = QApplication.focusWidget()
        if focus_widget is not None and (focus_widget is self.table or self.table.isAncestorOf(focus_widget)):
            return

        screws = state.get('screws', [])

        # 阻塞 itemChanged 信号，避免触发递归
        self.table.blockSignals(True)
        
        # 清空现有内容并重建，使用自定义的 QSpinBox 嵌入以支持滚轮调整
        self.table.clearContents()
        self.table.setRowCount(len(screws))

        for row, screw in enumerate(screws):
            # 标签
            tag_item = QTableWidgetItem(str(screw.get('tag', '')))
            tag_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 0, tag_item)

            # 状态 (只读)
            status_item = QTableWidgetItem(screw.get('status', '等待中'))
            current_flags = status_item.flags()
            new_flags = current_flags & ~Qt.ItemFlag.ItemIsEditable
            status_item.setFlags(new_flags)
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if screw.get('status') == '已完成':
                status_item.setBackground(QColor(Qt.GlobalColor.green))
            elif screw.get('status') == '已定位':
                status_item.setBackground(QColor(Qt.GlobalColor.yellow))
            self.table.setItem(row, 1, status_item)

            # X位置 (以 cm 显示) — 使用嵌入的 DoubleSpinBox
            x_val_cm = screw.get('position', {}).get('x', 0.0) * 100
            x_spin = QDoubleSpinBox()
            # 在属性中保存行列，回调 on updated 时读取（update_state 会在行变化时重建 widgets）
            x_spin.setProperty('row', row)
            x_spin.setProperty('col', 2)
            x_spin.setRange(-100.0, 100.0)
            x_spin.setValue(x_val_cm) # 设置初始值
            x_spin.valueChanged.connect(self.on_spinbox_changed)
            self.table.setCellWidget(row, 2, x_spin)

            # Y位置
            y_val_cm = screw.get('position', {}).get('y', 0.0) * 100
            y_spin = QDoubleSpinBox()
            y_spin.setProperty('row', row)
            y_spin.setProperty('col', 3)
            y_spin.setRange(-100.0, 100.0)
            y_spin.setValue(y_val_cm) # 设置初始值
            y_spin.valueChanged.connect(self.on_spinbox_changed)
            self.table.setCellWidget(row, 3, y_spin)

            # 允许偏差
            offset_val_cm = screw.get('position', {}).get('allowOffset', 0.0) * 100
            off_spin = QDoubleSpinBox()
            off_spin.setProperty('row', row)
            off_spin.setProperty('col', 4)
            off_spin.setRange(1.0, 20.0)
            off_spin.setValue(offset_val_cm) # 设置初始值
            off_spin.valueChanged.connect(self.on_spinbox_changed)
            self.table.setCellWidget(row, 4, off_spin)

        # 恢复信号
        self.table.blockSignals(False)

    def on_spinbox_changed(self, value_cm: float):
        """处理嵌入 SpinBox 的值变化，value_cm 是以 cm 为单位的浮点数。
        将 cm 转换为 m 并持久化。
        """
        sender = self.sender()
        if sender is None:
            return
        try:
            row = int(sender.property('row'))
            col = int(sender.property('col'))
        except Exception:
            return

        screws = state_bus.state.get('screws', []).copy()
        if row < 0 or row >= len(screws):
            return

        screw = screws[row]
        # cm -> m
        m_val = float(value_cm) / 100.0

        if col == 2:
            screw.setdefault('position', {})['x'] = m_val
        elif col == 3:
            screw.setdefault('position', {})['y'] = m_val
        elif col == 4:
            screw.setdefault('position', {})['allowOffset'] = m_val
        else:
            return

        self._update_screws(screws)

    def on_item_changed(self, item: QTableWidgetItem):
        """
        持久化单元格编辑，同步状态总线。
        """
        row = item.row()
        col = item.column()

        screws = state_bus.state.get('screws', []).copy()
        if row < 0 or row >= len(screws):
            return

        screw = screws[row]

        # 用于重置无效输入的辅助函数
        def _reset_to(prev_value_m):
            item.setText(f"{prev_value_m * 100:.1f}")

        if col == 0:  # tag
            screw['tag'] = item.text()
        elif col == 2:  # x (cm -> m)
            prev = screw.get('position', {}).get('x', 0.0)
            try:
                v = float(item.text()) / 100.0
            except Exception:
                _reset_to(prev)
                return
            screw.setdefault('position', {})['x'] = v
        elif col == 3:  # y
            prev = screw.get('position', {}).get('y', 0.0)
            try:
                v = float(item.text()) / 100.0
            except Exception:
                _reset_to(prev)
                return
            screw.setdefault('position', {})['y'] = v
        elif col == 4:  # allowOffset
            prev = screw.get('position', {}).get('allowOffset', 0.0)
            try:
                v = float(item.text()) / 100.0
            except Exception:
                _reset_to(prev)
                return
            screw.setdefault('position', {})['allowOffset'] = v
        else:
            # 状态列不可编辑，这里不应该被执行到
            return
        self._update_screws(screws)


    def add_row(self):
        screws = state_bus.state.get('screws', []).copy()
        # 默认标签自增
        new_tag = str(len(screws) + 1)
        screws.append({
            'tag': new_tag,
            'position': {'x': 0.0, 'y': 0.0, 'allowOffset': 0.05}
        })
        self._update_screws(screws)

    def delete_selected_rows(self):
        print("Deleting selected rows")
        # 支持用户只选中单元格的情况：收集所有被选中单元格对应的行索引并去重
        rows = sorted({idx.row() for idx in self.table.selectionModel().selectedIndexes()}, reverse=True)
        print("Deleting rows:", rows)
        if not rows:
            return
        screws = state_bus.state.get('screws', []).copy()
        for r in rows:
            if 0 <= r < len(screws):
                screws.pop(r)
        # 暂时转移焦点，使 update_state 可以执行表格更新
        self.add_button.setFocus()
        self._update_screws(screws)
    
    def _update_screws(self, screws):
        """
        持久化到 stored_config 的初始螺丝列表，
        同时同步 live 的 state_bus
        """
        # state_bus.state = {'screws': screws, **state_bus.state}
        # 持久存储到配置文件
        stored_config['init_screws'] = copy.deepcopy(screws)
