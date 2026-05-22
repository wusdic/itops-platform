# -*- coding: utf-8 -*-
"""自动发现设备可用凭据（默认账密 + 已配置账密）"""

import asyncio
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# 通用默认账密（几乎所有设备都尝试）
COMMON_DEFAULT_CREDS = [
    {"protocol": "ssh", "username": "admin", "password": ""},
    {"protocol": "ssh", "username": "admin", "password": "admin"},
    {"protocol": "ssh", "username": "root", "password": "root"},
    {"protocol": "ssh", "username": "root", "password": ""},
    {"protocol": "http", "username": "admin", "password": "admin"},
    {"protocol": "http", "username": "admin", "password": ""},
    {"protocol": "snmp", "community": "public"},
    {"protocol": "snmp", "community": "private"},
]

# 厂商特定默认账密
VENDOR_CREDENTIALS = {
    "Cisco Systems": {
        "ssh": [
            {"username": "cisco", "password": "cisco"},
            {"username": "admin", "password": "admin"},
            {"username": "cisco", "password": ""},
        ],
        "http": [
            {"username": "cisco", "password": "cisco"},
        ],
    },
    "Huawei": {
        "ssh": [
            {"username": "admin", "password": "admin"},
            {"username": "root", "password": "Huawei@2012"},
            {"username": "root", "password": ""},
        ],
        "http": [
            {"username": "admin", "password": "admin"},
        ],
    },
    "H3C (Huawei 3Com)": {
        "ssh": [
            {"username": "admin", "password": "admin"},
            {"username": "manager", "password": "manager"},
        ],
        "http": [
            {"username": "admin", "password": "admin"},
        ],
    },
    "Juniper Networks": {
        "ssh": [
            {"username": "root", "password": ""},
            {"username": "admin", "password": "admin"},
        ],
        "http": [
            {"username": "admin", "password": "admin"},
        ],
    },
    "Arista Networks": {
        "ssh": [
            {"username": "admin", "password": ""},
            {"username": "admin", "password": "admin"},
        ],
    },
    "Dell": {
        "ssh": [
            {"username": "admin", "password": "admin"},
            {"username": "root", "password": "calvin"},
        ],
        "http": [
            {"username": "admin", "password": "admin"},
        ],
    },
    "HPE": {
        "ssh": [
            {"username": "admin", "password": "admin"},
            {"username": "manager", "password": "manager"},
        ],
        "http": [
            {"username": "admin", "password": "admin"},
        ],
    },
    "TP-Link": {
        "http": [
            {"username": "admin", "password": "admin"},
            {"username": "admin", "password": ""},
        ],
        "ssh": [
            {"username": "admin", "password": "admin"},
        ],
    },
    "D-Link": {
        "http": [
            {"username": "admin", "password": "admin"},
        ],
        "ssh": [
            {"username": "admin", "password": "admin"},
        ],
    },
    "Hikvision Digital Technology": {
        "rtsp": [
            {"username": "admin", "password": "admin"},
            {"username": "admin", "password": ""},
        ],
        "http": [
            {"username": "admin", "password": "admin"},
            {"username": "admin", "password": ""},
        ],
    },
    "Dahua Technology": {
        "rtsp": [
            {"username": "admin", "password": "admin"},
            {"username": "admin", "password": ""},
        ],
        "http": [
            {"username": "admin", "password": "admin"},
        ],
    },
    "Fortinet": {
        "ssh": [
            {"username": "admin", "password": ""},
        ],
        "http": [
            {"username": "admin", "password": ""},
        ],
    },
    "Ubuntu": {
        "ssh": [
            {"username": "ubuntu", "password": ""},
            {"username": "root", "password": ""},
        ],
    },
    "CentOS": {
        "ssh": [
            {"username": "root", "password": ""},
        ],
    },
    "Red Hat": {
        "ssh": [
            {"username": "root", "password": ""},
        ],
    },
    "VMware": {
        "ssh": [
            {"username": "root", "password": ""},
        ],
        "http": [
            {"username": "root", "password": "vmware"},
        ],
    },
    "Synology": {
        "ssh": [
            {"username": "root", "password": ""},
        ],
        "http": [
            {"username": "admin", "password": "admin"},
        ],
    },
    "QNAP Systems": {
        "ssh": [
            {"username": "admin", "password": "admin"},
        ],
        "http": [
            {"username": "admin", "password": "admin"},
        ],
    },
    "Ruijie Networks": {
        "ssh": [
            {"username": "admin", "password": "admin"},
        ],
        "http": [
            {"username": "admin", "password": "admin"},
        ],
    },
    "Ruijie Reyee": {
        "http": [
            {"username": "admin", "password": "admin"},
        ],
    },
    "ZTE": {
        "ssh": [
            {"username": "admin", "password": "admin"},
        ],
        "http": [
            {"username": "admin", "password": "admin"},
        ],
    },
}


