from PyQt5.QtCore import QObject, QSettings, pyqtSignal

DEFAULT_CONFIG = {
    'init_screws': [],
    'map_physics_width': 2,
    'map_physics_height': 2,
    'imu_vertical_h': 1.0,
    'imu_center_point_x': 0,
    'imu_center_point_y': 0
}

class Config(QObject):
    stored_config_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings('Screwdriver', 'PyQt')

    def __getitem__(self, key):
        value = self.settings.value(key, DEFAULT_CONFIG[key])
        return value

    def get(self, key, default=None):
        return self.settings.value(key, default)

    def __setitem__(self, key, value):
        self.settings.setValue(key, value)
        print(f"Setting {key} to {value}")
        self.settings.sync()
        self.stored_config_updated.emit({key: value})


# 创建全局配置实例
stored_config = Config()