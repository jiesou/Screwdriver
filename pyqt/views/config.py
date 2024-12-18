from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QSlider, QSpinBox, QLabel
from PyQt5.QtCore import Qt

from ..units.config import config

class ConfigView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # 物理地图宽度
        self.map_width_slider = QSlider(Qt.Horizontal)
        self.map_width_slider.setMinimum(1)
        self.map_width_slider.setMaximum(100)
        self.map_width_slider.setValue(int(config['map_physics_width']))
        self.map_width_slider.valueChanged.connect(self.update_map_width)
        form_layout.addRow(QLabel("物理地图宽度(米)"), self.map_width_slider)

        self.map_width_spinbox = QSpinBox()
        self.map_width_spinbox.setMinimum(1)
        self.map_width_spinbox.setMaximum(100)
        self.map_width_spinbox.setValue(int(config['map_physics_width']))
        self.map_width_spinbox.valueChanged.connect(self.update_map_width)
        form_layout.addRow(self.map_width_spinbox)

        # 物理地图高度
        self.map_height_slider = QSlider(Qt.Horizontal)
        self.map_height_slider.setMinimum(1)
        self.map_height_slider.setMaximum(100)
        self.map_height_slider.setValue(int(config['map_physics_height']))
        self.map_height_slider.valueChanged.connect(self.update_map_height)
        form_layout.addRow(QLabel("物理地图高度(米)"), self.map_height_slider)

        self.map_height_spinbox = QSpinBox()
        self.map_height_spinbox.setMinimum(1)
        self.map_height_spinbox.setMaximum(100)
        self.map_height_spinbox.setValue(int(config['map_physics_height']))
        self.map_height_spinbox.valueChanged.connect(self.update_map_height)
        form_layout.addRow(self.map_height_spinbox)

        # 垂直参考中心X坐标
        self.center_x_slider = QSlider(Qt.Horizontal)
        self.center_x_slider.setMinimum(0)
        self.center_x_slider.setMaximum(40)
        self.center_x_slider.setValue(int(config['imu_center_point'][0]))
        self.center_x_slider.valueChanged.connect(self.update_center_x)
        form_layout.addRow(QLabel("垂直参考中心X坐标(米)"), self.center_x_slider)

        self.center_x_spinbox = QSpinBox()
        self.center_x_spinbox.setMinimum(0)
        self.center_x_spinbox.setMaximum(40)
        self.center_x_spinbox.setValue(int(config['imu_center_point'][0]))
        self.center_x_spinbox.valueChanged.connect(self.update_center_x)
        form_layout.addRow(self.center_x_spinbox)

        # 垂直参考中心Y坐标
        self.center_y_slider = QSlider(Qt.Horizontal)
        self.center_y_slider.setMinimum(0)
        self.center_y_slider.setMaximum(40)
        self.center_y_slider.setValue(int(config['imu_center_point'][1]))
        self.center_y_slider.valueChanged.connect(self.update_center_y)
        form_layout.addRow(QLabel("垂直参考中心Y坐标(米)"), self.center_y_slider)

        self.center_y_spinbox = QSpinBox()
        self.center_y_spinbox.setMinimum(0)
        self.center_y_spinbox.setMaximum(40)
        self.center_y_spinbox.setValue(int(config['imu_center_point'][1]))
        self.center_y_spinbox.valueChanged.connect(self.update_center_y)
        form_layout.addRow(self.center_y_spinbox)

        # 位置单元垂直距离
        self.vertical_h_slider = QSlider(Qt.Horizontal)
        self.vertical_h_slider.setMinimum(0)
        self.vertical_h_slider.setMaximum(15)
        self.vertical_h_slider.setValue(int(config['imu_vertical_h']))
        self.vertical_h_slider.valueChanged.connect(self.update_vertical_h)
        form_layout.addRow(QLabel("位置单元垂直距离(米)"), self.vertical_h_slider)

        self.vertical_h_spinbox = QSpinBox()
        self.vertical_h_spinbox.setMinimum(0)
        self.vertical_h_spinbox.setMaximum(15)
        self.vertical_h_spinbox.setValue(int(config['imu_vertical_h']))
        self.vertical_h_spinbox.valueChanged.connect(self.update_vertical_h)
        form_layout.addRow(self.vertical_h_spinbox)

        layout.addLayout(form_layout)

    def update_map_width(self, value):
        config['map_physics_width'] = value
        self.map_width_spinbox.setValue(value)

    def update_map_height(self, value):
        config['map_physics_height'] = value
        self.map_height_spinbox.setValue(value)

    def update_center_x(self, value):
        config['imu_center_point'] = (value, config['imu_center_point'][1])
        self.center_x_spinbox.setValue(value)

    def update_center_y(self, value):
        config['imu_center_point'] = (config['imu_center_point'][0], value)
        self.center_y_spinbox.setValue(value)

    def update_vertical_h(self, value):
        config['imu_vertical_h'] = value
        self.vertical_h_spinbox.setValue(value)