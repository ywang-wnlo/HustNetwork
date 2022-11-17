#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import requests
from PySide6 import QtCore, QtWidgets


class HustNetwork(QtCore.QThread):
    status_signal = QtCore.Signal(str)
    
    def __init__(self, username='', password='', ping_interval=15, ping_dns1='202.114.0.242', ping_dns2='223.5.5.5', config_file=None):
        super().__init__()
        if config_file is None:
            self._username = username
            self._password = password
            self._ping_interval = ping_interval
            self._ping_dns1 = ping_dns1
            self._ping_dns2 = ping_dns2
        else:
            with open(config_file, 'r') as f:
                self._username = f.readline().strip()
                self._password = f.readline().strip()
                self._ping_interval = int(f.readline().strip())
                self._ping_dns1 = f.readline().strip()
                self._ping_dns2 = f.readline().strip()
        self._auth_url = None
        self._referer = None
        self._origin = None

    def _ping(self, host):
        # 利用 ping 判断网络状态
        if sys.platform.lower() == "win32":
            cmd = f"ping -n 2 -w 1000 {host} > .ping-log"
        else:
            cmd = f"ping -c 2 -W 1 {host} > /tmp/ping-log"
        return False if os.system(cmd) else True

    def _check_status(self):
        # 默认情况依次 ping 校园网 DNS 和 阿里云 DNS
        return self._ping(self._ping_dns1) or self._ping(self._ping_dns2)

    def _get_auth_url(self):
        # 通过 http 的网站进行跳转
        test_url = "http://192.168.1.1"
        response = requests.get(test_url)
        response.encoding = 'utf8'

        # 获取跳转链接
        href = re.findall(r"href='(.+)'", response.text)
        self._referer = href[0]
        self._origin = self._referer.split("/eportal/")[0]
        self._auth_url = self._origin + "/eportal/InterFace.do?method=login"

    def _reconnection(self):
        if self._auth_url is None:
            self._get_auth_url()

        # 组成 post 数据
        data = {
            "userId": self._username,
            "password": self._password,
            "service": "",
            "queryString": self._referer.split("jsp?")[1],
            "operatorPwd": "",
            "operatorUserId": "",
            "validcode": ""
        }

        # 校园网认证
        headers = {
            "Host": self._origin.split("://")[1],
            "Origin": self._origin,
            "Referer": self._referer,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
        }
        response = requests.post(self._auth_url, data=data, headers=headers)

        # 打印响应状态
        response.encoding = response.apparent_encoding
        result = response.json()
        if result["result"] == 'success':
            self.status_signal.emit("认证成功！")
        else:
            self.status_signal.emit(result["message"])

    def run(self):
        while (True):
            if not self._check_status():
                self._reconnection()
            else:
                self.status_signal.emit("已认证！")
            time.sleep(self._ping_interval)

class HustNetworkGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.hustNetwork = None

        self.setWindowTitle("华科校园网认证")
        self.setWindowFlags(QtCore.Qt.WindowType.WindowMinimizeButtonHint |
                            QtCore.Qt.WindowType.WindowCloseButtonHint)

        self.layout = QtWidgets.QFormLayout(self)

        self.username = QtWidgets.QLineEdit()
        self.layout.addRow("校园网账号", self.username)

        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.layout.addRow("校园网密码", self.password)

        self.ping_interval = QtWidgets.QLineEdit("15")
        self.layout.addRow("断线重连间隔(s)", self.ping_interval)

        self.ping_dns1 = QtWidgets.QLineEdit("202.114.0.242")
        self.layout.addRow("ping 主机1", self.ping_dns1)
        self.ping_dns2 = QtWidgets.QLineEdit("223.5.5.5")
        self.layout.addRow("ping 主机2", self.ping_dns2)

        self.status = QtWidgets.QLabel("未运行")
        self.layout.addRow("当前状态", self.status)

        self.save_config = QtWidgets.QCheckBox("保存配置")
        self.save_config.setChecked(True)
        self.button = QtWidgets.QPushButton("开启服务")
        self.layout.addRow(self.save_config, self.button)

        self.button.clicked.connect(self.daemon_toggle)

        try:
            with open('.config', 'r') as f:
                self.username.setText(f.readline().strip())
                self.password.setText(f.readline().strip())
                self.ping_interval.setText(f.readline().strip())
                self.ping_dns1.setText(f.readline().strip())
                self.ping_dns2.setText(f.readline().strip())
        except Exception:
            pass
        
    @QtCore.Slot()
    def set_status(self, string: str):
        self.status.setText(string)

    def save_to_confg_file(self):
        if self.save_config.isChecked():
            with open('.config', 'w') as f:
                f.write(self.username.text() + '\n')
                f.write(self.password.text() + '\n')
                f.write(self.ping_interval.text() + '\n')
                f.write(self.ping_dns1.text() + '\n')
                f.write(self.ping_dns2.text() + '\n')

    def start_auth_daemon(self):
        if self.save_config.isChecked():
            self.hustNetwork = HustNetwork(config_file='.config')
        else:
            self.hustNetwork = HustNetwork(
                self.username.text(), self.password.text(), self.ping_interval.text(),
                self.ping_dns1.text(), self.ping_dns2.text())
        self.hustNetwork.status_signal.connect(self.set_status)
        self.hustNetwork.start()

    @QtCore.Slot()
    def daemon_toggle(self):
        if self.hustNetwork is None:
            self.save_to_confg_file()
            self.set_status("认证中...")
            self.start_auth_daemon()
            self.button.setText("停止服务")
        else:
            self.hustNetwork.terminate()
            self.hustNetwork.wait()
            del self.hustNetwork
            self.hustNetwork = None
            self.set_status("未运行")
            self.button.setText("开启服务")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = HustNetworkGUI()
    widget.resize(250, 200)
    widget.show()

    sys.exit(app.exec())
