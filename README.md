# HustNetwork

## 功能

无库依赖，自动认证华科校园网，并支持断线重连

## 使用

无需在路由器上，任何（通过通过路由器的）接入校园网的设备均可运行

```bash
python3 HustNetwork.py {校园网账号} {校园网密码}
```

程序需保持一直运行，推荐使用 screen 或者 systemctl 配置成 service 挂在后台
