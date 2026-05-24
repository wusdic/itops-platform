# modules/business/watermark_service.py — 操作水印服务
"""
为敏感操作生成可验证的防篡改水印。

原理：
  水印 = HMAC-SHA256(操作关键信息, 密钥) 的前16字符
  存储：operation_logs 表 watermark_id 字段

溯源验证：
  用户提供 watermark_id → 反查 operation_logs → 验证操作未被篡改
  watermark_id 格式：{action}:{resource}:{resource_id}:{operator}:{timestamp}:{hmac_prefix}
  示例：update:device:dev-001:admin:1779554818:a1b2c3d4e5f6
"""

import hmac
import hashlib
import time
from typing import Optional, Dict, Any
from datetime import datetime

WATERMARK_SECRET = "itops-platform-watermark-secret-v1"  # 生产环境从配置文件读取


def generate_watermark(
    action: str,
    resource: str,
    resource_id: str,
    operator: str,
    timestamp: Optional[float] = None,
) -> str:
    """
    生成操作水印 ID

    Args:
        action: 操作类型 (create/update/delete/export)
        resource: 资源类型 (device/workorder/alert/script/config)
        resource_id: 资源标识
        operator: 操作人
        timestamp: Unix 时间戳，默认当前时间

    Returns:
        水印 ID 字符串，如 "update:device:dev-001:admin:1779554818:a1b2c3d4"
    """
    if timestamp is None:
        timestamp = time.time()

    # 构造消息
    msg = f"{action}:{resource}:{resource_id}:{operator}:{int(timestamp)}"
    h = hmac.new(
        WATERMARK_SECRET.encode(),
        msg.encode(),
        hashlib.sha256,
    )
    hmac_prefix = h.hexdigest()[:16]

    return f"{msg}:{hmac_prefix}"


def verify_watermark(watermark_id: str) -> Dict[str, Any]:
    """
    验证水印是否有效（未被篡改）

    Args:
        watermark_id: 水印 ID

    Returns:
        {"valid": True/False, "reason": "...", "details": {...}}
    """
    parts = watermark_id.split(":")
    if len(parts) != 6:
        return {"valid": False, "reason": "水印格式错误"}

    action, resource, resource_id, operator, ts_str, hmac_prefix = parts

    try:
        ts = int(ts_str)
    except ValueError:
        return {"valid": False, "reason": "时间戳格式错误"}

    # 重建消息并重新计算 HMAC
    msg = f"{action}:{resource}:{resource_id}:{operator}:{ts}"
    expected_hmac = hmac.new(
        WATERMARK_SECRET.encode(),
        msg.encode(),
        hashlib.sha256,
    ).hexdigest()[:16]

    if not hmac.compare_digest(expected_hmac, hmac_prefix):
        return {"valid": False, "reason": "HMAC 校验失败，水印可能被篡改"}

    # 时间合理性检查（操作时间不能是未来或过久以前）
    now = time.time()
    if ts > now + 60:
        return {"valid": False, "reason": "操作时间异常（未来）", "details": {"timestamp": ts}}
    if now - ts > 365 * 24 * 3600:
        return {"valid": False, "reason": "水印已过期（超过1年）", "details": {"timestamp": ts}}

    return {
        "valid": True,
        "details": {
            "action": action,
            "resource": resource,
            "resource_id": resource_id,
            "operator": operator,
            "timestamp": ts,
            "operation_time": datetime.fromtimestamp(ts).isoformat(),
        },
    }


def parse_watermark(watermark_id: str) -> Optional[Dict[str, str]]:
    """解析水印 ID 各字段（不验证）"""
    parts = watermark_id.split(":")
    if len(parts) != 6:
        return None
    action, resource, resource_id, operator, ts_str, _ = parts
    try:
        return {
            "action": action,
            "resource": resource,
            "resource_id": resource_id,
            "operator": operator,
            "timestamp": ts_str,
        }
    except ValueError:
        return None


def batch_generate_watermarks(
    operations: list[Dict[str, Any]],
) -> list[Dict[str, Any]]:
    """批量生成水印（用于导出等批量操作）"""
    results = []
    for op in operations:
        wm = generate_watermark(
            action=op.get("action", "export"),
            resource=op.get("resource", "unknown"),
            resource_id=op.get("resource_id", "batch"),
            operator=op.get("operator", "system"),
        )
        results.append({"operation": op, "watermark_id": wm})
    return results
