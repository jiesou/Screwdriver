---
applyTo: '**'
---

# 代码风格要求
- PyQt 6 中涉及“螺丝状态”“位置”“配置”等概念时，使用 state_bus 和信号槽机制。dash.py 可以将 update_state 的信号作为参数传递，如
```py
ScrewTable(state_update_on=state_bus.updated)
```
这样就可以写
```py
state_update_on.connect(self.update_state)
```
- 不要 Overengineering！不要 Overengineering！不要 Overengineering！保持代码实现最最最简短简单。如果可能，减少代码的更改。
- 注释用中文
