#!/bin/bash
cd /home/zcxx/.hermes/projects/itops_platform

TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123456"}' | python3 -c "
import sys,json
d=json.load(sys.stdin)
token = d.get('data',{}).get('access_token') or d.get('access_token','')
print(token)
")

echo "=== page_size=200 ==="
curl -s "http://localhost:8000/api/v1/assets/device?page=1&page_size=200" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print('items:', len(d.get('items',[])), 'total:', d.get('total','?'))
"

echo "=== page_size=500 (should fail) ==="
curl -s "http://localhost:8000/api/v1/assets/device?page=1&page_size=500" \
  -H "Authorization: Bearer $TOKEN" | head -c 200
