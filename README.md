## 项目结构概述

- `.devcontainer/`: devcontainer 配置文件。

- `imu/`: IMU 相关的主要逻辑。

- `client/`: 前端项目目录，使用 Vue 3 和 Ant Design。

- `server/`: 后端项目目录，使用 Flask。

- `install_bluetooth.sh`: 用于 devcontainer 中安装蓝牙依赖的脚本。

- `map.py`: 绘制空间地图。

- `ori_bluetooth.py`: 可以得到全部 **原始** 数据的脚本。（蓝牙通信）

- `ori.py`: 可以得到全部 **原始** 数据的脚本。

## 开发日志

### 9.13
完成了“识别是否在拧螺丝”和空间定位的集成
回滚之前的更改，现在无论传感器是否静止后都会实时定位最近的螺丝，因为拧螺丝时肯定会破坏静止状态

### 9.11
实现了最基础的“识别是否在拧螺丝”功能

### 9.10
实现了新定位方式下的拧螺丝逻辑，并且现在在传感器相对静止后才会定位最近的螺丝

尝试实现 feat: 识别是否在拧螺丝
需要更替掉原先的 simulate_screw_tightening，于是建新分支

发现空间 offsetZ 以及加速度 Z 得到的值不稳定，不可用
发现电动螺丝刀启动时会旋转，而手对其的里使其回正的过程中，angle Z 有 *突变后较平缓返回* 的特征
于是尝试根据欧拉角 angle Z 的变化特征确认当前是否正在拧螺丝

### 9.9
实现了根据 position xy 匹配最接近的螺丝
添加里 csv log 以分析数据

发现：离开始位置太近（小于 0.1），数据也没有可信度

对于非平面上（斜面）的螺丝，尝试用欧拉角的差别来为综合距离加权。但发现欧拉角会在 0 和 180 之间跳，要用四元数解决

### 9.6
蓝牙依赖项很多
sudo dnf install pkgconf-pkg-config cairo-devel gcc python3-devel gobject-introspection-devel

mac: 67:F8:1E:C8:D6:77

用 devcontainer 管理依赖

### 9.5
imu空间定位不现实，累计误差大：
https://blog.csdn.net/Yong_Qi2015/article/details/130002620
摄像头绑螺丝刀上

### 9.4
跑通
初版定位
