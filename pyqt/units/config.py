import json
import os
from xdg import BaseDirectory

STORAGE_PATH = os.path.join(BaseDirectory.xdg_config_home, 'screwdriver', 'pyqt', 'config.json')

DEFAULT_CONFIG = {
    'init_screws': [],
    'map_physics_width': 2,
    'map_physics_height': 2,
    'imu_vertical_h': 1.0,
    'imu_center_point': (0, 0)
}

print(f"CONFIG_STORAGE_PATH: {STORAGE_PATH}")

class Config(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            if os.path.exists(STORAGE_PATH):
                with open(STORAGE_PATH, 'r') as f:
                    self.update({**DEFAULT_CONFIG, **json.load(f)})
            else:
                self.update(DEFAULT_CONFIG.copy())
        except Exception as e:
            print(f"Error loading config: {e}")
            self.update(DEFAULT_CONFIG.copy())
    
    def __setitem__(self, key, value):
        super().__setitem__(key, value)

        print(f"Saving config to {STORAGE_PATH}")
        os.makedirs(os.path.dirname(STORAGE_PATH), exist_ok=True)
        with open(STORAGE_PATH, 'w') as f:
            json.dump(self, f, indent=2)

# 创建全局配置实例
config = Config()