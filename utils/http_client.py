"""最简单的 HTTP 请求工具。"""

import requests


def get(url: str, **kwargs):
    """发送 GET 请求并返回 requests.Response。"""
    return requests.get(url, timeout=10, **kwargs)


def post(url: str, **kwargs):
    """发送 POST 请求并返回 requests.Response。"""
    return requests.post(url, timeout=10, **kwargs)
