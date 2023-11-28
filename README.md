# HustNetwork

## 功能

有库依赖，自动认证华科校园网，并支持断线重连，还有适用于 Window 的 GUI 版本

## 使用

无需在路由器上，任何（通过通过路由器的）接入校园网的设备均可运行

```bash
python3 HustNetwork.py hust-network.conf
python3 HustNetwork_GUI.py
HustNetwork_GUI.exe
```

其中 hust-network.conf 中内容依次为校园网账号和密码

程序需保持一直运行，推荐使用 screen 或者 systemctl 配置成 service 挂在后台

## 其他相关项目推荐

- Rust 二进制文件：https://github.com/black-binary/hust-network-login
- Shell 版本：https://github.com/jyi2ya/hust-network-login-sh
