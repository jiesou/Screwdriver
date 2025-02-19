from PyQt6.QtCore import QObject, QSettings, pyqtSignal
import os

DEFAULT_CONFIG = {
    'init_screws': [
        { "tag": "1", "position": { "x": 0.05, "y": 0.2, "allowOffset": 0.08 } },
        { "tag": "2", "position": { "x": 0.05, "y": -0.2, "allowOffset": 0.08 } },
        { "tag": "3", "position": { "x": 0.5, "y": 0.2, "allowOffset": 0.1 } },
        { "tag": "4", "position": { "x": 0.5, "y": -0.2, "allowOffset": 0.1 } }
    ],
    'map_physics_width': 2.0,
    'imu_center_point_x': 0.0,
    'imu_center_point_y': 0.0,
    'imu_vertical_h': 1.0,
    'current_sensor_http_base': 'http://192.168.4.1/status',
    'imu_top_com_port': '/dev/ttyUSB0',
    'imu_end_com_port': '/dev/ttyUSB1',
    'enable_z_axis_correction': True,
}

class Config(QObject):
    updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings('Screwdriver', 'PyQt')
        self.update_env_for_porcessor()

    def __getitem__(self, key):
        default = DEFAULT_CONFIG[key]
        # 根据默认值类型指定type参数
        value = self.settings.value(key, default, type=type(default))
        return value

    def get(self, key, default=None):
        return self.settings.value(key, default, type=type(default) if default is not None else None)

    def __setitem__(self, key, value):
        self.settings.setValue(key, value)
        self.settings.sync()
        self.updated.emit({key: value})
        self.update_env_for_porcessor()
    
    def update_env_for_porcessor(self):
        os.environ['CURRENT_SENSOR_HTTP'] = self['current_sensor_http_base']
        os.environ['IMU_TOP_COM_PORT'] = self['imu_top_com_port']
        os.environ['IMU_END_COM_PORT'] = self['imu_end_com_port']
        os.environ['ENABLE_Z_AXIS_CORRECTION'] = str(self['enable_z_axis_correction'])


# 创建全局配置实例
stored_config = Config()