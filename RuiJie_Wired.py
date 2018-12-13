#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import subprocess

class RuiJie_Wired(object):
    def __init__(self, file_path):
        self._test_time = 5 * 60
        self._reconnection_time = 10
        self._status = False
        self._file_path = file_path

    def _check_status(self):
        exit_code = os.system('ping baidu.com')
        self._status = False if exit_code else True
        if self._status:
            return
        time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("[Log] [%s]" % (time_string), end=" ")
        print("锐捷掉线，尝试重连", end=" ")

    def _reconnection(self):
        subprocess.call(self._file_path)
    
    def run(self):
        while(True):
            self._check_status()
            if self._status:
                time.sleep(self._test_time)
            else:
                self._reconnection()
                time.sleep(self._reconnection_time)


if __name__ == "__main__":
    ruijie = RuiJie_Wired(sys.argv[1])
    while(True):
        try:
            ruijie.run()
        except Exception as e:
            time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print("[Exception] [%s]" % (time_string), end=" ")
            print(e)
            