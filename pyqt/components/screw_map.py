from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import numpy as np

from pyqt.units.types import State

from ..units.stored_config import stored_config

class ScrewMap(QWidget):
    def __init__(self, state_update_on):
        super().__init__()
        state_update_on.connect(self.update_state)
        stored_config.updated.connect(self.update_config)

        self.screws = []
        self.position = None
        self.axes_flipped = False
        
        # 创建布局
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        self.flip_axes_button = QPushButton("切换 XY 轴")
        self.flip_axes_button.clicked.connect(self.toggle_axes)
        self.rotate_button = QPushButton("旋转90度")
        self.rotate_button.clicked.connect(self.rotate_90_degrees)
        button_layout.addWidget(self.flip_axes_button)
        button_layout.addWidget(self.rotate_button)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # 创建绘图窗口
        self.plot_widget = pg.PlotWidget()
        main_layout.addWidget(self.plot_widget)
        
        # 设置绘图属性
        self.plot_widget.setBackground(None)  # 设置背景透明
        self.plot_widget.showGrid(True, True)
        
        # 其他属性设置
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
        
        self.rotation_angle = 0  # 添加旋转角度属性
        
        # self.setMinimumSize(400, 400)
        
    def toggle_axes(self):
        self.axes_flipped = not self.axes_flipped
        self.update_plot()
        
    def rotate_90_degrees(self):
        self.rotation_angle = (self.rotation_angle + 90) % 360
        self.update_plot()
        
    def update_state(self, state: State):
        self.screws = state.screws
        self.position = state.position
        self.update_plot()
    
    def update_config(self, updated_config):
        self.plot_widget.setXRange(-updated_config['map_physics_width']/2, updated_config['map_physics_width']/2)
        self.plot_widget.setYRange(-updated_config['map_physics_width']/2, updated_config['map_physics_width']/2)
        
    def update_plot(self):
        # 获取当前视图的像素比例
        view_box = self.plot_widget.getViewBox()
        screen_size = view_box.viewPixelSize()
        pixel_scale = (screen_size[0] + screen_size[1]) / 2  # 取平均作为比例因子
        
        # 更新螺丝位置
        spots = []
        for screw in self.screws:
            color = {
                '已定位': (255, 0, 0),
                '已完成': (0, 255, 0)
            }.get(screw['status'], (0, 0, 255))
            
            # 根据当前视图比例调整 size
            display_size = screw['position']['allowOffset'] * 2 / pixel_scale
            
            x, y = screw['position']['x'], screw['position']['y']
            
            # 先处理旋转
            if self.rotation_angle == 90:
                x, y = -y, x
            elif self.rotation_angle == 180:
                x, y = -x, -y
            elif self.rotation_angle == 270:
                x, y = y, -x
                
            # 再处理xy轴翻转
            if self.axes_flipped:
                x, y = y, x
            
            spots.append({
                'pos': (x, y),
                'size': display_size,  # 使用调整后的大小
                'pen': None,
                'brush': pg.mkBrush(*color, 90),  # 50是透明度
                'symbol': 'o',
                'data': screw['tag']
            })
        
        self.screw_scatter.setData(spots)
        
        # 更新当前位置
        if self.position:
            x, y = self.position['x'], self.position['y']
            
            # 同样处理旋转
            if self.rotation_angle == 90:
                x, y = -y, x
            elif self.rotation_angle == 180:
                x, y = -x, -y
            elif self.rotation_angle == 270:
                x, y = y, -x
                
            if self.axes_flipped:
                x, y = y, x
            self.position_scatter.setData([x], [y])
        else:
            self.position_scatter.clear()
