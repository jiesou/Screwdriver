from typing import TypedDict, Any, Optional, Union
from dataclasses import dataclass, field, asdict

class Position(TypedDict):
    x: float
    y: float


class Screw(TypedDict, total=False):
    tag: Union[str, int]
    position: Position
    allowOffset: Optional[float]
    status: str


class SensorConnection(TypedDict):
    imu: bool = False
    current: bool = False
    encoder: bool = False

@dataclass
class State:
    position: Position = field(default_factory=lambda: {"x": 0.0, "y": 0.0})
    located_screw: Optional[Screw] = None
    is_screw_tightening: bool = False
    screw_count: int = 0
    screws: list[Screw] = field(default_factory=list)
    products_finished: int = 0
    sensor_connection: SensorConnection = field(default_factory=lambda: SensorConnection())
    
    def __getitem__(self, key: Any) -> Any:
        return getattr(self, key)
    def __setitem__(self, key: Any, value: Any) -> None:
        setattr(self, key, value)
    def get(self, key: Any, default: Any = None) -> Any:
        return getattr(self, key, default)


@dataclass
class ConfigData:
    """配置数据类"""
    init_screws: list[Screw] = field(default_factory=lambda: [
        {"tag": "1", "position": {"x": 0.05, "y": 0.2, "allowOffset": 0.08}},
        {"tag": "2", "position": {"x": 0.05, "y": -0.2, "allowOffset": 0.08}},
        {"tag": "3", "position": {"x": 0.5, "y": 0.2, "allowOffset": 0.1}},
        {"tag": "4", "position": {"x": 0.5, "y": -0.2, "allowOffset": 0.1}}
    ])
    map_physics_width: float = 2.0
    imu_center_point_x: float = 0.0
    imu_center_point_y: float = 0.0
    imu_vertical_h: float = 1.0
    current_sensor_http_base: str = 'http://192.168.4.1/api/status'
    imu_com_port: str = '/dev/ttyUSB0'
    enable_z_axis_correction: bool = False
    
    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)
    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)
    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)
    def items(self):
        return asdict(self).items()
