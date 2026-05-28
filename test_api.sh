#!/bin/bash
cd /home/zcxx/.hermes/projects/itops_platform

# Get token - handle both {data:{access_token}} and {access_token:} formats
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123456"}')

TOKEN=$(echo "$RESPONSE" | python3 -c "
import sys,json
d=json.load(sys.stdin)
# Try nested format first, then flat
token = d.get('data',{}).get('access_token') or d.get('access_token','')
print(token)
")
echo "TOKEN=${TOKEN:0:20}..."

echo ""
echo "=== 1. convert-to-workorder (alert_id=1) ==="
curl -s -X POST "http://localhost:8000/api/v1/workorders/convert-to-workorder" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"alert_id": 1}'

echo ""
echo ""
echo "=== 2. admin/menus ==="
curl -s http://localhost:8000/api/v1/admin/menus -H "Authorization: Bearer $TOKEN"

echo ""
echo ""
echo "=== 3. admin/dicts ==="
curl -s http://localhost:8000/api/v1/admin/dicts -H "Authorization: Bearer $TOKEN"

echo ""
echo ""
echo "=== 4. monitoring/alerts/statistics ==="
curl -s http://localhost:8000/api/v1/monitoring/alerts/statistics -H "Authorization: Bearer $TOKEN"

echo ""
echo ""
echo "=== 5. monitoring/metrics/history ==="
curl -s "http://localhost:8000/api/v1/monitoring/metrics/history?metric_type=cpu_usage&hours=24" -H "Authorization: Bearer $TOKEN" | head -c 300

echo ""
echo ""
echo "=== 6. automation/scripts ==="
curl -s http://localhost:8000/api/v1/automation/scripts -H "Authorization: Bearer $TOKEN" | head -c 300
