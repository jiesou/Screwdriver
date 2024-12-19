from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QSlider, QDoubleSpinBox, QLabel
from PyQt5.QtCore import Qt

from ..units.event_bus import event_bus
from ..units.config import config

class ConfigView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # 物理地图宽度
        self.map_width_spinbox = QDoubleSpinBox()
        self.map_width_spinbox.setMinimum(1.0)
        self.map_width_spinbox.setMaximum(100.0)
        self.map_width_spinbox.setSingleStep(0.1)
        self.map_width_spinbox.setValue(float(config['map_physics_width']))
        self.map_width_spinbox.valueChanged.connect(self.update_map_width)
        form_layout.addRow(QLabel("物理地图宽度(米)"), self.map_width_spinbox)

        # 物理地图高度
        self.map_height_spinbox = QDoubleSpinBox()
        self.map_height_spinbox.setMinimum(1.0)
        self.map_height_spinbox.setMaximum(100.0)
        self.map_height_spinbox.setSingleStep(0.1)
        self.map_height_spinbox.setValue(float(config['map_physics_height']))
        self.map_height_spinbox.valueChanged.connect(self.update_map_height)
        form_layout.addRow(QLabel("物理地图高度(米)"),  self.map_height_spinbox)

        # 垂直参考中心X坐标
        self.center_x_spinbox = QDoubleSpinBox()
        self.center_x_spinbox.setMinimum(-8.0)
        self.center_x_spinbox.setMaximum(8.0)
        self.center_x_spinbox.setSingleStep(0.1)
        self.center_x_spinbox.setValue(float(config['imu_center_point'][0]))
        self.center_x_spinbox.valueChanged.connect(self.update_center_x)
        form_layout.addRow(QLabel("垂直参考中心X坐标(米)"), self.center_x_spinbox)

        # 垂直参考中心Y坐标
        self.center_y_spinbox = QDoubleSpinBox()
        self.center_y_spinbox.setMinimum(-8.0)
        self.center_y_spinbox.setMaximum(8.0)
        self.center_y_spinbox.setSingleStep(0.1)
        self.center_y_spinbox.setValue(float(config['imu_center_point'][1]))
        self.center_y_spinbox.valueChanged.connect(self.update_center_y)
        form_layout.addRow(QLabel("垂直参考中心Y坐标(米)"), self.center_y_spinbox)

        # 位置单元垂直距离
        self.vertical_h_spinbox = QDoubleSpinBox()
        self.vertical_h_spinbox.setMinimum(0.05)
        self.vertical_h_spinbox.setMaximum(3.0)
        self.vertical_h_spinbox.setSingleStep(0.05)
        self.vertical_h_spinbox.setValue(float(config['imu_vertical_h']))
        self.vertical_h_spinbox.valueChanged.connect(self.update_vertical_h)
        form_layout.addRow(QLabel("位置单元垂直距离(米)"),  self.vertical_h_spinbox)

        layout.addLayout(form_layout)

    def update_map_width(self, value):
        config['map_physics_width'] = value

    def update_map_height(self, value):
        config['map_physics_height'] = value

    def update_center_x(self, value):
        config['imu_center_point'] = (value, config['imu_center_point'][1])
        event_bus.processor_api.imu_api.processor.center_point = config['imu_center_point']

    def update_center_y(self, value):
        config['imu_center_point'] = (config['imu_center_point'][0], value)
        event_bus.processor_api.imu_api.processor.center_point = config['imu_center_point']

    def update_vertical_h(self, value):
        config['imu_vertical_h'] = value
        event_bus.processor_api.imu_api.processor.h = config['imu_vertical_h']