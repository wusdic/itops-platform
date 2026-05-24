# -*- coding: utf-8 -*-
"""
IP Range Scanner for Device Auto-Discovery

Provides parallel ping sweep, TCP banner grabbing, and OS fingerprinting
for discovering devices in IP ranges.
"""

import asyncio
import logging
import socket
import struct
import concurrent.futures
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
from enum import Enum
import ipaddress
import re

logger = logging.getLogger(__name__)


class OSType(str, Enum):
    """操作系统类型"""
    WINDOWS = "windows"
    LINUX = "linux"
    UNIX = "unix"
    NETWORK = "network"
    UNKNOWN = "unknown"


@dataclass
class DiscoveredHost:
    """发现的Host"""
    ip: str
    hostname: Optional[str] = None
    mac: Optional[str] = None
    os_type: OSType = OSType.UNKNOWN
    os_version: Optional[str] = None
    vendor: Optional[str] = None
    ports: List[int] = field(default_factory=list)
    services: Dict[str, str] = field(default_factory=dict)
    status: str = "unknown"
    response_time: Optional[float] = None
    ttl: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)
    raw_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ip": self.ip,
            "hostname": self.hostname,
            "mac": self.mac,
            "os_type": self.os_type.value if isinstance(self.os_type, OSType) else self.os_type,
            "os_version": self.os_version,
            "vendor": self.vendor,
            "ports": self.ports,
            "services": self.services,
            "status": self.status,
            "response_time": self.response_time,
            "ttl": self.ttl,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class IPScanner:
    """
    IP Range Scanner
    
    Features:
    - Parallel ping sweep
    - TCP banner grabbing
    - OS fingerprinting based on TTL and banner
    - Common port scanning
    """
    
    # Common ports to scan (includes 8000 for local FastAPI)
    COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5900, 8080, 8443, 8000]
    
    # TCP ports for banner grabbing
    BANNER_PORTS = [21, 22, 23, 80, 443, 3306, 3389, 8080]
    
    # OS detection patterns
    WINDOWS_BANNER_PATTERNS = [b"windows", b"microsoft", b"iis", b"asp.net"]
    LINUX_BANNER_PATTERNS = [b"linux", b"ubuntu", b"centos", b"debian", b"red hat", b"fedora", b"ssh-", b"apache", b"nginx"]
    NETWORK_DEVICE_PATTERNS = [b"cisco", b"huawei", b"h3c", b"juniper", b"arista", b"dell", b"hp ", b"broadcom", b"router", b"switch"]
    
    def __init__(
        self,
        timeout: float = 2.0,
        ping_timeout: float = 1.0,
        ping_count: int = 2,
        max_workers: int = 50,
        ports: List[int] = None,
    ):
        """
        Initialize IP Scanner
        
        Args:
            timeout: TCP connection timeout
            ping_timeout: Ping timeout per host
            ping_count: Number of ping attempts
            max_workers: Maximum parallel workers
            ports: Custom port list (defaults to COMMON_PORTS)
        """
        self.timeout = timeout
        self.ping_timeout = ping_timeout
        self.ping_count = ping_count
        self.max_workers = max_workers
        self.ports = ports or self.COMMON_PORTS
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    
    async def scan_ip_range(
        self,
        cidr: str,
        progress_callback: Callable[[int, int, str], None] = None,
    ) -> List[DiscoveredHost]:
        """
        Scan IP range (CIDR notation)
        
        Args:
            cidr: CIDR notation (e.g., "192.168.1.0/24")
            progress_callback: Optional callback(complete, total, current_ip)
            
        Returns:
            List of discovered hosts
        """
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            hosts = list(network.hosts())
            total = len(hosts)
            
            logger.info(f"Scanning {cidr}: {total} hosts to check")
            
            discovered = []
            completed = 0
            
            # Use semaphore to limit concurrent operations
            semaphore = asyncio.Semaphore(self.max_workers)
            
            async def scan_host(host):
                async with semaphore:
                    nonlocal completed
                    try:
                        result = await self._scan_single_host(str(host))
                        completed += 1
                        if progress_callback:
                            progress_callback(completed, total, str(host))
                        return result
                    except Exception as e:
                        logger.debug(f"Error scanning {host}: {e}")
                        completed += 1
                        if progress_callback:
                            progress_callback(completed, total, str(host))
                        return None
            
            tasks = [scan_host(host) for host in hosts]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, DiscoveredHost) and result.status == "up":
                    discovered.append(result)
            
            logger.info(f"Discovery complete: {len(discovered)} hosts up out of {total} scanned")
            return discovered
            
        except ValueError as e:
            logger.error(f"Invalid CIDR format: {cidr} - {e}")
            raise ValueError(f"Invalid CIDR format: {cidr}") from e
    
    async def scan_hosts(
        self,
        hosts: List[str],
        progress_callback: Callable[[int, int, str], None] = None,
    ) -> List[DiscoveredHost]:
        """
        Scan specific hosts
        
        Args:
            hosts: List of IP addresses or hostnames
            progress_callback: Optional callback
            
        Returns:
            List of discovered hosts
        """
        total = len(hosts)
        discovered = []
        completed = 0
        
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def scan_host(ip):
            nonlocal completed
            async with semaphore:
                try:
                    result = await self._scan_single_host(ip)
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total, ip)
                    return result
                except Exception as e:
                    logger.debug(f"Error scanning {ip}: {e}")
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total, ip)
                    return None
        
        tasks = [scan_host(ip) for ip in hosts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, DiscoveredHost) and result.status == "up":
                discovered.append(result)
        
        return discovered
    
    async def _scan_single_host(self, ip: str) -> Optional[DiscoveredHost]:
        """
        Scan a single host - ping first, then do port scan and banner grab
        """
        start_time = datetime.now()
        
        # Ping check first
        is_alive, ttl, response_time = await self._ping(ip)
        
        if not is_alive:
            # Try TCP check as fallback for hosts that block ICMP
            is_alive = await self._tcp_check(ip, [80, 443, 22])
            if not is_alive:
                return DiscoveredHost(ip=ip, status="down")
        
        host = DiscoveredHost(
            ip=ip,
            status="up",
            ttl=ttl,
            response_time=response_time,
        )
        
        # Try to resolve hostname
        try:
            hostname, _, _ = await asyncio.get_event_loop().run_in_executor(
                None, socket.gethostbyaddr, ip
            )
            host.hostname = hostname
        except (socket.herror, socket.gaierror, Exception):
            pass
        
        # Detect OS
        host.os_type, host.os_version = self._detect_os(ttl, b"")  # Will be refined after banner grab
        
        # Scan ports
        open_ports = await self._scan_ports(ip, self.ports)
        host.ports = open_ports
        
        # Grab banners
        banners = await self._grab_banners(ip, self.BANNER_PORTS)
        host.services = banners
        
        # Refine OS detection with banner info
        combined_banner = " ".join(banners.values()).encode('utf-8', errors='ignore') if banners else b""
        host.os_type, host.os_version = self._detect_os(ttl, combined_banner)
        
        # Detect vendor from banners
        host.vendor = self._detect_vendor(combined_banner)
        
        host.timestamp = datetime.now()
        return host
    
    async def _ping(self, ip: str) -> tuple:
        """
        Ping a host using asyncio
        
        Returns:
            (is_alive, ttl, response_time_ms)
        """
        try:
            # Try ICMP ping first (requires root on Linux)
            loop = asyncio.get_event_loop()
            
            # Create raw socket for ICMP
            # Note: This may fail without root privileges
            import os
            import struct
            import time
            
            if os.getuid() == 0:  # root
                return await self._icmp_ping(ip)
            else:
                # Fallback to TCP ping
                return await self._tcp_ping_fallback(ip)
                
        except Exception as e:
            logger.debug(f"Ping failed for {ip}: {e}")
            return await self._tcp_ping_fallback(ip)
    
    async def _icmp_ping(self, ip: str) -> tuple:
        """ICMP ping (requires root)"""
        try:
            import os
            import struct
            import time
            import asyncio
            
            # Create raw ICMP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            sock.setsockopt(socket.SOL_IP, socket.IP_TTL, 64)
            sock.settimeout(self.ping_timeout)
            
            # ICMP echo request
            packet_id = os.getpid() & 0xFFFF
            seq = 1
            
            header = struct.pack('!BBHHH', 8, 0, 0, packet_id, seq)
            data = b'ping'
            
            # Calculate checksum
            def checksum(data):
                s = 0
                for i in range(0, len(data), 2):
                    s += (data[i] << 8) + data[i + 1]
                while s >> 16:
                    s = (s & 0xFFFF) + (s >> 16)
                return ~s & 0xFFFF
            
            checksum_val = checksum(header + data)
            header = struct.pack('!BBHHH', 8, 0, checksum_val, packet_id, seq)
            packet = header + data
            
            start_time = time.time()
            sock.sendto(packet, (ip, 0))
            
            # Wait for reply
            recv_packet, addr = sock.recv(1024)
            end_time = time.time()
            
            sock.close()
            
            # Parse ICMP response
            icmp_header = recv_packet[20:28]
            _, _, _, seq = struct.unpack('!BBHHH', icmp_header)
            
            response_time = (end_time - start_time) * 1000  # ms
            ttl = 64  # Default TTL
            
            return True, ttl, response_time
            
        except Exception as e:
            logger.debug(f"ICMP ping failed for {ip}: {e}")
            return False, None, None
    
    async def _tcp_ping_fallback(self, ip: str) -> tuple:
        """TCP ping fallback - try to connect to common ports"""
        try:
            # 扩展常见端口列表，覆盖更多服务
            for port in [80, 443, 22, 445, 3306, 3389, 8080, 8443, 8000, 6379, 5432, 27017, 9200, 2375]:
                if await self._tcp_check(ip, [port]):
                    return True, 64, None  # Assume TTL of 64 for responsive hosts
            return False, None, None
        except Exception:
            return False, None, None
    
    async def _tcp_check(self, ip: str, ports: List[int]) -> bool:
        """Check if host is reachable via TCP"""
        
        async def check_port(port):
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(ip, port),
                    timeout=self.timeout,
                )
                writer.close()
                await writer.wait_closed()
                return True
            except Exception:
                return False
        
        results = await asyncio.gather(*[check_port(p) for p in ports], return_exceptions=True)
        return any(r is True for r in results)
    
    async def _scan_ports(self, ip: str, ports: List[int]) -> List[int]:
        """Scan ports on a host"""
        
        async def check_port(port):
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(ip, port),
                    timeout=self.timeout,
                )
                writer.close()
                await writer.wait_closed()
                return port
            except Exception:
                return None
        
        results = await asyncio.gather(*[check_port(p) for p in ports], return_exceptions=True)
        return [r for r in results if r is not None]
    
    async def _grab_banners(self, ip: str, ports: List[int]) -> Dict[str, str]:
        """Grab service banners"""
        banners = {}
        
        async def grab_banner(port):
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(ip, port),
                    timeout=self.timeout,
                )
                
                # Send HTTP request for web ports
                if port in [80, 443, 8080, 8443]:
                    writer.write(b"GET / HTTP/1.0\r\nHost: %s\r\n\r\n" % ip.encode())
                    await writer.drain()
                
                try:
                    data = await asyncio.wait_for(reader.read(1024), timeout=self.timeout)
                    if data:
                        banner = data.decode('utf-8', errors='ignore').strip()
                        if banner:
                            service_name = self._identify_service(port, banner)
                            banners[service_name] = banner[:200]
                except asyncio.TimeoutError:
                    pass
                
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
        
        await asyncio.gather(*[grab_banner(p) for p in ports], return_exceptions=True)
        return banners
    
    def _identify_service(self, port: int, banner: str) -> str:
        """Identify service based on port and banner"""
        port_service_map = {
            21: "ftp",
            22: "ssh",
            23: "telnet",
            25: "smtp",
            53: "dns",
            80: "http",
            110: "pop3",
            143: "imap",
            443: "https",
            3306: "mysql",
            3389: "rdp",
            5900: "vnc",
            8080: "http-proxy",
            8443: "https-alt",
        }
        return port_service_map.get(port, f"port-{port}")
    
    def _detect_os(self, ttl: Optional[int], banner: bytes) -> tuple:
        """
        Detect OS type and version from TTL and banner
        
        Returns:
            (os_type, os_version)
        """
        banner_lower = banner.lower() if banner else b""
        
        # Check banner patterns first
        for pattern in self.WINDOWS_BANNER_PATTERNS:
            if pattern in banner_lower:
                return OSType.WINDOWS, self._extract_version(banner_lower, [b"windows", b"microsoft"])
        
        for pattern in self.LINUX_BANNER_PATTERNS:
            if pattern in banner_lower:
                return OSType.LINUX, self._extract_version(banner_lower, [b"linux", b"ubuntu", b"centos", b"debian"])
        
        for pattern in self.NETWORK_DEVICE_PATTERNS:
            if pattern in banner_lower:
                return OSType.NETWORK, self._extract_version(banner_lower, [b"cisco", b"huawei", b"juniper"])
        
        # TTL-based detection as fallback
        if ttl:
            if ttl <= 64:
                return OSType.LINUX, "linux/unix (TTL-based)"
            elif ttl <= 128:
                return OSType.WINDOWS, "windows (TTL-based)"
            elif ttl <= 255:
                return OSType.NETWORK, "network device (TTL-based)"
        
        return OSType.UNKNOWN, None
    
    def _extract_version(self, banner: bytes, keywords: List[bytes]) -> Optional[str]:
        """Extract version string from banner"""
        for keyword in keywords:
            if keyword in banner:
                # Try to find version pattern
                match = re.search(rb'(\d+\.\d+(?:\.\d+)?)', banner)
                if match:
                    return match.group(1).decode('utf-8', errors='ignore')
        return None
    
    def _detect_vendor(self, banner: bytes) -> Optional[str]:
        """Detect vendor from banner"""
        banner_lower = banner.lower() if banner else b""
        
        vendor_patterns = {
            "Cisco": [b"cisco", b"ios-xe", b"nx-os", b"ios"],
            "Huawei": [b"huawei", b"vrp"],
            "Juniper": [b"juniper", b"junos"],
            "H3C": [b"h3c", b"comware"],
            "Arista": [b"arista", b"eos"],
            "Dell": [b"dell"],
            "HP": [b"hp ", b"hewlett"],
            "VMware": [b"vmware", b"esxi"],
            "Microsoft": [b"windows", b"microsoft"],
            "Linux": [b"linux", b"ubuntu", b"centos", b"debian"],
        }
        
        for vendor, patterns in vendor_patterns.items():
            for pattern in patterns:
                if pattern in banner_lower:
                    return vendor
        
        return None
    
    def _parse_target(self, target: str) -> List[str]:
        """Parse target string into list of IP addresses
        
        Args:
            target: CIDR notation (e.g., "192.168.1.0/24") or single IP
            
        Returns:
            List of IP address strings
        """
        targets = []
        
        try:
            if '/' in target:
                network = ipaddress.ip_network(target, strict=False)
                for ip in network.hosts():
                    targets.append(str(ip))
            else:
                # Validate single IP address
                ipaddress.ip_address(target)
                targets.append(target)
        except ValueError as e:
            logger.error(f"Invalid target format: {target} - {e}")
            raise ValueError(f"Invalid target format: {target}") from e
        
        return targets
    
    def close(self):
        """Close the scanner and cleanup resources"""
        self._executor.shutdown(wait=False)


