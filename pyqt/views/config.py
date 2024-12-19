from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QDoubleSpinBox, QLabel
from PyQt5.QtCore import QSignalBlocker

from ..units.event_bus import event_bus
from ..units.stored_config import stored_config

class ConfigView(QWidget):
    def __init__(self):
        super().__init__()
        self.spinboxes = {}  # 存储所有 spinbox 的引用
        stored_config.stored_config_updated.connect(self.update_stored_config)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        # 通用设置函数
        def setup_spinbox(min_val, max_val, step, initial_val, key, label, extra_callback=None):
            spinbox = QDoubleSpinBox()
            spinbox.setMinimum(min_val)
            spinbox.setMaximum(max_val)
            spinbox.setSingleStep(step)
            spinbox.setValue(float(initial_val))
            
            def update_value(value):
                stored_config[key] = value
                if extra_callback:
                    extra_callback(value)

            spinbox.valueChanged.connect(update_value)
            form_layout.addRow(QLabel(label), spinbox)
            self.spinboxes[key] = spinbox  # 保存 spinbox 引用
            return spinbox

        setup_spinbox(
            1.0, 100.0, 0.1,
            stored_config['map_physics_width'],
            'map_physics_width',
            "物理地图宽度(米)"
        )

        setup_spinbox(
            1.0, 100.0, 0.1,
            stored_config['map_physics_height'],
            'map_physics_height',
            "物理地图高度(米)"
        )

        setup_spinbox(
            -8.0, 8.0, 0.05,
            stored_config['imu_center_point_x'],
            'imu_center_point_x',
            "垂直参考中心X偏移(米)",
            lambda _: setattr(event_bus.processor_api.imu_api.processor, 'center_point',
                              (stored_config['imu_center_point_x'], stored_config['imu_center_point_y']))
        )

        setup_spinbox(
            -8.0, 8.0, 0.05,
            stored_config['imu_center_point_y'],
            'imu_center_point_y',
            "垂直参考中心Y偏移(米)",
            lambda _: setattr(event_bus.processor_api.imu_api.processor, 'center_point',
                              (stored_config['imu_center_point_x'], stored_config['imu_center_point_y']))
        )

        setup_spinbox(
            0.05, 3.0, 0.05,
            stored_config['imu_vertical_h'],
            'imu_vertical_h',
            "位置单元垂直距离(米)",
            lambda v: setattr(event_bus.processor_api.imu_api.processor, 'h', v)
        )

        layout.addLayout(form_layout)

    def update_stored_config(self, updated_config):
        # 防止循环更新
        # with QSignalBlocker(self):
        for key, value in updated_config.items():
            if key in self.spinboxes:
                self.spinboxes[key].setValue(value)
