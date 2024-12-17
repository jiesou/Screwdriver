from PyQt5.QtWidgets import (QMainWindow, QWidget, QPushButton, 
                           QVBoxLayout, QHBoxLayout, QLabel)
from PyQt5.QtCore import Qt

from .views.dash import DashView

from .units.event_bus import event_bus

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
        
        # 操作菜单按钮
        self.operations_btn = QPushButton("操作")
        self.operations_btn.clicked.connect(self.show_operations_menu)
        
        # 位置信息显示
        self.position_label = QLabel("等待操作")
        self.position_label.setStyleSheet("color: green;")
        event_bus.state_updated.connect(
            lambda data: self.position_label.setText(
                f"X: {data['position'][0]*100:.1f} cm Y: {data['position'][1]*100:.1f} cm {'拧螺丝中' if data.get('is_screw_tightening') else '未拧螺丝'}"
            ) if data.get('position') else None
        )
        
        # 添加到工具栏
        toolbar_layout.addWidget(self.operations_btn)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.position_label)

        # 添加工具栏到主布局
        main_layout.addWidget(toolbar)

        # 添加仪表盘视图
        self.dash_view = DashView()
        main_layout.addWidget(self.dash_view)
        
        print("======PyQt inited======")


    def show_operations_menu(self):
        # TODO: 实现操作菜单
        pass