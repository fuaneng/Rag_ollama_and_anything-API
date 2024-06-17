#     -*- coding:utf-8 -*-
# @Time         : 2024-06-13 14:29:07
# @Author       : Rowan
# @Illustration :

import curl_cffi.requests as cffi_requests
import json


def main():
    session = cffi_requests.Session(timeout=15, impersonate="chrome107")
    api = "http://192.168.1.54:5000/api/get_details"
    with open("./data.json", "r", encoding="utf-8") as file:
        data = json.load(file)
    print(type(data))
    data = {"product": "SN54ACT16244", "item": data}
    response = session.post(api, data=data)
    print(response.status_code)
    print(response.text)


if __name__ == '__main__':
    main()
