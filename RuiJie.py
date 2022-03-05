#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import sys
import time
import json

class RuiJie(object):
    def __init__(self, userId, password):
        self._test_time = 60
        self._status = False
        self._href = None
        self._userId = userId
        self._password = password

    def _check_status(self):
        test_url = "http://192.168.1.1/"
        page = requests.get(test_url)
        page.encoding = "utf8"
        soup = BeautifulSoup(page.text, "html5lib")
        meta = soup.select_one("head > meta")
        self._status = (meta is not None)
        if self._status:
            return
        time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("[Log] [%s]" % (time_string), end=" ")
        print("锐捷掉线，尝试重连", end=" ")
        script = soup.select_one("script")
        self._href = script.string.split("\'")[1]
        self._iplink = self._href.split("/eportal/")[0]

    def _reconnection(self):
        url = self._iplink + "/eportal/InterFace.do?method=login"
        data = {
            "userId": self._userId,
            "password": self._password,
            "service": "",
            "queryString": self._href.split("jsp?")[1],
            "operatorPwd": "",
            "validcode": ""
        }
        headers = {
            "Host": self._iplink[7:],
            "Origin": self._iplink,
            "Referer": self._href,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36"
        }
        page = requests.post(url, data=data, headers=headers)
        soup = BeautifulSoup(page.text, "html5lib")
        body = soup.select_one("body")
        result = json.loads(body.text)
        print(result["result"])

    def run(self):
        while(True):
            self._check_status()
            if self._status:
                time.sleep(self._test_time)
            else:
                self._reconnection()
                time.sleep(10)


if __name__ == "__main__":
    ruijie = RuiJie(sys.argv[1], sys.argv[2])
    while(True):
        try:
            ruijie.run()
        except Exception as e:
            time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print("[Exception] [%s]" % (time_string), end=" ")
            print(e)
