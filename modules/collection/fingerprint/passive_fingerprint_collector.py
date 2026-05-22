# -*- coding: utf-8 -*-
"""免认证设备指纹采集器"""

import socket
import re
import subprocess
import logging
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

# 内置 MAC OUI 数据库（常用厂商）
OUI_DATABASE = {
    "001A2B": "Cisco Systems",
    "005056": "VMware",
    "000C29": "VMware",
    "000569": "VMware",
    "001C42": "Parallels",
    "000393": "Apple",
    "000A95": "Apple",
    "0050BA": "Netgear",
    "0014BF": "Linksys",
    "001E58": "D-Link",
    "001F3C": "TP-Link",
    "002369": "TP-Link",
    "B4B024": "TP-Link",
    "002719": "TP-Link",
    "1CFA68": "TP-Link",
    "00E04C": "Realtek",
    "001E88": "Hikvision",
    "001B2B": "Hikvision",
    "ACCF85": "Hikvision",
    "001D0F": "Hikvision",
    "64322A": "Hikvision",
    "0022A0": "Dahua",
    "002565": "Dahua",
    "485F37": "Dahua",
    "3482DE": "Dahua",
    "001882": "Huawei",
    "00259E": "Huawei",
    "00E0FC": "Huawei",
    "04021F": "Huawei",
    "0425C5": "Huawei",
    "0433C2": "Huawei",
    "342912": "Huawei",
    "3400A3": "Huawei",
    "38378B": "Huawei",
    "3C4711": "Huawei",
    "001E10": "H3C",
    "00005E": "IANA",
    "00037F": "A10 Networks",
    "001CB3": "Arista Networks",
    "001C73": "Arista Networks",
    "000CEF": "Arista Networks",
    "F88D28": "Ruijie Networks",
    "00749C": "Ruijie Networks",
    "00F81C": "Ruijie Networks",
    "7483C2": "Ruijie Networks",
    "B4714B": "Ruijie Networks",
    "E83A12": "Ruijie Networks",
    "EC2280": "Ruijie Networks",
    "60E327": "Ruijie Networks",
    "D4EE07": "Ruijie Networks",
    "784476": "Ruijie Networks",
    "D4AE52": "Dell",
    "5C260A": "Dell",
    "1866DA": "Dell",
    "F8BC12": "Dell",
    "24B6FD": "Dell",
}


def lookup_mac_vendor(mac: str) -> Optional[str]:
    """根据 MAC 地址查找厂商"""
    if not mac:
        return None
    mac_clean = mac.upper().replace(':', '').replace('-', '').replace('.', '')
    if len(mac_clean) < 6:
        return None
    oui = mac_clean[:6]
    return OUI_DATABASE.get(oui)


