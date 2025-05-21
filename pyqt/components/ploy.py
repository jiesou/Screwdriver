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
        """创建初始图形，展示连杆模型的可视化"""
        # 固定点位置
        top_pos = np.array([0.0, 0.0, 0.0])
        end_pos = np.array([0.4, 0.0, 0.0])
        
        # 初始中间点（垂直段两端点）
        M = np.array([0.25, 0.0, -0.15])  # 上端点
        N = np.array([0.25, 0.0, -0.15])  # 下端点
        
        # 创建中间连接点
        self.M_point = self.ax.scatter([M[0]], [M[1]], [M[2]], 
                                    color='green', s=10, label='M')
        self.N_point = self.ax.scatter([N[0]], [N[1]], [N[2]], 
                                    color='yellow', s=10, label='N')
        
        # 创建连接线        
        self.end_line, = self.ax.plot([end_pos[0], N[0]], 
                                    [end_pos[1], N[1]], 
                                    [end_pos[2], N[2]], 
                                    'b-', linewidth=1)
        self.top_line, = self.ax.plot([top_pos[0], M[0]], 
                                    [top_pos[1], M[1]], 
                                    [top_pos[2], M[2]], 
                                    'r-', linewidth=1)
        
        # 创建垂直连接段
        self.vertical_line, = self.ax.plot([M[0], N[0]], 
                                        [M[1], N[1]], 
                                        [M[2], N[2]], 
                                        'g-', linewidth=0)
        
        # 创建射线（使用虚线表示）
        self.end_ray, = self.ax.plot([end_pos[0], end_pos[0]], 
                                    [end_pos[1], end_pos[1]], 
                                    [end_pos[2], end_pos[2]], 
                                    'b--', linewidth=1)
        self.top_ray, = self.ax.plot([top_pos[0], top_pos[0]], 
                                    [top_pos[1], top_pos[1]], 
                                    [top_pos[2], top_pos[2]], 
                                    'r--', linewidth=1)
        # 创建角度指示器（X平面）
        self.angle_top_x = self.ax.plot([0], [0], [0], 'r-', linewidth=2)[0]
        self.angle_end_x = self.ax.plot([0], [0], [0], 'b-', linewidth=2)[0]
        
        # 创建角度指示器（Y平面）
        self.angle_top_y = self.ax.plot([0], [0], [0], 'r-', linewidth=2)[0]
        self.angle_end_y = self.ax.plot([0], [0], [0], 'b-', linewidth=2)[0]
        
        # 创建角度标签
        self.angle_text_top_x = self.ax.text(0, 0, -0.5, "αx: 0°", color='r', size=8)
        self.angle_text_top_y = self.ax.text(0, 0, -0.6, "αy: 0°", color='r', size=8)
        self.angle_text_end_x = self.ax.text(0.5, 0, -0.5, "βx: 0°", color='b', size=8)
        self.angle_text_end_y = self.ax.text(0.5, 0, -0.6, "βy: 0°", color='b', size=8)
        
        # 添加图例
        # self.ax.legend()
        
        # 更新画布
        self.canvas.draw()

    def update_state(self, state):
        """更新状态"""
        self.top_angles = state['imu_top_data'].get('angle', {'x': 0, 'y': 0})
        self.end_angles = state['imu_end_data'].get('angle', {'x': 0, 'y': 0})


    def update_rays(self):
        """更新射线显示 - 考虑固定长度连杆模型"""
        try:

            # 1) 二维解算函数：给定基线 D、上下两条射线与水平线的夹角 alpha/beta (rad)、目标竖直距离 L，
            #    求解两条射线上同一 x 处的两点 M(z_m) 和 N(z_n)
            #    alpha 是 TOP，连接 M；beta 是 END，连接 N
            def solve_2d(D, beta, alpha, L):
                print(f"D: {D}, alpha: {alpha}, beta: {beta}, L: {L}")
                # 公式： x = (D * tan(beta) - L) / (tan(alpha) + tan(beta))
                x = (D * np.tan(beta) - L) / (np.tan(alpha) + np.tan(beta))
                # 对应的 z 坐标（注意 2D 中 y 轴对应我们的 z 轴）
                z_m = x * - np.tan(alpha)
                z_n = (x - D) * np.tan(beta)
                return x, z_m, z_n
            
            # 3) 两个固定点的 3D 坐标
            top_pos = np.array([0.5, 0.0, 0.0])
            end_pos = np.array([0.0, 0.0, 0.0])

            # 把角度转成弧度
            top_X = np.deg2rad(self.top_angles['x'])
            top_Y = np.deg2rad(self.top_angles['y'])
            end_X = np.deg2rad(self.end_angles['x'])
            end_Y = np.deg2rad(self.end_angles['y'])
            # 射线计算
            # 射线起点固定
            top_dir = np.array([
                math.tan(top_Y),
                math.tan(top_X),
                -1.0
            ])
            end_dir = np.array([
                math.tan(end_Y),
                math.tan(end_X),
                -1.0
            ])
            # 归一化函数
            def normalize(vec):
                norm = np.linalg.norm(vec)
                return vec / norm if norm != 0 else vec

            # 更新射线
            top_dir_norm = normalize(top_dir)
            end_dir_norm = normalize(end_dir)

            L = 0.2

            # —— 辅助：从方向向量算出 2D 夹角 —— 
            alpha_inXPanel = math.acos(-top_dir_norm[0])
            alpha_inYPanel = math.acos(-top_dir_norm[1])
            beta_inXPanel = math.acos(end_dir_norm[0])
            beta_inYPanel = math.acos(end_dir_norm[1])

            # 2) 在 XZ 平面上解：基线长度 D_x
            D_x = top_pos[0] - end_pos[0]
            x_mn_inXPanel, z_m_inXPanel, z_n_inXPanel = solve_2d(D_x, alpha_inXPanel, beta_inXPanel, L)
            
            # 3) 在 YZ 平面上解：基线长度 D_y
            D_y = top_pos[1] - end_pos[1]
            y_mn_inYPanel, z_m_inYPanel, z_n_inYPanel = solve_2d(D_y, alpha_inYPanel, beta_inYPanel, L)
            
            # 5) 合并为 3D 点
            M = np.array([ x_mn_inXPanel,  y_mn_inYPanel,  z_m_inXPanel ])
            N = np.array([ x_mn_inXPanel,  y_mn_inYPanel,  z_n_inXPanel ])

            # 更新散点位置
            self.M_point._offsets3d = ([M[0]], [M[1]], [M[2]])
            self.N_point._offsets3d = ([N[0]], [N[1]], [N[2]])

            # 更新连接线
            self.top_line.set_data_3d([top_pos[0], M[0]], 
                                    [top_pos[1], M[1]], 
                                    [top_pos[2], M[2]])
            
            self.end_line.set_data_3d([end_pos[0], N[0]], 
                                    [end_pos[1], N[1]], 
                                    [end_pos[2], N[2]])
            
            self.vertical_line.set_data_3d([M[0], N[0]], 
                                        [M[1], N[1]], 
                                        [M[2], N[2]])

            
            # 更新射线显示（在更新其他图形元素之后）
            ray_length = 1  # 射线长度


            self.top_ray.set_data_3d(
                [top_pos[0], top_pos[0] + ray_length * top_dir_norm[0]], 
                [top_pos[1], top_pos[1] + ray_length * top_dir_norm[1]], 
                [top_pos[2], top_pos[2] + ray_length * top_dir_norm[2]]
            )

            self.end_ray.set_data_3d(
                [end_pos[0], end_pos[0] + ray_length * end_dir_norm[0]], 
                [end_pos[1], end_pos[1] + ray_length * end_dir_norm[1]], 
                [end_pos[2], end_pos[2] + ray_length * end_dir_norm[2]]
            )


            # ===== 新增：更新角度可视化 =====
            # 角度弧半径
            arc_radius = 0.2
            
            # 绘制角度弧 - TOP X方向
            theta_top_x = np.linspace(0, alpha_inXPanel, 20)
            arc_x_top = np.array([[top_pos[0] + arc_radius * math.cos(t), top_pos[1], top_pos[2] - arc_radius * math.sin(t)] for t in theta_top_x])
            self.angle_top_x.set_data_3d(arc_x_top[:, 0], arc_x_top[:, 1], arc_x_top[:, 2])
            
            # 绘制角度弧 - TOP Y方向
            theta_top_y = np.linspace(0, alpha_inYPanel, 20)
            arc_y_top = np.array([[top_pos[0], top_pos[1] + arc_radius * math.cos(t), top_pos[2] - arc_radius * math.sin(t)] for t in theta_top_y])
            self.angle_top_y.set_data_3d(arc_y_top[:, 0], arc_y_top[:, 1], arc_y_top[:, 2])
            
            # 绘制角度弧 - END X方向
            theta_end_x = np.linspace(0, beta_inXPanel, 20)
            arc_x_end = np.array([[end_pos[0] + arc_radius * math.cos(t), end_pos[1], end_pos[2] - arc_radius * math.sin(t)] for t in theta_end_x])
            self.angle_end_x.set_data_3d(arc_x_end[:, 0], arc_x_end[:, 1], arc_x_end[:, 2])
            
            # 绘制角度弧 - END Y方向
            theta_end_y = np.linspace(0, beta_inYPanel, 20)
            arc_y_end = np.array([[end_pos[0], end_pos[1] + arc_radius * math.cos(t), end_pos[2] - arc_radius * math.sin(t)] for t in theta_end_y])
            self.angle_end_y.set_data_3d(arc_y_end[:, 0], arc_y_end[:, 1], arc_y_end[:, 2])
            
            # 更新角度标签
            self.angle_text_top_x.set_position([top_pos[0] + 0.05, top_pos[1], top_pos[2] - 0.3])
            self.angle_text_top_x.set_text(f"αx: {np.rad2deg(alpha_inXPanel):.1f}°")
            
            self.angle_text_top_y.set_position([top_pos[0], top_pos[1] + 0.05, top_pos[2] - 0.3])
            self.angle_text_top_y.set_text(f"αy: {np.rad2deg(alpha_inYPanel):.1f}°")
            
            self.angle_text_end_x.set_position([end_pos[0] + 0.05, end_pos[1], end_pos[2] - 0.3])
            self.angle_text_end_x.set_text(f"βx: {np.rad2deg(beta_inXPanel):.1f}°")
            
            self.angle_text_end_y.set_position([end_pos[0], end_pos[1] + 0.05, end_pos[2] - 0.3])
            self.angle_text_end_y.set_text(f"βy: {np.rad2deg(beta_inYPanel):.1f}°")
            
            # 更新画布
            self.canvas.draw_idle()
            
            
        except Exception as e:
            print(f"Error updating rays: {e}")