# Global scanner instance
_scanner: Optional[IPScanner] = None


def get_scanner() -> IPScanner:
    """Get or create global scanner instance"""
    global _scanner
    if _scanner is None:
        _scanner = IPScanner()
    return _scanner


# ============== ARP Scanner ==============

class ARPScanner:
    """
    ARP-based network discovery scanner.

    Provides active ARP scanning using raw sockets (requires root),
    and passive ARP cache reading (works without root).

    ARP discovers devices on the same L2 network segment, providing
    MAC addresses that help identify device vendors and detect IP
    conflicts.
    """

    ARP_OP_REQUEST = 1
    ARP_OP_REPLY = 2

    def __init__(self, timeout: float = 2.0, max_workers: int = 50):
        self.timeout = timeout
        self.max_workers = max_workers

    async def scan_ip_range(
        self,
        cidr: str,
        progress_callback: Callable[[int, int, str], None] = None,
    ) -> List[DiscoveredHost]:
        """
        Scan IP range using ARP.

        Uses raw ARP packets when running as root (active scan).
        Falls back to reading /proc/net/arp cache when not root (passive).

        Args:
            cidr: CIDR notation (e.g. "192.168.1.0/24")
            progress_callback: Optional callback(complete, total, current_ip)

        Returns:
            List of DiscoveredHost with MAC addresses populated
        """
        import os

        network = ipaddress.ip_network(cidr, strict=False)
        hosts = list(network.hosts())
        total = len(hosts)

        logger.info(f"ARP scanning {cidr}: {total} hosts")

        if os.getuid() == 0:
            discovered = await self._active_arp_scan(hosts, progress_callback)
        else:
            discovered = await self._passive_arp_scan(hosts, progress_callback)

        logger.info(f"ARP discovery complete: {len(discovered)} hosts found")
        return discovered

    async def _active_arp_scan(
        self,
        hosts: List[Any],
        progress_callback: Callable[[int, int, str], None] = None,
    ) -> List[DiscoveredHost]:
        """Send ARP requests using raw sockets (requires root)."""
        discovered = []
        completed = 0
        total = len(hosts)
        semaphore = asyncio.Semaphore(self.max_workers)

        async def arp_one(host_str: str):
            nonlocal completed
            async with semaphore:
                try:
                    result = await self._arp_request(str(host_str))
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total, str(host_str))
                    return result
                except Exception as e:
                    logger.debug(f"ARP failed for {host_str}: {e}")
                    completed += 1
                    if progress_callback:
                        progress_callback(completed, total, str(host_str))
                    return None

        tasks = [arp_one(h) for h in hosts]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, DiscoveredHost) and result.mac:
                discovered.append(result)

        return discovered

    async def _arp_request(self, ip: str) -> Optional[DiscoveredHost]:
        """
        Send a single ARP request via raw socket and wait for reply.

        Returns DiscoveredHost with MAC if target responds, None otherwise.
        """
        import os
        import struct
        import time

        # Get source IP and MAC of this host on the relevant interface
        src_ip = self._get_local_ip()
        src_mac = self._get_local_mac()
        if not src_ip or not src_mac:
            return None

        # Build ARP request packet
        eth_dst = b'\xff\xff\xff\xff\xff\xff'       # Broadcast
        eth_src = self._mac_str_to_bytes(src_mac)   # Our MAC
        eth_type = struct.pack('!H', 0x0806)         # ARP

        # ARP header
        htype = struct.pack('!H', 1)                  # Ethernet
        ptype = struct.pack('!H', 0x0800)             # IPv4
        hlen = struct.pack('!B', 6)                   # MAC length
        plen = struct.pack('!B', 4)                   # IP length
        oper = struct.pack('!H', self.ARP_OP_REQUEST)

        sha = self._mac_str_to_bytes(src_mac)         # Sender MAC
        spa = socket.inet_aton(src_ip)                # Sender IP
        tha = b'\x00\x00\x00\x00\x00\x00'            # Target MAC (unknown)
        tpa = socket.inet_aton(ip)                    # Target IP

        arp_packet = eth_src + eth_dst + eth_type + htype + ptype + hlen + plen + oper + sha + spa + tha + tpa

        # Build Ethernet frame: dstMAC + srcMAC + ethertype
        frame = eth_dst + eth_src + eth_type + arp_packet[14:]

        try:
            sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(0x0806))
            sock.settimeout(self.timeout)

            # Bind to any interface (or try to find the right one)
            try:
                sock.bind(('any', 0))
            except (OSError, ValueError):
                # Try default interface
                try:
                    sock.bind(('eth0', 0))
                except (OSError, ValueError):
                    try:
                        sock.bind(('ens33', 0))
                    except (OSError, ValueError):
                        pass

            start = time.time()
            sock.send(frame)
            response = sock.recv(1024)
            elapsed = (time.time() - start) * 1000

            sock.close()

            # Parse ARP reply: Ethernet(14) + ARP(28)
            if len(response) < 42:
                return None

            arp_data = response[14:]
            ethertype = struct.unpack('!H', arp_data[12:14])[0]
            if ethertype != 0x0806:
                return None

            oper = struct.unpack('!H', arp_data[6:8])[0]
            if oper != self.ARP_OP_REPLY:
                return None

            sender_mac_bytes = arp_data[8:14]
            sender_mac = self._mac_bytes_to_str(sender_mac_bytes)
            sender_ip = socket.inet_ntoa(arp_data[14:18])

            host = DiscoveredHost(
                ip=sender_ip,
                mac=sender_mac,
                status="up",
                response_time=elapsed,
                vendor=self._vendor_from_mac(sender_mac),
            )
            host.os_type, host.os_version = self._os_hint_from_mac(sender_mac)
            return host

        except (OSError, Exception) as e:
            logger.debug(f"Raw ARP socket error for {ip}: {e}")
            return None

    def _get_local_ip(self) -> Optional[str]:
        """Get this host's IP address by connecting to an external address."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return None

    def _get_local_mac(self) -> str:
        """Get this host's MAC address from /sys/class/net/*/address."""
        import glob
        for path in glob.glob("/sys/class/net/*/address"):
            try:
                mac = open(path).read().strip()
                if mac != "00:00:00:00:00:00":
                    return mac
            except Exception:
                pass
        return "00:00:00:00:00:00"

    async def _passive_arp_scan(
        self,
        hosts: List[Any],
        progress_callback: Callable[[int, int, str], None] = None,
    ) -> List[DiscoveredHost]:
        """
        Read /proc/net/arp to get ARP cache entries.
        Works without root, but only shows cached entries.
        """
        discovered = []
        completed = 0
        total = len(hosts)

        try:
            with open("/proc/net/arp", "r") as f:
                lines = f.readlines()[1:]  # Skip header

            host_set = {str(h) for h in hosts}
            arp_map: Dict[str, str] = {}

            for line in lines:
                parts = line.split()
                if len(parts) < 4:
                    continue
                ip_addr = parts[0]
                hw_type = parts[1]
                mac_addr = parts[3]

                if hw_type != "0x1":
                    continue  # Not Ethernet
                if mac_addr in ("00:00:00:00:00:00", "...(ignored)"):
                    continue

                arp_map[ip_addr] = mac_addr

            for ip_str in host_set:
                completed += 1
                if progress_callback:
                    progress_callback(completed, total, ip_str)

                if ip_str in arp_map:
                    mac = arp_map[ip_str]
                    host = DiscoveredHost(
                        ip=ip_str,
                        mac=mac,
                        status="up",
                        vendor=self._vendor_from_mac(mac),
                    )
                    host.os_type, host.os_version = self._os_hint_from_mac(mac)
                    discovered.append(host)

        except Exception as e:
            logger.error(f"Failed to read /proc/net/arp: {e}")

        return discovered

    def _mac_str_to_bytes(self, mac: str) -> bytes:
        return bytes(int(b, 16) for b in mac.split(':'))

    def _mac_bytes_to_str(self, b: bytes) -> str:
        return ':'.join(f'{x:02x}' for x in b)

    def _vendor_from_mac(self, mac: str) -> Optional[str]:
        """Look up vendor OUI from first 3 bytes of MAC."""
        oui = mac.replace(':', '').upper()[:6]
        from .scanner import OUI_DATABASE
        return OUI_DATABASE.get(oui)

    def _os_hint_from_mac(self, mac: str) -> tuple:
        """Coarse OS hint from MAC prefix (some vendors = network设备)."""
        oui = mac.replace(':', '').upper()[:6]
        network_vendors = {
            '000FE2',  # Cisco
            '001E68',  # Huawei
            '00269F',  # Huawei
            '34A3B8',  # Huawei
            'D4E949',  # HP
            '3C4A4B',  # Cisco
            '00264A',  # Juniper
        }
        if oui in network_vendors:
            return OSType.NETWORK, "network device (ARP)"
        return OSType.UNKNOWN, None


