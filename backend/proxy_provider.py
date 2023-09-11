import requests
import re
from string import digits


class ProxyProvider:

    PROXY_LIST_FILE_URL: str = (
        "https://raw.githubusercontent.com/clarketm/"
        "proxy-list/master/proxy-list.txt"
    )
    PROXY_LINE_PATTERN: re.Pattern = re.compile(
        r"^(?P<ip>[0-9]{1,3}(\.[0-9]{1,3}){1,3}):"
        r"(?P<port>[0-9]{1,5}) .{2}-(?P<flags>.*)$"
    )

    PROXY_STATUS_FILE_URL: str = (
        "https://raw.githubusercontent.com/clarketm/"
        "proxy-list/master/proxy-list-status.txt"
    )
    PROXY_STATUS_LINE_PATTERN: re.Pattern = re.compile(
        r"^(?P<ip>[0-9]{1,3}(\.[0-9]{1,3}){1,3}):"
        r"(?P<port>[0-9]{1,5}) => (?P<status>.*)$"
    )

    _proxies: list[dict[str, str]] = []

    @classmethod
    def _fetch_proxies(cls):
        response = requests.get(cls.PROXY_LIST_FILE_URL)
        lines = response.text.split("\n")
        all_proxies = []
        for line in lines:
            if len(line) == 0:
                continue
            if line[0] not in digits:
                continue
            match = cls.PROXY_LINE_PATTERN.match(line)
            if match is None:
                continue
            ip = match.group('ip')
            port = match.group('port')
            flags = match.group('flags')
            ip_hiding = "!" in flags
            if ip_hiding:
                all_proxies.append({
                    "ip": ip,
                    "port": port
                })

        response = requests.get(cls.PROXY_STATUS_FILE_URL)
        lines = response.text.split("\n")
        online_proxies = {}
        for line in lines:
            if len(line) == 0:
                continue
            if line[0] not in digits:
                continue
            match = cls.PROXY_STATUS_LINE_PATTERN.match(line)
            if match is None:
                continue
            ip = match.group('ip')
            port = match.group('port')
            status = match.group('status')
            if status == "success":
                online_proxies[ip] = port

        for proxy in all_proxies:
            if proxy['ip'] in online_proxies:
                cls._proxies.append({
                    'http': f"http://{proxy['ip']}:{proxy['port']}",
                    'https': f"https://{proxy['ip']}:{proxy['port']}"
                })

    @classmethod
    def get_proxy(cls, index: int) -> dict[str, str]:
        return cls._proxies[index % len(cls._proxies)]


ProxyProvider._fetch_proxies()
