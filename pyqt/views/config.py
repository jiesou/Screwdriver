from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QDoubleSpinBox, 
                            QLabel, QLineEdit, QCheckBox, QTabWidget)
from PyQt6.QtCore import QSignalBlocker

from ..units.state_bus import state_bus
from ..units.stored_config import stored_config

class ConfigView(QWidget):
    def __init__(self):
        super().__init__()
        self.spinboxes = {}
        stored_config.updated.connect(self.update_stored_config)

        layout = QVBoxLayout(self)
        
        # 创建标签页控件
        tab_widget = QTabWidget()
        
        # 创建第一个标签页 - 物理参数
        physics_tab = QWidget()
        physics_layout = QFormLayout(physics_tab)
        
        # 通用设置函数
        def setup_spinbox(min_val, max_val, step, key, label, parent_layout):
            spinbox = QDoubleSpinBox()
            spinbox.setMinimum(min_val)
            spinbox.setMaximum(max_val)
            spinbox.setSingleStep(step)
            spinbox.setValue(stored_config[key])
            
            def update_value(value):
                stored_config[key] = value

            spinbox.valueChanged.connect(update_value)
            parent_layout.addRow(QLabel(label), spinbox)
            self.spinboxes[key] = spinbox
            return spinbox

        # 添加物理参数配置
        setup_spinbox(1.0, 100.0, 0.1, 'map_physics_width', "物理地图宽度(米)", physics_layout)
        setup_spinbox(-8.0, 8.0, 0.05, 'imu_center_point_x', "垂直参考中心X偏移(米)", physics_layout)
        setup_spinbox(-8.0, 8.0, 0.05, 'imu_center_point_y', "垂直参考中心Y偏移(米)", physics_layout)
        setup_spinbox(0.05, 3.0, 0.05, 'imu_vertical_h', "位置单元垂直距离(米)", physics_layout)

        # 创建第二个标签页 - 通讯设置
        comm_tab = QWidget()
        comm_layout = QFormLayout(comm_tab)

        self.http_path_input = QLineEdit()
        self.http_path_input.setText(stored_config['current_sensor_http_base'])
        
        def update_http_path(value):
            stored_config['current_sensor_http_base'] = value

        self.http_path_input.textChanged.connect(update_http_path)
        comm_layout.addRow(QLabel('电流传感器HTTP通讯路径'), self.http_path_input)

        self.z_axis_correction_checkbox = QCheckBox("启用Z轴矫正")
        self.z_axis_correction_checkbox.setChecked(stored_config['enable_z_axis_correction'])

        def update_z_axis_correction(state):
            stored_config['enable_z_axis_correction'] = bool(state)

        self.z_axis_correction_checkbox.stateChanged.connect(update_z_axis_correction)
        comm_layout.addRow(self.z_axis_correction_checkbox)

        # 添加标签页
        tab_widget.addTab(physics_tab, "物理参数")
        tab_widget.addTab(comm_tab, "通讯设置")
        
        layout.addWidget(tab_widget)

    def update_stored_config(self, updated_config):
        for key, value in updated_config.items():
            if key in self.spinboxes:
                self.spinboxes[key].setValue(value)
