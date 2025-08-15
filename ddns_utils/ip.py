from typing import Literal
import requests
import re
import os
import logging

logger = logging.getLogger(__name__)

IP_STORED_FILE: dict[Literal[4, 6], os.PathLike | str] = {
    4: "ipv4.txt",
    6: "ipv6.txt"
}

for file_path in IP_STORED_FILE.values():
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("")


def check_version(ip: str) -> Literal[4, 6]:
    if re.match(r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$", ip):
        return 4
    elif re.match(r"^[0-9a-f]{0,4}(:[0-9a-f]{0,4}){1,7}$", ip):
        return 6
    else:
        raise ValueError("Invalid IP address.")


def get_ip(version: Literal[4, 6] = 4) -> str:
    """ 获取公网 IP（通过调用公网 API）
    :param version: IP 版本（4 / 6）
    :return: IP 地址
    :exception ValueError: 无效的版本
    :exception RuntimeError: 无法获取 IPv6（可能不支持）
    """
    if version == 4:
        url = "https://api.ipify.org/"
    elif version == 6:
        url = "https://api64.ipify.org/"
    else:
        raise ValueError("Invalid version. Please use 4 or 6.")
    ip = requests.get(url, proxies={"http": "", "https": ""}).text
    if version == 6 and check_version(ip) == 4:
        raise RuntimeError("No IPv6.")
    return ip


def get_ip_if_changed(version: Literal[4, 6] = 4, save: bool = True) -> str | None:
    ip = get_ip(version)
    logger.info(f"Current IP: {ip}")
    with open(IP_STORED_FILE[version], "r") as f:
        if ip == f.read():
            logger.info(f"Same as stored, Returned None.")
            return None
    if save:
        with open(IP_STORED_FILE[version], "w") as f:
            f.write(ip)
    return ip


def save_ip(ip: str):
    version = check_version(ip)
    with open(IP_STORED_FILE[version], "w") as f:
        f.write(ip)


def delete_saved_ip(version: Literal[4, 6] = 4):
    with open(IP_STORED_FILE[version], "w") as f:
        f.write("")