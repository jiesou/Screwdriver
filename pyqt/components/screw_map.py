from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import numpy as np

from ..units.stored_config import stored_config

class ScrewMap(QWidget):
    def __init__(self, state_update_on):
        super().__init__()
        state_update_on.connect(self.update_state)
        stored_config.stored_config_updated.connect(self.update_config)

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
        self.plot_widget.setXRange(-stored_config['map_physics_width']/2, stored_config['map_physics_width']/2)
        self.plot_widget.setYRange(-stored_config['map_physics_width']/2, stored_config['map_physics_width']/2)
        self.plot_widget.showGrid(True, True)
        # 获取 ViewBox 并设置缩放限制
        self.plot_widget.getViewBox().setLimits(
            minXRange=0.5,  # 最大放大倍数
            minYRange=0.5,  # 最大放大倍数
        )
        
        # 创建散点图项
        self.screw_scatter = pg.ScatterPlotItem()
        self.position_scatter = pg.ScatterPlotItem(size=8, pen=pg.mkPen(None), brush=pg.mkBrush(255, 0, 0))
        
        self.plot_widget.addItem(self.screw_scatter)
        self.plot_widget.addItem(self.position_scatter)
        
        
        # self.setMinimumSize(400, 400)
        
    def update_state(self, state):
        self.screws = state.get('screws', [])
        self.position = state.get('position', None)
        self.update_plot()
    
    def update_config(self, _):
        self.plot_widget.setXRange(-stored_config['map_physics_width']/2, stored_config['map_physics_width']/2)
        self.plot_widget.setYRange(-stored_config['map_physics_width']/2, stored_config['map_physics_width']/2)
        
    def update_plot(self):
        # 获取当前视图的像素比例
        view_box = self.plot_widget.getViewBox()
        screen_size = view_box.viewPixelSize()
        pixel_scale = (screen_size[0] + screen_size[1]) / 2  # 取平均作为比例因子
        
        # 更新螺丝位置
        spots = []
        for screw in self.screws:
            color = {
                '已定位': (255, 255, 0),
                '已完成': (0, 255, 0)
            }.get(screw['status'], (0, 0, 255))
            
            # 根据当前视图比例调整 size
            display_size = screw['position']['allowOffset'] * 2 / pixel_scale
            
            spots.append({
                'pos': (screw['position']['x'], screw['position']['y']),
                'size': display_size,  # 使用调整后的大小
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
