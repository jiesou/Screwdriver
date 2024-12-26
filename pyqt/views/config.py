from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QDoubleSpinBox, QLabel
from PyQt6.QtCore import QSignalBlocker

from ..units.state_bus import state_bus
from ..units.stored_config import stored_config

class ConfigView(QWidget):
    def __init__(self):
        super().__init__()
        self.spinboxes = {}  # 存储所有 spinbox 的引用
        stored_config.updated.connect(self.update_stored_config)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        # 通用设置函数
        def setup_spinbox(min_val, max_val, step, key, label):
            spinbox = QDoubleSpinBox()
            spinbox.setMinimum(min_val)
            spinbox.setMaximum(max_val)
            spinbox.setSingleStep(step)
            spinbox.setValue(stored_config[key])
            
            def update_value(value):
                stored_config[key] = value

            spinbox.valueChanged.connect(update_value)
            form_layout.addRow(QLabel(label), spinbox)
            self.spinboxes[key] = spinbox  # 保存 spinbox 引用
            return spinbox

        setup_spinbox(
            1.0, 100.0, 0.1,
            'map_physics_width',
            "物理地图宽度(米)"
        )
        
        setup_spinbox(
            -8.0, 8.0, 0.05,
            'imu_center_point_x',
            "垂直参考中心X偏移(米)"
        )

        setup_spinbox(
            -8.0, 8.0, 0.05,
            'imu_center_point_y',
            "垂直参考中心Y偏移(米)"
        )

        setup_spinbox(
            0.05, 3.0, 0.05,
            'imu_vertical_h',
            "位置单元垂直距离(米)"
        )

        layout.addLayout(form_layout)

    def update_stored_config(self, updated_config):
        for key, value in updated_config.items():
            if key in self.spinboxes:
                self.spinboxes[key].setValue(value)
