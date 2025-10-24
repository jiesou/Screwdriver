from PyQt6.QtCore import QObject, QSettings, pyqtSignal
from .types import ConfigData
from dataclasses import asdict, fields
import os


class Config(QObject):
    """配置管理类，使用 ConfigData dataclass 进行类型化"""
    updated = pyqtSignal(ConfigData)
    
    def __init__(self):
        super().__init__()
        self.settings = QSettings('Screwdriver', 'PyQt')
        self._config_data = self._load_config()
        self.update_env_for_processor()

    def _load_config(self) -> ConfigData:
        """从 QSettings 加载配置到 ConfigData"""
        config = ConfigData()
        for field in fields(ConfigData):
            key = field.name
            default = getattr(config, key)
            # 根据默认值类型指定type参数
            value = self.settings.value(key, default, type=type(default))
            setattr(config, key, value)
        return config

    def __getitem__(self, key: str):
        return getattr(self._config_data, key)
    def get(self, key: str, default=None):
        return getattr(self._config_data, key, default)
    def __setitem__(self, key: str, value):
        setattr(self._config_data, key, value)
        self.settings.setValue(key, value)
        self.settings.sync()
        # 发送完整的配置数据
        self.updated.emit(self._config_data)
        self.update_env_for_processor()
    
    def update_env_for_processor(self):
        """更新环境变量供 processor 使用"""
        os.environ['CURRENT_SENSOR_HTTP'] = self._config_data.current_sensor_http_base
        os.environ['IMU_COM_PORT'] = self._config_data.imu_com_port
        os.environ['ENABLE_Z_AXIS_CORRECTION'] = str(self._config_data.enable_z_axis_correction)
    
# 创建全局配置实例
stored_config = Config()