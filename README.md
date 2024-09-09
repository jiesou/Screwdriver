## 项目结构概述

- `.devcontainer/`: devcontainer 配置文件。

- `imu/`: IMU 相关的主要逻辑。

- `client/`: 前端项目目录，使用 Vue 3 和 Vite。

- `server/`: 后端项目目录，使用 Flask。

- `install_bluetooth.sh`: 用于 devcontainer 中安装蓝牙依赖的脚本。

- `map.py`: 可以绘制空间地图。

- `ori_bluetooth.py`: 可以得到全部 **原始** 数据的脚本。（蓝牙通信）

- `ori.py`: 可以得到全部 **原始** 数据的脚本。

## 开发日志

### 9.9
根据 position xy 匹配最接近的螺丝
加 csv log

发现：离开始位置太近（小于 0.1）也没有可信度

欧拉角会在 0 和 180 之间跳，要用四元数解决

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