class CredentialDiscovery:
    """
    自动发现设备可用凭据（默认账密 + 已配置账密）
    
    按优先级尝试认证：
    1. 已配置的账密（最高优先级）
    2. 厂商默认账密（根据 fingerprint 的 vendor 匹配）
    3. 通用默认账密（admin/admin, root/root 等）
    """
    
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
    
    async def discover(
        self,
        ip: str,
        fingerprint: Dict,
        configured_creds: List[Dict],
    ) -> Dict[str, Any]:
        """
        探测设备的可用凭据
        
        Args:
            ip: 设备 IP
            fingerprint: 免认证指纹结果
            configured_creds: 已配置的账密列表
            
        Returns:
            {
                'success': True/False,
                'method': 'ssh'/'snmp'/'http'/...,
                'credential_source': 'configured'/'default'/'common',
                'is_default_credential': True/False,
                'credentials': {'username': ..., 'password': ...},
                'banner': ...,
                'failed_attempts': [...],
            }
        """
        vendor = fingerprint.get('mac_vendor') or fingerprint.get('os_vendor')
        open_ports = fingerprint.get('open_ports', {})
        
        # 优先级1: 已配置账密
        if configured_creds:
            for cred in configured_creds:
                result = await self._try_credential(ip, cred, open_ports)
                if result['success']:
                    result['credential_source'] = 'configured'
                    result['is_default_credential'] = False
                    return result
        
        # 优先级2: 厂商默认账密
        if vendor:
            vendor_creds = VENDOR_CREDENTIALS.get(vendor, {})
            for protocol, creds in vendor_creds.items():
                for cred in creds:
                    full_cred = {**cred, 'protocol': protocol}
                    result = await self._try_credential(ip, full_cred, open_ports)
                    if result['success']:
                        result['credential_source'] = 'default'
                        result['is_default_credential'] = True
                        result['vendor'] = vendor
                        return result
        
        # 优先级3: 通用默认账密
        for cred in COMMON_DEFAULT_CREDS:
            if self._protocol_available(cred.get('protocol'), open_ports):
                result = await self._try_credential(ip, cred, open_ports)
                if result['success']:
                    result['credential_source'] = 'common'
                    result['is_default_credential'] = True
                    return result
        
        return {
            'success': False,
            'credential_source': None,
            'is_default_credential': None,
        }
    
    def _protocol_available(self, protocol: str, open_ports: Dict) -> bool:
        """检查协议对应的端口是否开放"""
        port_map = {'ssh': 22, 'http': 80, 'https': 443, 'snmp': 161, 'telnet': 23}
        if protocol and protocol in port_map:
            return port_map[protocol] in open_ports
        return True  # 不确定时就尝试
    
    async def _try_credential(self, ip: str, cred: Dict, open_ports: Dict) -> Dict:
        """尝试单个账密"""
        protocol = cred.get('protocol', 'ssh')
        
        try:
            if protocol == 'ssh' and 22 in open_ports:
                return await self._try_ssh(ip, 22, cred.get('username', ''), cred.get('password', ''))
            elif protocol == 'http' and 80 in open_ports:
                return await self._try_http(ip, 80, cred.get('username', ''), cred.get('password', ''))
            elif protocol == 'https' and 443 in open_ports:
                return await self._try_http(ip, 443, cred.get('username', ''), cred.get('password', ''), use_ssl=True)
            elif protocol == 'snmp' and 161 in open_ports:
                return await self._try_snmp(ip, cred.get('community', 'public'))
        except Exception as e:
            logger.debug(f"Credential probe error: {e}")
        
        return {'success': False}
    
    async def _try_ssh(self, ip: str, port: int, username: str, password: str) -> Dict:
        """尝试 SSH 认证"""
        try:
            import paramiko
            from paramiko.ssh_exception import AuthenticationException
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._ssh_connect(ip, port, username, password)
            )
            return {'success': True, 'method': 'ssh', 'username': username, 'password': password}
        except Exception as e:
            return {'success': False, 'error': str(e)[:50]}
    
    def _ssh_connect(self, ip: str, port: int, username: str, password: str) -> bool:
        """同步 SSH 连接（在线程池中运行）"""
        import paramiko
        from paramiko.ssh_exception import AuthenticationException
        
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(ip, port=port, username=username, password=password,
                          timeout=self.timeout, banner_timeout=self.timeout, auth_timeout=self.timeout)
            client.close()
            return True
        except AuthenticationException:
            return False
        except Exception:
            return False
    
    async def _try_http(self, ip: str, port: int, username: str, password: str, use_ssl: bool = False) -> Dict:
        """尝试 HTTP Basic 认证"""
        import base64
        try:
            reader, writer = await asyncio.open_connection(ip, port)
            auth_string = f"{username}:{password}"
            auth_bytes = base64.b64encode(auth_string.encode('utf-8')).decode('ascii')
            request = f"GET / HTTP/1.0\r\nHost: {ip}\r\n"
            if username:
                request += f"Authorization: Basic {auth_bytes}\r\n"
            request += "\r\n"
            writer.write(request.encode('utf-8'))
            await writer.drain()
            response_bytes = await asyncio.wait_for(reader.read(512), timeout=self.timeout)
            writer.close()
            await writer.wait_closed()
            response = response_bytes.decode('utf-8', errors='ignore')
            if "401" in response:
                return {'success': False, 'error': '401_unauthorized'}
            return {'success': True, 'method': 'https' if use_ssl else 'http', 'username': username, 'password': password}
        except Exception as e:
            return {'success': False, 'error': str(e)[:50]}
    
    async def _try_snmp(self, ip: str, community: str) -> Dict:
        """尝试 SNMP 认证"""
        # 简化版：只检测端口可达
        # 完整版需要 pysnmp
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            packet = b'\x30' + b'\x00' * 20 + community.encode('utf-8') + b'\x00' * 10
            sock.sendto(packet, (ip, 161))
            sock.close()
            return {'success': True, 'method': 'snmp', 'community': community}
        except Exception:
            return {'success': False}
