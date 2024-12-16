from PyQt5.QtCore import QObject, pyqtSignal

class ReactiveState(QObject):
    """模拟Vue的reactive状态管理"""
    state_changed = pyqtSignal(str, object)  # 信号:属性名,新值

    def __init__(self):
        super().__init__()
        self._state = {}

    def __getattr__(self, name):
        return self._state.get(name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super().__setattr__(name, value)
            return
        self._state[name] = value
        self.state_changed.emit(name, value)