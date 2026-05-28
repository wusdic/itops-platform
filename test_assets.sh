#!/bin/bash
cd /home/zcxx/.hermes/projects/itops_platform

RESP=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123456"}')

TOKEN=$(echo "$RESP" | python3 -c "
import sys,json
d=json.load(sys.stdin)
token = d.get('data',{}).get('access_token') or d.get('access_token','')
print(token)
")

echo "=== /assets/device (raw) ==="
curl -s "http://localhost:8000/api/v1/assets/device?page=1&page_size=3" \
  -H "Authorization: Bearer $TOKEN"

echo ""
echo "=== /devices/stats ==="
curl -s "http://localhost:8000/api/v1/devices/stats" \
  -H "Authorization: Bearer $TOKEN"

echo ""
echo "=== /monitoring/metrics/hosts ==="
curl -s "http://localhost:8000/api/v1/monitoring/metrics/hosts" \
  -H "Authorization: Bearer $TOKEN" | head -c 300