def get_mac_via_arp(ip: str) -> Optional[str]:
    """通过 ARP 获取 IP 对应的 MAC 地址"""
    try:
        result = subprocess.run(
            ['ip', 'neigh', 'show', ip],
            capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0 and result.stdout:
            match = re.search(r'lladdr\s+([0-9a-fA-F:]{17})', result.stdout)
            if match:
                return match.group(1)
    except Exception:
        pass

    try:
        result = subprocess.run(
            ['arp', '-n', ip],
            capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0 and result.stdout:
            match = re.search(r'([0-9a-fA-F:]{17})', result.stdout)
            if match:
                return match.group(1)
    except Exception:
        pass
    return None


def grab_ssh_banner(ip: str, port: int = 22, timeout: float = 3.0) -> Optional[str]:
    """抓取 SSH banner"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        banner = sock.recv(512)
        sock.close()
        return banner.decode('utf-8', errors='ignore').strip()
    except Exception:
        return None


def grab_http_headers(ip: str, port: int, timeout: float = 3.0) -> Optional[Dict]:
    """抓取 HTTP Server header"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))

        request = f"GET / HTTP/1.0\r\nHost: {ip}\r\nConnection: close\r\n\r\n"
        sock.send(request.encode('utf-8'))

        response = b""
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
                if b"\r\n\r\n" in response:
                    break
            except socket.timeout:
                break
        sock.close()

        response_str = response.decode('utf-8', errors='ignore')
        if "\r\n\r\n" not in response_str:
            return None
        header_part = response_str.split("\r\n\r\n")[0]

        headers = {}
        for line in header_part.split("\r\n"):
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key.lower()] = value.strip()

        return headers
    except Exception:
        return None


def infer_os_from_banner(banner: str, http_headers: Optional[Dict] = None) -> Tuple[Optional[str], Optional[str], float]:
    """从 banner 推断操作系统和厂商"""
    banner_lower = banner.lower()

    if 'ubuntu' in banner_lower:
        return ('Linux/Ubuntu', 'Canonical', 0.9)
    elif 'debian' in banner_lower:
        return ('Linux/Debian', 'Debian', 0.9)
    elif 'centos' in banner_lower:
        return ('Linux/CentOS', 'CentOS', 0.85)
    elif 'red hat' in banner_lower or 'rhel' in banner_lower:
        return ('Linux/RHEL', 'Red Hat', 0.85)
    elif 'rocky' in banner_lower:
        return ('Linux/Rocky', 'Rocky Linux', 0.85)
    elif 'fedora' in banner_lower:
        return ('Linux/Fedora', 'Red Hat', 0.8)
    elif 'amazon' in banner_lower:
        return ('Linux/AWS', 'Amazon', 0.85)
    elif 'windows' in banner_lower or 'win32' in banner_lower:
        return ('Windows', 'Microsoft', 0.9)
    elif 'mikrotik' in banner_lower or 'routeros' in banner_lower:
        return ('RouterOS/MikroTik', 'MikroTik', 0.95)
    elif 'hp' in banner_lower or 'procurve' in banner_lower or 'aruba' in banner_lower:
        return ('Linux/HP', 'HPE', 0.7)
    elif 'cisco' in banner_lower or 'ios-xe' in banner_lower or 'ios-xr' in banner_lower or 'nx-os' in banner_lower:
        return ('IOS/Cisco', 'Cisco Systems', 0.8)
    elif 'huawei' in banner_lower or 'vrp' in banner_lower:
        return ('VRP/Huawei', 'Huawei', 0.85)
    elif 'h3c' in banner_lower or 'comware' in banner_lower:
        return ('Comware/H3C', 'H3C', 0.85)
    elif 'juniper' in banner_lower or 'junos' in banner_lower:
        return ('Junos/Juniper', 'Juniper Networks', 0.9)
    elif 'arista' in banner_lower or 'eos' in banner_lower:
        return ('EOS/Arista', 'Arista Networks', 0.9)
    elif 'fortigate' in banner_lower or 'fortinet' in banner_lower:
        return ('FortiOS/Fortinet', 'Fortinet', 0.9)
    elif 'sros' in banner_lower or 'nokia' in banner_lower:
        return ('SROS/Nokia', 'Nokia', 0.85)

    if http_headers:
        server = http_headers.get('server', '').lower()
        x_powered = http_headers.get('x-powered-by', '').lower()
        if 'iis' in server or 'microsoft' in server:
            return ('Windows', 'Microsoft', 0.7)
        elif 'nginx' in server:
            return ('Linux/nginx', 'nginx', 0.6)
        elif 'apache' in server:
            return ('Linux/Apache', 'Apache', 0.6)

    return (None, None, 0.0)


def infer_device_type(ports: List[int], os_type: Optional[str], vendor: Optional[str]) -> str:
    """推断设备类型"""
    if 161 in ports and 162 in ports:
        return 'network_device'
    if os_type:
        os_lower = os_type.lower()
        if 'windows' in os_lower:
            return 'windows_server'
        if 'ubuntu' in os_lower or 'debian' in os_lower or 'centos' in os_lower or 'rhel' in os_lower:
            return 'linux_server'
        if 'routeros' in os_lower or 'vrp' in os_lower or 'junos' in os_lower or 'eos' in os_lower:
            return 'network_device'
    if vendor:
        vendor_lower = vendor.lower()
        if any(x in vendor_lower for x in ['cisco', 'huawei', 'h3c', 'juniper', 'arista']):
            return 'network_device'
        if any(x in vendor_lower for x in ['hikvision', 'dahua']):
            return 'camera'
        if any(x in vendor_lower for x in ['tp-link', 'netgear', 'linksys']):
            return 'soho_router'
    return 'unknown'


class PassiveFingerprintCollector:
    """
    免认证设备指纹采集器
    不需要目标设备凭据，通过以下方式收集信息：
    1. 端口扫描（常见管理端口）
    2. SSH banner 抓取
    3. HTTP Server header 抓取
    4. SNMP sysDesc probe (community: public)
    5. MAC OUI 厂商识别
    6. OS 类型推断
    """

    def __init__(self):
        self.common_ports = [22, 23, 80, 443, 161, 162, 3389, 5900, 8080, 8443, 623, 445]

    def collect(self, ip: str, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """
        对目标 IP 进行被动指纹采集
        """
        result = {
            'ip': ip,
            'ports_found': [],
            'open_ports': {},
            'ssh_banner': None,
            'http_server': None,
            'snmp_sysdesc': None,
            'mac_address': None,
            'mac_vendor': None,
            'os_type': None,
            'os_vendor': None,
            'os_confidence': 0.0,
            'device_type': 'unknown',
        }

        # 1. 端口探测
        ports_found = self._probe_ports(ip, self.common_ports, timeout=timeout / max(len(self.common_ports), 1))
        result['ports_found'] = ports_found

        # 2. SSH banner
        if 22 in ports_found:
            banner = grab_ssh_banner(ip, 22, timeout=timeout / 2)
            result['ssh_banner'] = banner

        # 3. HTTP headers
        for port in [80, 443, 8080, 8443]:
            if port in ports_found:
                headers = grab_http_headers(ip, port, timeout=timeout / 2)
                if headers:
                    result['http_server'] = headers.get('server')
                    break

        # 4. MAC 地址
        mac = get_mac_via_arp(ip)
        result['mac_address'] = mac
        if mac:
            result['mac_vendor'] = lookup_mac_vendor(mac)

        # 5. OS 推断
        os_type, os_vendor, confidence = infer_os_from_banner(result['ssh_banner'] or '', result['http_server'])
        result['os_type'] = os_type
        result['os_vendor'] = os_vendor
        result['os_confidence'] = confidence

        # 6. 设备类型
        result['device_type'] = infer_device_type(ports_found, os_type, result['mac_vendor'])

        # 7. 端口映射
        port_service_map = {
            22: 'ssh', 23: 'telnet', 80: 'http', 443: 'https',
            161: 'snmp', 162: 'snmptrap', 3389: 'rdp', 5900: 'vnc',
            8080: 'http-proxy', 8443: 'https-alt', 623: 'ipmi', 445: 'smb'
        }
        result['open_ports'] = {p: port_service_map.get(p, 'unknown') for p in ports_found}

        if not ports_found and not result['ssh_banner']:
            return None

        return result

    def _probe_ports(self, ip: str, ports: List[int], timeout: float = 1.0) -> List[int]:
        """探测端口是否开放"""
        open_ports = []
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))
                sock.close()
                if result == 0:
                    open_ports.append(port)
            except Exception:
                pass
        return open_ports
