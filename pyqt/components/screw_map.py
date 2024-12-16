from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPointF

class ScrewMap(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.screws = []
        self.current_position = None
        self.scale = 400  # 像素/米
        
    def update_map(self, screws, position):
        self.screws = screws
        self.current_position = position
        self.update()  # 触发重绘
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制背景
        painter.fillRect(self.rect(), QColor(240, 240, 240))
        
        # 移动原点到中心
        painter.translate(self.width() / 2, self.height() / 2)
        
        # 绘制网格和坐标轴
        self._draw_grid(painter)
        
        # 绘制螺丝位置
        for screw in self.screws:
            x = screw['position']['x'] * self.scale
            y = -screw['position']['y'] * self.scale  # 注意Y轴方向
            
            # 根据状态设置颜色
            if screw.get('status') == '已完成':
                color = QColor(0, 255, 0)  # 绿色
            elif screw.get('status') == '已定位':
                color = QColor(255, 165, 0)  # 橙色
            else:
                color = QColor(200, 200, 200)  # 灰色
                
            painter.setPen(QPen(color, 2))
            painter.drawEllipse(QPointF(x, y), 5, 5)
            
        # 绘制当前位置
        if self.current_position:
            x, y = self.current_position
            painter.setPen(QPen(Qt.red, 3))
            painter.drawEllipse(QPointF(x * self.scale, -y * self.scale), 8, 8)

    def _draw_grid(self, painter):
        # 绘制坐标轴
        painter.setPen(QPen(Qt.black, 1))
        # painter.drawLine(-self.width()/2, 0, self.width()/2, 0)  # X轴
        # painter.drawLine(0, -self.height()/2, 0, self.height()/2)  # Y轴