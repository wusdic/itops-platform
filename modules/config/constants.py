# -*- coding: utf-8 -*-
"""
统一管理模块内的魔法数字常量
"""
from __future__ import annotations


# ========== 端口常量 ==========
class Port:
    """标准服务端口常量"""
    SYSLOG = 514              # Syslog 服务 (UDP/TCP)
    REDFISH = 443             # Redfish API (HTTPS)
    WINRM_HTTP = 5985         # WinRM HTTP
    WINRM_HTTPS = 5986        # WinRM HTTPS
    REDIS = 6379              # Redis
    RABBITMQ = 15672          # RabbitMQ Management API
    VMWARE = 443              # VMware vCenter/ESXi
    TELNET = 23               # Telnet


# ========== Telnet 协议常量 ==========
class TelnetCmd:
    """Telnet 协议命令字节常量 (RFC 854)"""
    IAC = bytes([255])        # Interpret As Command
    DONT = bytes([254])
    DO = bytes([253])
    WONT = bytes([252])
    WILL = bytes([251])
    SB = bytes([250])         # Sub-negotiation Begin
    SE = bytes([240])         # Sub-negotiation End
    ECHO = bytes([1])
    SGA = bytes([3])          # Suppress Go Ahead
    NAWS = bytes([31])         # Window Size
    TSPEED = bytes([32])
    ENVIRON = bytes([36])
    LINEMODE = bytes([34])
