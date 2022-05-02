#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import sys
import time

import requests


class RuiJie(object):
    def __init__(self, userId, password):
        self._test_time = 60
        self._userId = userId
        self._password = password

    def _ping(self, host):
        cmd = "ping {} 2 {} > ping.log".format(
            "-n" if sys.platform.lower() == "win32" else "-c",
            host
        )
        return False if os.system(cmd) else True

    def _check_status(self):
        return self._ping("202.114.0.242") or self._ping("223.5.5.5")

    def _reconnection(self):
        time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("[Log] [%s]" % (time_string), end=" ")
        print("锐捷掉线，尝试重连", end=" ")

        test_url = "http://192.168.1.1"
        response = requests.get(test_url)
        response.encoding = 'utf8'

        href = re.findall(r"href='(.+)'", response.text)
        referer = href[0]
        origin = referer.split("/eportal/")[0]
        url = origin + "/eportal/InterFace.do?method=login"

        data = {
            "userId": self._userId,
            "password": self._password,
            "service": "",
            "queryString": referer.split("jsp?")[1],
            "operatorPwd": "",
            "operatorUserId": "",
            "validcode": ""
        }

        headers = {
            "Host": origin.split("://")[1],
            "Origin": origin,
            "Referer": referer,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
        }
        response = requests.post(url, data=data, headers=headers)
        response.encoding = response.apparent_encoding
        result = response.json()
        print(result["result"], result["message"])

    def run(self):
        while(True):
            time.sleep(self._test_time)
            if not self._check_status():
                self._reconnection()


if __name__ == "__main__":
    ruijie = RuiJie(sys.argv[1], sys.argv[2])
    while(True):
        try:
            ruijie.run()
        except Exception as e:
            time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print("[Exception] [%s]" % (time_string), end=" ")
            print(e)
