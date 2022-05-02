#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import time

import requests

HUST_DNS = "202.114.0.242"
OTHER_DNS = "223.5.5.5"

class HustNetwork(object):
    def __init__(self, config_file):
        self._test_time = 60
        with open(config_file, 'r') as f:
            self._userId = f.readline().strip()
            self._password = f.readline().strip()

    def _ping(self, host):
        # 利用 ping 判断网络状态
        cmd = "ping {} 2 {} > {}ping.log".format(
            "-n" if sys.platform.lower() == "win32" else "-c",
            host,
            "./" if sys.platform.lower() == "win32" else "/tmp/"
        )
        return False if os.system(cmd) else True

    def _check_status(self):
        # 依次 ping 校园网 DNS 和 阿里云 DNS
        return self._ping(HUST_DNS) or self._ping(OTHER_DNS)

    def _reconnection(self):
        time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("[Log] [%s]" % (time_string), end=" ")
        print("锐捷掉线，尝试重连", end=" ")

        # 通过 http 的网站进行跳转
        test_url = "http://192.168.1.1"
        response = requests.get(test_url)
        response.encoding = 'utf8'

        # 获取跳转链接
        href = re.findall(r"href='(.+)'", response.text)
        referer = href[0]
        origin = referer.split("/eportal/")[0]
        url = origin + "/eportal/InterFace.do?method=login"

        # 组成 post 数据
        data = {
            "userId": self._userId,
            "password": self._password,
            "service": "",
            "queryString": referer.split("jsp?")[1],
            "operatorPwd": "",
            "operatorUserId": "",
            "validcode": ""
        }

        # 校园网认证
        headers = {
            "Host": origin.split("://")[1],
            "Origin": origin,
            "Referer": referer,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
        }
        response = requests.post(url, data=data, headers=headers)

        # 打印响应状态
        response.encoding = response.apparent_encoding
        result = response.json()
        print(result["result"], result["message"])

    def run(self):
        while(True):
            if not self._check_status():
                self._reconnection()
            time.sleep(self._test_time)


if __name__ == "__main__":
    hustNetwork = HustNetwork(sys.argv[1])
    while(True):
        try:
            hustNetwork.run()
        except Exception as e:
            time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print("[Exception] [%s]" % (time_string), end=" ")
            print(e)
