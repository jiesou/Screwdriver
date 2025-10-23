from typing import TypedDict, List, Dict, Any, Optional, Union


class Position(TypedDict):
    x: float
    y: float


class Screw(TypedDict, total=False):
    tag: Union[str, int]
    position: Position
    allowOffset: Optional[float]


class StateDict(TypedDict):
    position: List[float]
    screws: List[Screw]
    is_screw_tightening: bool
    screw_count: int


# PartialState 可以表示更新片段，允许只包含部分字段
class PartialState(TypedDict, total=False):
    position: Optional[List[float]]
    screws: Optional[List[Screw]]
    is_screw_tightening: Optional[bool]
    screw_count: Optional[int]


# 配置更新的通用类型（stored_config.updated 发出的 payload 为 {key: value}）
ConfigUpdate = Dict[str, Any]
from typing import TypedDict, List, Dict, Any, Optional, Union


class Position(TypedDict):
    x: float
    y: float


class Screw(TypedDict, total=False):
    tag: Union[str, int]
    position: Position
    allowOffset: Optional[float]


class StateDict(TypedDict):
    position: List[float]
    screws: List[Screw]
    is_screw_tightening: bool
    screw_count: int


# PartialState 可以表示更新片段，允许只包含部分字段
class PartialState(TypedDict, total=False):
    position: Optional[List[float]]
    screws: Optional[List[Screw]]
    is_screw_tightening: Optional[bool]
    screw_count: Optional[int]
