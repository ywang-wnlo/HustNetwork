#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import time
import math
import subprocess

import requests

HUST_DNS = "202.114.0.242"
OTHER_DNS = "223.5.5.5"


class HustNetwork(object):
    def __init__(self, config_file):
        self._test_time = 60
        with open(config_file, 'r') as f:
            self._userId = f.readline().strip()
            self._password = f.readline().strip()
        self._auth_url = None
        self._referer = None
        self._origin = None
        # 认证过程中不要走系统代理
        self._proxies = {
            'http': None,
            'https': None,
        }
        self._encrypted_password = None

    def _ping(self, host):
        # 利用 ping 判断网络状态
        if sys.platform.lower() == "win32":
            cmd = f"ping -n 2 -w 1000 {host}"
            creation_flags = subprocess.CREATE_NO_WINDOW
        else:
            cmd = f"ping -c 2 -W 1 {host}"
            creation_flags = 0
        args = cmd.split(' ')
        th = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=creation_flags)
        return (th.wait() == 0)

    def _check_status(self):
        # 依次 ping 校园网 DNS 和 阿里云 DNS
        return self._ping(HUST_DNS) or self._ping(OTHER_DNS)

    def _get_auth_url(self):
        # 通过 http 的网站进行跳转
        test_url = "http://1.1.1.1"
        response = requests.get(test_url, proxies=self._proxies)
        response.encoding = 'utf8'

        # 获取跳转链接
        href = re.findall(r"href='(.+)'", response.text)
        self._referer = href[0]
        self._origin = self._referer.split("/eportal/")[0]
        self._auth_url = self._origin + "/eportal/InterFace.do?method=login"

    def _password_encrypt(self):
        page_info_url = self._origin + "/eportal/InterFace.do?method=pageInfo"
        data = {
            "queryString": self._referer
        }
        response = requests.post(
            page_info_url, data=data, proxies=self._proxies)
        response.encoding = 'utf8'
        result = response.json()

        self._publicKey_exponent = result["publicKeyExponent"]
        self._publicKey_modulus = result["publicKeyModulus"]
        return result["passwordEncrypt"]

    # 加密的模拟来源于
    # 1. https://blog.csdn.net/Kreeda/article/details/117965385
    # 2. https://www.cnblogs.com/himax/p/python_rsa_no_padding.html
    def _get_encrypted_password(self):
        if self._encrypted_password is None:
            # 加上通用的 mac string
            self._encrypted_password = self._password + ">111111111"
            e = int(self._publicKey_exponent, 16)
            m = int(self._publicKey_modulus, 16)
            # 16进制转10进制
            t = self._encrypted_password.encode('utf-8')
            # 字符串逆向并转换为bytes
            input_nr = int.from_bytes(t, byteorder='big')
            # 将字节转化成int型数字，如果没有标明进制，看做ascii码值
            crypt_nr = pow(input_nr, e, m)
            # 计算x的y次方，如果z在存在，则再对结果进行取模，其结果等效于pow(x,y) %z
            length = math.ceil(m.bit_length() / 8)
            # 取模数的比特长度(二进制长度)，除以8将比特转为字节
            crypt_data = crypt_nr.to_bytes(length, byteorder='big')
            # 将密文转换为bytes存储(8字节)，返回hex(16字节)
            self._encrypted_password = crypt_data.hex()
        return self._encrypted_password

    def _reconnection(self):
        time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print("[Log] [%s]" % (time_string), end=" ")
        print("锐捷掉线，尝试重连", end=" ")

        if self._auth_url is None:
            self._get_auth_url()

        # 组成 post 数据
        data = {
            "userId": self._userId,
            "password": self._password,
            "service": "",
            "queryString": self._referer.split("jsp?")[1],
            "operatorPwd": "",
            "operatorUserId": "",
            "validcode": "",
            "passwordEncrypt": ""
        }
        if self._password_encrypt():
            data["password"] = self._get_encrypted_password()
            data["passwordEncrypt"] = "true"

        # 校园网认证
        headers = {
            "Host": self._origin.split("://")[1],
            "Origin": self._origin,
            "Referer": self._referer,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"
        }
        response = requests.post(
            self._auth_url, data=data, headers=headers, proxies=self._proxies)

        # 打印响应状态
        response.encoding = response.apparent_encoding
        result = response.json()
        print(result["result"], result["message"])

    def run(self):
        while (True):
            if not self._check_status():
                self._reconnection()
            time.sleep(self._test_time)


if __name__ == "__main__":
    hustNetwork = HustNetwork(sys.argv[1])
    while (True):
        try:
            hustNetwork.run()
        except Exception as e:
            time_string = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print("[Exception] [%s]" % (time_string), end=" ")
            print(e)
