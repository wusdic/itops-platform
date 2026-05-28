# Monitoring API Verification Report
**Date:** 2026-05-28 01:17 AM  
**API Base URL:** http://localhost:8000/api/v1  
**Auth:** admin / Admin@123456

---

## Verification Summary

| # | API Endpoint | Method | Status | Notes |
|---|---|---|---|---|
| 1 | `/monitoring/alerts/statistics` | GET | ✅ PASS | Returns total=6, critical=4, warning=0, info=2, active=3 |
| 2 | `/monitoring/alerts/stats` | GET | ✅ PASS | Alias route, returns same data |
| 3 | `/monitoring/metrics/history` | GET | ✅ PASS | Returns 100 points with timestamp/value/host |
| 4 | `/monitoring/metrics/history?device_id=1` | GET | ✅ PASS | Filters by device_id |
| 5 | `/monitoring/metrics/top/cpu` | ✅ PASS | Returns `{"status":"success","count":0,"items":[]}` (no cpu_usage data) |
| 6 | `/monitoring/metrics/top/memory` | GET | ✅ PASS | Returns success (no memory_usage data) |
| 7 | `/monitoring/metrics/top/disk` | GET | ✅ PASS | Returns success (no disk_usage data) |
| 8 | `/workorders/convert-to-workorder` (alert 999) | POST | ✅ PASS | Returns 404 "告警 999 不存在" |
| 9 | `/workorders/convert-to-workorder` (alert 5) | POST | ❌ FAIL | Internal Server Error |

---

## Detailed Test Results

### 1. GET /monitoring/alerts/statistics ✅

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/monitoring/alerts/statistics" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200 OK):**
```json
{
    "total": 6,
    "critical": 4,
    "warning": 0,
    "info": 2,
    "active": 3
}
```

**Analysis:** Works correctly. Shows 6 total alerts, 4 critical/high severity, 2 info/low, 3 active.

---

### 2. GET /monitoring/metrics/history ✅

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/monitoring/metrics/history" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200 OK):**
```json
{
    "status": "success",
    "metric": "all",
    "device_id": null,
    "count": 100,
    "points": [
        {
            "timestamp": "2026-05-28T00:51:09",
            "value": 0.0,
            "host": "auto-192-168-1-221"
        },
        ...
    ]
}
```

**Analysis:** Returns last 100 metric data points from the database. Supports filtering by `device_id`, `metric`, `start`, `end`, `step`, `limit`.

---

### 3. GET /monitoring/metrics/top/{type} ✅

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/monitoring/metrics/top/cpu" \
  -H "Authorization: Bearer $TOKEN"
```

**Response (200 OK):**
```json
{
    "status": "success",
    "metric_type": "cpu",
    "metric_name": "cpu_usage",
    "count": 0,
    "items": []
}
```

**Analysis:** Route works correctly. Returns empty results because no `cpu_usage` metric data exists with the required aggregation pattern. The metric type to metric name mapping (`cpu` → `cpu_usage`) works correctly.

**Note:** The query uses a subquery to find the MAX(timestamp) per device, then joins back to get the value. If no data matches `metric_name == 'cpu_usage'`, results are empty.

---

### 4. POST /workorders/convert-to-workorder (404 case) ✅

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/workorders/convert-to-workorder" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"alert_id": 999}'
```

**Response (404):**
```json
{
    "detail": "告警 999 不存在"
}
```

**Analysis:** Correctly returns 404 for non-existent alert.

---

### 5. POST /workorders/convert-to-workorder (real alert) ❌

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/workorders/convert-to-workorder" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"alert_id": 5}'
```

**Response (500 Internal Server Error):**
```json
{
    "error": "Internal Server Error",
    "request_id": "00c07103-8f9c-4b9d-a3a9-5546a548a58c"
}
```

**Analysis:** Bug identified in `api/routes/workorder.py` line 1507:

```python
title = request.title or f"[告警转工单] {alert.name or '未知告警'} (ID:{alert.id})"
```

The `Alert` model does NOT have a `name` attribute. The correct field is `title`. This causes an `AttributeError` when processing any valid alert.

**Expected fix:**
```python
title = request.title or f"[告警转工单] {alert.title or '未知告警'} (ID:{alert.id})"
```

Similarly line 1518:
```python
f"- 告警名称: {alert.name or '未知'}\n"
```
Should be:
```python
f"- 告警名称: {alert.title or '未知'}\n"
```

---

## API Inventory Check

From `API_INVENTORY.md`:
- `GET /api/v1/monitoring/alerts/statistics` - Status: ❌ (marked as missing, but actually EXISTS and WORKS)
- `GET /api/v1/monitoring/metrics/history` - Status: ❌ (marked as missing, but actually EXISTS and WORKS)
- `GET /api/v1/monitoring/metrics/top/{type}` - Status: ❌ (marked as missing, but actually EXISTS and WORKS)
- `POST /api/v1/workorders/convert-to-workorder` - Status: ❌ (marked as missing, but actually EXISTS but HAS BUG)

---

## Files Analyzed

| File | Purpose |
|---|---|
| `/home/zcxx/.hermes/projects/itops_platform/api/routes/monitoring.py` | Contains alerts/statistics, metrics/history, metrics/top routes |
| `/home/zcxx/.hermes/projects/itops_platform/api/routes/workorder.py` | Contains convert-to-workorder route (line 1490) |
| `/home/zcxx/.hermes/projects/itops_platform/modules/foundation/db_models/alert.py` | Alert model definition |

---

## Conclusion

**4 of 5 monitoring module APIs work correctly.** The `convert-to-workorder` endpoint has an AttributeError bug due to incorrect field reference (`alert.name` instead of `alert.title`).
