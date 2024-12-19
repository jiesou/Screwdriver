from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
import pyqtgraph as pg
import numpy as np

from ..units.event_bus import event_bus
from ..units.config import config

class ScrewMap(QWidget):
    def __init__(self):
        super().__init__()
        self.screws = []
        self.position = None
        
        # 创建布局
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # 创建绘图窗口
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)
        
        # 设置绘图属性
        self.plot_widget.setAspectLocked(True)
        self.plot_widget.setXRange(-config['map_physics_width']/2, config['map_physics_width']/2)
        self.plot_widget.setYRange(-config['map_physics_height']/2, config['map_physics_height']/2)
        self.plot_widget.showGrid(True, True)
        
        # 创建散点图项
        self.screw_scatter = pg.ScatterPlotItem()
        self.position_scatter = pg.ScatterPlotItem(size=8, pen=pg.mkPen(None), brush=pg.mkBrush(255, 0, 0))
        
        self.plot_widget.addItem(self.screw_scatter)
        self.plot_widget.addItem(self.position_scatter)
        
        # 连接事件总线
        event_bus.state_updated.connect(self.update_state)
        
        self.setMinimumSize(800, 800)
        
    def update_state(self, state):
        self.screws = state.get('screws', [])
        self.position = state.get('position', None)
        self.update_plot()
        
    def update_plot(self):
        # 更新螺丝位置
        spots = []
        for screw in self.screws:
            color = {
                '已定位': (255, 255, 0),
                '已完成': (0, 255, 0)
            }.get(screw['status'], (0, 0, 255))
            
            spots.append({
                'pos': (screw['position']['x'], screw['position']['y']),
                'size': screw['position']['allowOffset'] * 2 * 400,  # 转换到像素大小
                'pen': None,
                'brush': pg.mkBrush(*color, 50),  # 50是透明度
                'symbol': 'o',
                'data': screw['tag']
            })
        
        self.screw_scatter.setData(spots)
        
        # 更新当前位置
        if self.position:
            self.position_scatter.setData(
                [self.position[0]], 
                [self.position[1]]
            )
        else:
            self.position_scatter.clear()
