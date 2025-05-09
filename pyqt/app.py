from PyQt6.QtWidgets import (QMainWindow, QWidget, QPushButton, 
                           QVBoxLayout, QHBoxLayout, QLabel)
from PyQt6.QtCore import Qt, QEvent

import json

from .views.dash import DashView
from .views.config import ConfigView
from .components.screw_counter import ScrewCounter

from .units.state_bus import state_bus
from .units.stored_config import stored_config

from processor.imu.communication import z_axes_to_zero

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("螺丝管理系统")
        
        # 创建主容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # 顶部工具栏
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar.setStyleSheet("background-color: aliceblue;")

        toolbar_layout.addWidget(ScrewCounter())
        
        # 操作按钮
        self.reset_z_btn = QPushButton("重置Z轴角")
        self.reset_z_btn.clicked.connect(lambda: z_axes_to_zero())
        toolbar_layout.addWidget(self.reset_z_btn)

        self.reset_desktop_btn = QPushButton("重置桌面坐标系")
        self.reset_desktop_btn.clicked.connect(self.reset_desktop)
        toolbar_layout.addWidget(self.reset_desktop_btn)
        
        # 位置信息显示
        self.position_label = QLabel("等待操作")
        self.position_label.setStyleSheet("color: green;")
        state_bus.updated.connect(
            lambda data: self.position_label.setText(
                f"X: {data['position'][0]*100:.1f} cm Y: {data['position'][1]*100:.1f} cm {'拧螺丝中' if data.get('is_screw_tightening') else '未拧螺丝'} "
                f"连接状态：IMU {'已连接' if data['sensor_connection']['imu'] else '未连接'}；"
                f"电流  {'已连接' if data['sensor_connection']['current'] else '未连接'}"
            ) if data.get('position') else None
        )
        
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.position_label)

        # 添加工具栏到主布局
        main_layout.addWidget(toolbar)

        # 添加仪表盘视图
        self.dash_view = DashView()
        main_layout.addWidget(self.dash_view)
        
        self.config_view = ConfigView()
        main_layout.addWidget(self.config_view)
        
        print("======PyQt inited======")
        

    def reset_desktop(self):
        if 'position' in state_bus.state:
            x, y = state_bus.state['position']
            # 直接更新配置
            stored_config['imu_center_point_x'] = float(stored_config['imu_center_point_x'] - x)
            stored_config['imu_center_point_y'] = float(stored_config['imu_center_point_y'] - y)