from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from mpl_toolkits.mplot3d import Axes3D

class RayVisualizer(QWidget):
    def __init__(self, state_update_on):
        super().__init__()
        state_update_on.connect(self.update_state)
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        
        # 设置最小尺寸
        self.setMinimumSize(400, 400)
        
        # 创建 matplotlib 图形和 3D 轴
        self.figure = plt.figure(figsize=(5, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111, projection='3d')
        
        # 添加导航工具栏，实现旋转、缩放等功能
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        
        # 存储射线图形对象，避免重复创建
        self.top_line = None
        self.end_line = None
        self.top_point = None
        self.end_point = None
        
        # 设置坐标轴范围和标签
        self.setup_axes()
        
        # 初始化射线数据
        self.top_angles = {'x': 0, 'y': 0}
        self.end_angles = {'x': 0, 'y': 0}
        
        # 创建初始图形
        self.create_initial_plot()
        
        # 设置定时器控制更新频率
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_rays)
        self.update_timer.start(50)  # 每100毫秒更新一次

    def setup_axes(self):
        """设置坐标轴范围和标签"""
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_xlim([-1, 1])
        self.ax.set_ylim([-1, 1])
        self.ax.set_zlim([-1, 1])
        self.ax.set_title('Ray Visualization')
        self.ax.view_init(elev=30, azim=45)

    def create_initial_plot(self):
        """创建初始图形"""
        # 初始位置
        top_start = np.array([0, 0, 0])
        end_start = np.array([0.5, 0.07, -1.0])
        ray_length = 2.0
        
        # 初始方向
        top_dir = np.array([0, 0, -1])
        end_dir = np.array([0, 0, 1])
        
        top_end = top_start + top_dir * ray_length
        end_end = end_start + end_dir * ray_length
        
        # 创建射线对象
        self.top_line, = self.ax.plot([top_start[0], top_end[0]], 
                                     [top_start[1], top_end[1]], 
                                     [top_start[2], top_end[2]], 
                                     'r-', linewidth=2, label='TOP')
        
        self.end_line, = self.ax.plot([end_start[0], end_end[0]], 
                                     [end_start[1], end_end[1]], 
                                     [end_start[2], end_end[2]], 
                                     'b-', linewidth=2, label='END')
        
        # 创建点对象
        self.top_point = self.ax.scatter([top_start[0]], [top_start[1]], [top_start[2]], 
                                       color='red', s=50)
        
        self.end_point = self.ax.scatter([end_start[0]], [end_start[1]], [end_start[2]], 
                                       color='blue', s=50)
        
        self.ax.legend()
        self.canvas.draw()

    def update_state(self, state):
        """更新状态"""
        top_angles = state['imu_top_data'].get('angle', {'x': 0, 'y': 0})
        end_angles = state['imu_end_data'].get('angle', {'x': 0, 'y': 0})
        self.top_angles = top_angles
        self.end_angles = end_angles

    def update_rays(self):
        """更新射线显示"""
        try:
            # TOP射线计算
            tx_rad = np.radians(self.top_angles['x'])
            ty_rad = np.radians(self.top_angles['y'])
            top_start = np.array([0, 0, 0])
            top_dir = np.array([
                math.tan(ty_rad),   
                math.tan(tx_rad),   
                -1.0               
            ])
            top_dir = top_dir / np.linalg.norm(top_dir)
            
            # END射线计算
            ex_rad = np.radians(self.end_angles['x'])
            ey_rad = np.radians(self.end_angles['y'])
            end_start = np.array([0.5, 0.07, -1.0])
            end_dir = np.array([
                math.tan(ey_rad),   
                math.tan(ex_rad),   
                1.0                
            ])
            end_dir = end_dir / np.linalg.norm(end_dir)
            
            # 计算端点
            ray_length = 2.0
            top_end = top_start + top_dir * ray_length
            end_end = end_start + end_dir * ray_length
            
            # 更新射线数据
            self.top_line.set_data_3d([top_start[0], top_end[0]], 
                                    [top_start[1], top_end[1]], 
                                    [top_start[2], top_end[2]])
            
            self.end_line.set_data_3d([end_start[0], end_end[0]], 
                                    [end_start[1], end_end[1]], 
                                    [end_start[2], end_end[2]])
            
            # 更新点数据
            self.top_point._offsets3d = ([top_start[0]], [top_start[1]], [top_start[2]])
            self.end_point._offsets3d = ([end_start[0]], [end_start[1]], [end_start[2]])
            
            # 仅更新必要部分，不重绘整个图形
            self.canvas.draw_idle()
            
        except Exception as e:
            print(f"Error updating rays: {e}")