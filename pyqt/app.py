from PyQt5.QtWidgets import (QMainWindow, QWidget, QPushButton, 
                           QVBoxLayout, QHBoxLayout, QLabel)
from PyQt5.QtCore import Qt
from .units.event_bus import event_bus
from .views.dash import DashView

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("螺丝管理系统")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建主容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # 顶部工具栏
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar.setStyleSheet("background-color: aliceblue;")
        
        # 连接状态指示
        self.status_label = QLabel("服务连接状态: 正在连接...")
        self.status_label.setStyleSheet("color: red;")
        event_bus.server_connected_changed.connect(self.update_connection_status)
        
        # 连接控制按钮
        self.connect_btn = QPushButton("连接")
        self.connect_btn.clicked.connect(self.toggle_connection)
        
        # 操作菜单按钮
        self.operations_btn = QPushButton("操作")
        self.operations_btn.clicked.connect(self.show_operations_menu)
        
        # 位置信息显示
        self.position_label = QLabel("等待操作")
        self.position_label.setStyleSheet("color: green;")
        event_bus.moving_streamer.data_received.connect(self.update_position_info)
        
        # 添加到工具栏
        toolbar_layout.addWidget(self.status_label)
        toolbar_layout.addWidget(self.connect_btn)
        toolbar_layout.addWidget(self.operations_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.position_label)
        
        # 添加工具栏到主布局
        main_layout.addWidget(toolbar)
        
        # 添加仪表盘视图
        self.dash_view = DashView()
        main_layout.addWidget(self.dash_view)

    def update_connection_status(self, connected):
        if connected:
            self.status_label.setText("服务连接状态: 已连接")
            self.status_label.setStyleSheet("color: green;")
            self.connect_btn.setText("中断连接")
        else:
            self.status_label.setText("服务连接状态: 正在连接...")
            self.status_label.setStyleSheet("color: red;")
            self.connect_btn.setText("连接")

    def update_position_info(self, data):
        if data.get('position'):
            x, y = data['position']
            status = "拧螺丝中" if data.get('is_screw_tightening') else "未拧螺丝"
            self.position_label.setText(
                f"X: {x*100:.1f} cm Y: {y*100:.1f} cm {status}"
            )

    def toggle_connection(self):
        if event_bus.moving_streamer.event_state.is_doing:
            event_bus.moving_streamer.stop()
        else:
            event_bus.moving_streamer.start()

    def show_operations_menu(self):
        # TODO: 实现操作菜单
        pass