from PyQt6.QtWidgets import (QWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QVBoxLayout, QHBoxLayout, QPushButton,
                             QApplication)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt

from ..units.state_bus import state_bus
from ..units.stored_config import stored_config


class ScrewTable(QWidget):
    def __init__(self, state_update_on):
        super().__init__()
        # flag to ignore itemChanged during programmatic updates
        self._updating = False

        state_update_on.connect(self.update_state)

        # layout
        main_layout = QVBoxLayout(self)

        btn_layout = QHBoxLayout()
        self.add_button = QPushButton("添加一行")
        self.delete_button = QPushButton("删除选中")
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

        # 设置列宽
        self.table.setColumnWidth(0, 50)  # 标签
        self.table.setColumnWidth(1, 70)  # 状态
        self.table.setColumnWidth(2, 70)  # X位置
        self.table.setColumnWidth(3, 70)  # Y位置
        self.table.setColumnWidth(4, 80)  # 允许偏差

        # signals
        self.table.itemChanged.connect(self.on_item_changed)
        self.add_button.clicked.connect(self.add_row)
        self.delete_button.clicked.connect(self.delete_selected_rows)

    def update_state(self, state):
        """Populate table from incoming state. This is programmatic and must
        not trigger persisting back to the state bus.
        """
        # 如果用户正在编辑表格（焦点在表格或其内部编辑器），跳过自动刷新，避免覆盖输入
        focus_widget = QApplication.focusWidget()
        if focus_widget is not None and (focus_widget is self.table or self.table.isAncestorOf(focus_widget)):
            return

        screws = state.get('screws', [])

        self._updating = True
        try:
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

                # X位置 (以 cm 显示)
                x_val = screw.get('position', {}).get('x', 0.0) * 100
                x_pos = QTableWidgetItem(f"{x_val:.1f}")
                x_pos.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 2, x_pos)

                # Y位置
                y_val = screw.get('position', {}).get('y', 0.0) * 100
                y_pos = QTableWidgetItem(f"{y_val:.1f}")
                y_pos.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 3, y_pos)

                # 允许偏差
                offset_val = screw.get('position', {}).get('allowOffset', 0.0) * 100
                offset = QTableWidgetItem(f"{offset_val:.1f}")
                offset.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 4, offset)
        finally:
            self._updating = False

    def on_item_changed(self, item: QTableWidgetItem):
        """Persist a single cell edit back to the global state bus.

        The table shows distances in cm; convert back to meters for state.
        """
        if self._updating:
            return

        row = item.row()
        col = item.column()

        screws = state_bus.state.get('screws', []).copy()
        if row < 0 or row >= len(screws):
            return

        screw = screws[row]

        # Helper to reset invalid numeric edits back to previous formatted value
        def _reset_to(prev_value_m):
            self._updating = True
            try:
                item.setText(f"{prev_value_m * 100:.1f}")
            finally:
                self._updating = False

        try:
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
                # status column is read-only and shouldn't get here
                return

            # write back to global state so other components update
            state_bus.state = {'screws': screws}

        except Exception as e:
            # don't crash UI on unexpected errors; reset the cell
            try:
                if col in (2, 3, 4):
                    prev = screw.get('position', {}).get(('x' if col==2 else 'y' if col==3 else 'allowOffset'), 0.0)
                    _reset_to(prev)
            except Exception:
                pass

    def add_row(self):
        screws = state_bus.state.get('screws', []).copy()
        # 默认标签自增
        new_tag = str(len(screws) + 1)
        state_bus.state['screws'].append({
            'tag': new_tag,
            'position': {'x': 0.0, 'y': 0.0, 'allowOffset': 0.05}
        })
        state_bus.state = {'screws': screws}

    def delete_selected_rows(self):
        rows = sorted({idx.row() for idx in self.table.selectionModel().selectedRows()}, reverse=True)
        if not rows:
            return
        screws = state_bus.state.get('screws', []).copy()
        for r in rows:
            if 0 <= r < len(screws):
                screws.pop(r)
        state_bus.state = {'screws': screws}