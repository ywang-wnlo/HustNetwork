#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import os
import sys
import time
import json

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
        test_url = "http://192.168.1.1"
        page = requests.get(test_url)
        soup = BeautifulSoup(page.text, "html5lib")
        time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("[Log] [%s]" % (time_string), end=" ")
        print("锐捷掉线，尝试重连", end=" ")
        script = soup.select_one("script")
        self._referer = script.string.split("\'")[1]
        self._origin = self._referer.split("/eportal/")[0]
        url = self._origin + "/eportal/InterFace.do?method=login"
        data = {
            "userId": self._userId,
            "password": self._password,
            "service": "",
            "queryString": self._referer.split("jsp?")[1],
            "operatorPwd": "",
            "operatorUserId": "",
            "validcode": ""
        }
        headers = {
            "Host": self._origin.split("://")[1],
            "Origin": self._origin,
            "Referer": self._referer,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
        }
        page = requests.post(url, data=data, headers=headers)
        page.encoding = page.apparent_encoding
        soup = BeautifulSoup(page.text, "html5lib")
        body = soup.select_one("body")
        result = json.loads(body.text)
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
