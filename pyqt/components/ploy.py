from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QTimer
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

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
        self.update_timer.start(50)  # 每50毫秒更新一次(20hz)

    def setup_axes(self):
        """设置坐标轴范围和标签"""
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')
        self.ax.set_xlim([0, 1])
        self.ax.set_ylim([0, 1])
        self.ax.set_zlim([-1, 1])
        self.ax.view_init(elev=30, azim=35)

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
        
        self.closest_line = self.ax.plot([0, 0], [0, 0], [0, 0], 'g--', linewidth=2, label='Closest Points')
        
        # 创建点对象
        self.mid_point = self.ax.scatter([0], [0], [0], color='green', s=50)

        self.top_point = self.ax.scatter([top_start[0]], [top_start[1]], [top_start[2]], 
                                       color='red', s=50)
        
        self.end_point = self.ax.scatter([end_start[0]], [end_start[1]], [end_start[2]], 
                                       color='blue', s=50)
        
        self.canvas.draw()

    def update_state(self, state):
        """更新状态"""
        self.top_angles = state['imu_top_data'].get('angle', {'x': 0, 'y': 0})
        self.end_angles = state['imu_end_data'].get('angle', {'x': 0, 'y': 0})

    def update_rays(self):
        """更新射线显示"""
        try:
            # TOP射线计算
            tx_rad = np.radians(self.top_angles['x'])
            ty_rad = np.radians(-self.top_angles['y'])
            top_start = np.array([0, 0, 0])
            top_dir = np.array([
                math.tan(ty_rad),   
                math.tan(tx_rad),   
                -1.0               
            ])
            # 归一化：只保留方向信息。并固定射线长度为 -1.0
            top_dir = top_dir / np.linalg.norm(top_dir)
            
            # END射线计算
            ex_rad = np.radians(self.end_angles['x'])
            ey_rad = np.radians(-self.end_angles['y'])
            end_start = np.array([0.5, 0.07, -1.0])
            end_dir = np.array([
                math.tan(ey_rad),   
                math.tan(ex_rad),   
                1.0                
            ])
            # 归一化：只保留方向信息。并固定射线长度为 -1.0
            end_dir = end_dir / np.linalg.norm(end_dir)
            
            # 计算射线末端
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
            
            # ****计算两条射线上的最近点****
            # 向量：如一个向量 V = [vx, vy, vz]，vx 就是 V 在 x 轴的分量，表示水平方向有多长。

            # 计算从 end_start 指向 top_start 的向量 w0
            w0 = top_start - end_start

            # 分别计算点积值
            a = np.dot(top_dir, top_dir)       # top_dir 自己的长度平方（归一化后为1）
            b = np.dot(top_dir, end_dir)        # 两个方向在相同坐标轴上的"重合"程度
            c = np.dot(end_dir, end_dir)         # end_dir 自己的长度平方（归一化后为1）
            d = np.dot(top_dir, w0)              # w0 在 top_dir 方向上的分量（投影长度）
            e = np.dot(end_dir, w0)              # w0 在 end_dir 方向上的分量

            # 计算参数 sc 和 tc，表示从各射线起点沿方向走多少长度可以到达最近点
            # 计算时只考虑方向，不考虑长度（点积后）
            sc = (b * e - c * d) / (a * c - b * b)
            tc = (a * e - b * d) / (a * c - b * b)

            # 利用参数计算两条射线上的最近点坐标
            closest_point_top = top_start + sc * top_dir
            closest_point_end = end_start + tc * end_dir

            # 更新最近点连线
            self.closest_line[0].set_data_3d([closest_point_top[0], closest_point_end[0]],
                                           [closest_point_top[1], closest_point_end[1]],
                                           [closest_point_top[2], closest_point_end
                                           [2]])

            # 求中点
            mid_point = (closest_point_top + closest_point_end) / 2

            self.mid_point._offsets3d = ([mid_point[0]], [mid_point[1]], [mid_point
            [2]])


            # 仅更新必要部分
            self.canvas.draw_idle()
            
        except Exception as e:
            print(f"Error updating rays: {e}")