# Global ARP scanner instance
_arp_scanner: Optional[ARPScanner] = None


def get_arp_scanner() -> ARPScanner:
    """Get or create global ARP scanner instance."""
    global _arp_scanner
    if _arp_scanner is None:
        _arp_scanner = ARPScanner()
    return _arp_scanner


# OUI database — first 3 bytes of MAC -> vendor name
OUI_DATABASE = {
    "000000": "Xerox",
    "0050F2": "Microsoft",
    "00155D": "Microsoft (Hyper-V)",
    "00163E": "Xen",
    "001C42": "Parallels",
    "001E52": "Cisco",
    "001E68": "Huawei",
    "002264": "Cisco",
    "00264A": "Juniper",
    "00269F": "Huawei",
    "00269F": "Huawei",
    "0027D8": "HP",
    "00300F": "Cisco",
    "003065": "Cisco",
    "00308F": "Cisco",
    "003EE1": "Apple",
    "004269": "Cisco",
    "0050F2": "Microsoft",
    "006051": "Cisco",
    "00E04C": "Realtek",
    "00F76F": "Cisco",
    "00FEDC": "Apple",
    "080027": "VirtualBox",
    "0C8D98": "Apple",
    "14109F": "Apple",
    "18AF61": "Cisco",
    "1C6976": "Cisco",
    "204E91": "Cisco",
    "20A2E4": "Google",
    "246E96": "Juniper",
    "28CF5B": "Apple",
    "2C33BE": "Apple",
    "2C8D9C": "Apple",
    "30F7C5": "Apple",
    "34A3B8": "Huawei",
    "34785A": "Cisco",
    "3497AF": "Cisco",
    "34E2FD": "Cisco",
    "38009C": "Huawei",
    "3C15C2": "HP",
    "3C4A4B": "Cisco",
    "3C5AB4": "Cisco",
    "3C97BF": "Samsung",
    "40B395": "Cisco",
    "440444": "Cisco",
    "44D884": "Cisco",
    "4C526F": "Cisco",
    "50A3C8": "Cisco",
    "50EDBB": "HP",
    "54B802": "Cisco",
    "58556A": "Cisco",
    "5C005C": "Cisco",
    "5C1BBE": "Dell",
    "5C5098": "HP",
    "5C5182": "Juniper",
    "5C5EAB": "Cisco",
    "64776B": "Cisco",
    "6805CA": "Cisco",
    "6C40F9": "Cisco",
    "70A2B3": "Cisco",
    "70DF2F": "HP",
    "74A226": "Cisco",
    "78A3E4": "Cisco",
    "78S10G": "Dell",
    "7C5CF8": "Cisco",
    "80C8A2": "HP",
    "8425DB": "Cisco",
    "84841F": "Cisco",
    "8843F1": "Cisco",
    "8C851E": "HP",
    "8CAEC2": "HP",
    "9062AF": "Cisco",
    "94A7B1": "Cisco",
    "9898A6": "D-Link",
    "9C8E64": "Cisco",
    "9CAC7C": "Arista",
    "9CDD0F": "Cisco",
    "A03D6E": "HP",
    "A4148A": "Arista",
    "A447DD": "Cisco",
    "A8E1EE": "HPE",
    "ACDE48": "Dell",
    "B0E1B0": "Cisco",
    "B4148B": "Arista",
    "B49691": "Cisco",
    "B89E7C": "Dell",
    "BC9FEF": "Cisco",
    "C026E7": "HP",
    "C064EB": "HP",
    "C0C522": "Huawei",
    "C81F66": "D-Link",
    "CC4E24": "Arista",
    "CC6EE0": "HP",
    "D02EB0": "HP",
    "D47AE2": "Cisco",
    "D4C1DE": "Arista",
    "D4E949": "HP",
    "D8720B": "Dell",
    "DC81F2": "Dell",
    "E01C41": "Arista",
    "E4C62F": "HP",
    "E4EAA4": "Huawei",
    "E8B248": "Dell",
    "EC8EB8": "Cisco",
    "F04DB2": "Huawei",
    "F07689": "Huawei",
    "F4CF252": "HP",
    "F4E9D8": "Cisco",
    "F80F41": "Cisco",
    "FC15B4": "HP",
    "FC8F90C": "Huawei",
}

