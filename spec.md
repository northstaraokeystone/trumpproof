# TrumpProof Specification

**Version:** 1.0.0
**Status:** Active
**Tenant ID:** trumpproof

> No receipt → not real. $700B+ in transparency gaps. One umbrella, five modules.

## Executive Summary

TrumpProof is a receipts-native proof infrastructure suite targeting five Trump administration governance domains totaling $700B+ in documented transparency gaps. Built on ProofPack v3 architecture, each domain module produces verifiable receipts for every claim, decision, and transaction.

## The Paradigm Shift

| Old Paradigm | TrumpProof Paradigm |
|--------------|---------------------|
| Investigate after scandal | Receipts-native by construction |
| FOIA requests delayed | Real-time verification infrastructure |
| Compliance theater | Provable accountability |
| Partisan attack tools | Nonpartisan efficiency metrics |

**Core Insight:** Government accountability systems produce CLAIMS. TrumpProof produces RECEIPTS. Claims are contested. Receipts are mathematical.

## The Five Modules

| Module | Operator | Dollar Exposure | Priority |
|--------|----------|-----------------|----------|
| TariffProof | Howard Lutnick | $195B FY2025, $90B refunds | HIGH |
| BorderProof | Tom Homan | $170B allocation | HIGHEST |
| GulfProof | Jared Kushner | $5.4B AUM, $157M fees | Medium |
| GolfProof | Eric Trump | $354M annual | Medium |
| LicenseProof | Eric Trump | $36M licensing | LOW |

**Cross-Domain Pattern:** Saudi PIF is central node across Golf, Gulf, License, and indirectly Tariff domains.

## Inputs

### Data Sources
- CBP customs revenue data (tariff module)
- ICE budget allocations (border module)
- SEC filings and fund disclosures (gulf module)
- LIV Golf event data (golf module)
- Licensing agreements (license module)
- LDA filings (lobbying cross-reference)
- OFAC SDN list (sanctions screening)

### Input Schemas
All inputs are validated against JSON schemas in `data/schemas/`.

## Outputs

### Receipt Types
Every function emits a receipt. Receipt types include:
- `tariff_ingest_receipt`, `allocation_receipt`, `verification_receipt`
- `exemption_application_receipt`, `exemption_outcome_receipt`
- `detention_receipt`, `citizenship_verification_receipt`
- `swf_investment_receipt`, `fara_violation_receipt`
- `payment_receipt`, `emolument_assessment_receipt`
- `ownership_receipt`, `pif_connection_receipt`
- `loop_cycle_receipt`, `harvest_receipt`

### Receipt Format
```json
{
  "receipt_type": "string",
  "ts": "ISO8601",
  "tenant_id": "trumpproof",
  "payload_hash": "SHA256:BLAKE3"
}
```

## SLOs

| Operation | Threshold | Action on Breach |
|-----------|-----------|------------------|
| Ingest latency | ≤50ms p95 | reject |
| Verification latency | ≤100ms p95 | reject |
| Facility metrics staleness | ≤24h | escalate |
| Cost computation | ≤1s p95 | reject |
| Cycle completion | ≤60s | alert |

## Stoprules

1. **stoprule_hash_mismatch** - Emit anomaly, halt on hash mismatch
2. **stoprule_unverified_claim** - Emit anomaly, escalate on unverified claim
3. **stoprule_citizen_flag** - Emit anomaly, immediate review on potential citizen
4. **stoprule_death_rate** - Emit anomaly, halt on elevated death rate
5. **stoprule_fara_violation** - Emit anomaly, escalate on FARA violation

## Rollback

In case of critical failure:
1. Halt all cycles
2. Preserve receipt ledger
3. Emit `rollback_receipt` with reason
4. Notify operators
5. Wait for human intervention

## The 6 Mandatory Scenarios

1. **BASELINE** - Standard operation, 0 stoprule violations
2. **TARIFF_SCOTUS** - Model Supreme Court IEEPA decision scenarios
3. **BORDER_ACCOUNTABILITY** - Detention accountability under stress
4. **GULF_RETURNS** - Zero-return edge case handling
5. **CROSS_DOMAIN_PIF** - PIF detection in ≥4 domains
6. **GÖDEL** - Edge cases and graceful degradation

## Gate Requirements

### T+2h: SKELETON
- [ ] spec.md exists
- [ ] ledger_schema.json exists
- [ ] cli.py emits valid receipt

### T+24h: MVP
- [ ] pytest tests pass
- [ ] emit_receipt in all src/*.py
- [ ] assertions in all tests

### T+48h: HARDENED
- [ ] anomaly detection active
- [ ] bias checks present
- [ ] stoprules on all error paths
- [ ] All 6 scenarios pass
