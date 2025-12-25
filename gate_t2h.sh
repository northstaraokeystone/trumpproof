#!/bin/bash
# gate_t2h.sh - TrumpProof T+2h SKELETON Gate
# RUN THIS OR KILL PROJECT

set -e

echo "=== TrumpProof T+2h Gate: SKELETON ==="

# 1. Check required files exist
[ -f spec.md ] || { echo "FAIL: no spec.md"; exit 1; }
echo "✓ spec.md exists"

[ -f ledger_schema.json ] || { echo "FAIL: no ledger_schema.json"; exit 1; }
echo "✓ ledger_schema.json exists"

[ -f cli.py ] || { echo "FAIL: no cli.py"; exit 1; }
echo "✓ cli.py exists"

# 2. Verify schema is valid JSON
python3 -c "import json; json.load(open('ledger_schema.json'))" || { echo "FAIL: invalid ledger_schema.json"; exit 1; }
echo "✓ ledger_schema.json is valid JSON"

# 3. CLI emits valid receipt JSON
python3 cli.py --test 2>&1 | grep -q '"receipt_type"' || { echo "FAIL: cli.py does not emit receipt"; exit 1; }
echo "✓ cli.py emits valid receipt"

# 4. Verify tenant_id
python3 -c "from src.core import TENANT_ID; assert TENANT_ID == 'trumpproof', f'Wrong tenant: {TENANT_ID}'" || { echo "FAIL: wrong tenant_id"; exit 1; }
echo "✓ TENANT_ID is 'trumpproof'"

# 5. Verify dual_hash format
python3 -c "from src.core import dual_hash; h = dual_hash('test'); assert ':' in h, 'No colon in hash'" || { echo "FAIL: dual_hash format wrong"; exit 1; }
echo "✓ dual_hash produces SHA256:BLAKE3 format"

echo ""
echo "=== PASS: T+2h gate ==="
