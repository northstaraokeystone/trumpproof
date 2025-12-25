#!/bin/bash
# gate_t24h.sh - TrumpProof T+24h MVP Gate
# RUN THIS OR KILL PROJECT

set -e

echo "=== TrumpProof T+24h Gate: MVP ==="

# 1. Run T+2h gate first
./gate_t2h.sh || { echo "FAIL: T+2h gate failed"; exit 1; }

# 2. Run pytest
python3 -m pytest tests/ -q || { echo "FAIL: tests failed"; exit 1; }
echo "✓ pytest tests pass"

# 3. Verify emit_receipt in all src files (excluding constants and __init__)
for f in src/*.py src/*/*.py; do
    basename_f="$(basename $f)"
    if [ -f "$f" ] && [ "$basename_f" != "__init__.py" ] && [ "$basename_f" != "constants.py" ]; then
        grep -q "emit_receipt\|from.*core import" "$f" || { echo "FAIL: $f missing emit_receipt"; exit 1; }
    fi
done
echo "✓ emit_receipt in all src files"

# 4. Verify assertions in tests
for f in tests/*.py; do
    if [ -f "$f" ] && [ "$(basename $f)" != "__init__.py" ] && [ "$(basename $f)" != "conftest.py" ]; then
        grep -q "assert" "$f" || { echo "FAIL: $f missing assertions"; exit 1; }
    fi
done
echo "✓ assertions in all test files"

# 5. Verify all modules import
python3 -c "
from src.tariff import revenue, exemption, refund, lobby
from src.border import detention, contractor, citizenship, condition
from src.gulf import investment, fara, returns, fees
from src.golf import payment, event, sanctions, emoluments
from src.license import ownership, attestation, partner
from src.loop import cycle, harvest, cross_domain, pif_tracker
print('✓ all modules import successfully')
" || { echo "FAIL: module import failed"; exit 1; }

echo ""
echo "=== PASS: T+24h gate ==="
