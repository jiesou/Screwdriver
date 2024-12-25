from PyQt6.QtCore import QObject, QSettings, pyqtSignal

DEFAULT_CONFIG = {
    'init_screws': [],
    'map_physics_width': 2.0,
    'map_physics_height': 2.0,
    'imu_vertical_h': 1.0,
    'imu_center_point_x': 0.0,
    'imu_center_point_y': 0.0
}

class Config(QObject):
    stored_config_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings('Screwdriver', 'PyQt')

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
        self.stored_config_updated.emit({key: value})


# 创建全局配置实例
stored_config = Config()