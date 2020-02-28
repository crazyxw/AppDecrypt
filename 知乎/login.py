# -*- coding: utf-8 -*-
"""
模拟登录 知乎app
版本: v5.6.1
"""
import hmac
import urllib3
import requests
import base64
import hashlib
import time
from urllib.parse import quote
import random
urllib3.disable_warnings()


class ZhiHuLogin(object):
    def __init__(self, account: str, password: str):
        self.sess = self.__init_session()
        self.account = account,
        self.password = password
        self.mac = self.generate_mac()
        self.imei = self.generate_imei()
        self.os = self.generate_os()
        self.sn = self.generate_sn()
        self.udid = None
        self.release = self.generate_release()
        self.brand, self.model = self.generate_brand_and_model()
        self.network = self.generate_network()
        self.app_id = "1355"
        self.app_build = "571"
        self.app_version = "5.6.1"
        self.api_version = "3.0.75"
        self.package_name = "com.zhihu.android"

    @staticmethod
    def __init_session():
        sess = requests.Session()
        sess.verify = False
        return sess

    @staticmethod
    def generate_mac():
        """
        生成mac 地址
        :return:
        """
        return "00:81:fc:7d:b8:e8"

    @staticmethod
    def generate_sn():
        return "".join([str(random.randint(1, 9)) for _ in range(8)])

    @staticmethod
    def generate_network():
        networks = ["WIFI", "4G", "3G"]
        return random.choice(networks)

    @staticmethod
    def generate_imei():
        return "86" + "".join([str(random.randint(1, 10)) for _ in range(13)])

    @staticmethod
    def generate_os():
        return "Android"

    @staticmethod
    def generate_release():
        releases = ["7.0", "8.0", "9.0"]
        return random.choice(releases)

    @staticmethod
    def generate_brand_and_model():
        brands = (
                ("xiaomi", ("MI 5s Plus", "MI 5s", "MI 6")),
                ("huawei", ("Mate 30", "Mate 30 Pro", "P30")),
                  )
        brand, models = random.choice(brands)
        model = random.choice(models)
        return brand.title(), model

    def get_udid(self):
        if not self.udid:
            url = "https://appcloud.zhihu.com/v1/device"
            data = {
                "app_build": self.app_build,
                "app_version": self.app_version,
                "bt_ck": "1",
                "bundle_id": self.package_name,
                "cp_ct": "4",
                "cp_fq": "2188800",
                "cp_tp": "AArch64 Processor rev 1 (aarch64)",
                "cp_us": str(random.randint(3, 8)),
                "d_n": "QCOM-BTD",
                "fr_mem": "0",
                "fr_st": "104222",
                "im_e": self.imei,
                "mc_ad": self.mac,
                "mcc": "",
                "nt_st": "1",
                "ph_br": self.brand,
                "ph_md": self.model,
                "ph_os": " ".join([self.os, self.release]),
                "ph_sn": self.sn,
                "pvd_nm": "",
                "tt_mem": "27",
                "tt_st": "115105",
                "tz_of": "28800",
            }
            headers = {
                "User-Agent": self.ua(),
                "x-app-id": self.app_id,  # 固定值
                "x-req-ts": self.ts(),  # 时间戳
                "x-sign-version": "2",  # 固定值 sign版本
                "host": "appcloud.zhihu.com",
            }
            _url_path = []
            for k, v in data.items():
                t = k
                if v:
                    t += "=" + quote(v.replace(" ", "+"), safe="+")
                _url_path.append(t)
            url_str = "&".join(_url_path)
            tmp = headers["x-app-id"] + headers["x-sign-version"] + url_str + headers["x-req-ts"]
            headers["x-req-signature"] = get_sign(tmp, "dd49a835-56e7-4a0f-95b5-efd51ea5397f")
            resp = self.sess.post(url, headers=headers, data=url_str.encode(), verify=False)
            self.udid = resp.json()["udid"]
        return self.udid

    def get_suger(self):
        t = f"IMEI={self.imei};ANDROID_ID=d92bee66bc70db02;MAC={self.mac}"
        return base64.b64encode(t.encode()).decode()

    def ua(self):
        return f"{self.package_name}/Futureve/{self.app_version} Mozilla/5.0 (Linux; Android {self.release}) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/52.0.2743.100 Mobile Safari/537.36 Google-HTTP-Java-Client/1.22.0 (gzip)"

    def app_za(self):
        return f"OS={self.os}&Release={self.release}&Model={self.model}&VersionName={self.app_version}&VersionCode={self.app_build}&Width=720&Height=1280&Installer=%E8%B1%8C%E8%B1%86%E8%8D%9A&WebView=52.0.2743.100DeviceType=AndroidPhoneBrand={self.brand}OperatorType=46000"

    @staticmethod
    def ts():
        return str(int(time.time()))

    def get_capsion_ticket(self):
        url = "https://api.zhihu.com/captcha"
        headers = {
            "user-agent": self.ua(),
            "x-api-version": self.api_version,
            "x-app-version": self.app_version,
            "x-app-za": self.app_za(),
            "x-app-flavor": "wandoujia",
            "x-app-build": "release",
            "x-network-type": "WiFi",
            "x-suger": self.get_suger(),
            "x-udid": self.get_udid(),
        }
        self.sess.get(url, headers=headers)

    def login(self):
        url = "https://api.zhihu.com/sign_in"

        data = {
            "client_id": "8d5227e0aaaa4797a763ac64e0c3b8",  # 固定值
            "grant_type": "password",
            "password": self.password,
            "source": "com.zhihu.android",
            "timestamp": self.ts(),
            "username": "+86%s" % self.account
        }
        tmp = data["grant_type"] + data["client_id"] + data["source"] + data["timestamp"]
        data["signature"] = get_sign(tmp, "ecbefbf6b17e47ecb9035107866380")
        headers = {
            "user-agent": self.ua(),
            "x-api-version": self.api_version,
            "x-app-version": self.app_version,
            "x-app-za": self.app_za(),
            "x-app-flavor": "wandoujia",
            "x-app-build": "release",
            "x-network-type": "WiFi",
            "x-suger": self.get_suger(),
            "x-udid": self.get_udid(),
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        resp = self.sess.post(url, headers=headers, data=data)
        print(resp.text)

    def run(self):
        self.get_capsion_ticket()
        self.login()


def get_sign(text, pk):
    return hmac.new(pk.encode(), text.encode(), hashlib.sha1).hexdigest()


if __name__ == '__main__':
    acc = ""
    pw = ""
    lg = ZhiHuLogin(acc, pw)
    lg.run()

