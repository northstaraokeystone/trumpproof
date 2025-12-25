#!/usr/bin/env python3
"""TrumpProof CLI

Receipts-Native Government Accountability Infrastructure.
No receipt → not real. $700B+ in transparency gaps. One umbrella, five modules.

Usage:
    python cli.py --test              Run quick validation
    python cli.py --scenario NAME     Run specific scenario
    python cli.py --all               Run all 6 scenarios
    python cli.py --receipt TYPE      Emit sample receipt
"""

import argparse
import json
import sys

from src.core import emit_receipt, dual_hash, TENANT_ID
from src.constants import (
    TARIFF_FY2025_REVENUE,
    BORDER_FOUR_YEAR_ALLOCATION,
    PIF_TOTAL_EXPOSURE,
)


def main():
    parser = argparse.ArgumentParser(
        description="TrumpProof: Receipts-Native Government Accountability Infrastructure"
    )
    parser.add_argument("--test", action="store_true", help="Run quick validation")
    parser.add_argument("--scenario", type=str, help="Run specific scenario")
    parser.add_argument("--all", action="store_true", help="Run all 6 scenarios")
    parser.add_argument("--receipt", type=str, help="Emit sample receipt of TYPE")
    parser.add_argument("--version", action="store_true", help="Show version")

    args = parser.parse_args()

    if args.version:
        print("TrumpProof v1.0.0")
        print(f"Tenant: {TENANT_ID}")
        print(f"Total Exposure: ${PIF_TOTAL_EXPOSURE / 1e9:.1f}B+")
        return 0

    if args.test:
        return run_test()

    if args.receipt:
        return emit_sample_receipt(args.receipt)

    if args.scenario:
        return run_scenario(args.scenario)

    if args.all:
        return run_all_scenarios()

    # Default: emit test receipt
    return run_test()


def run_test():
    """Run quick validation - emit test receipt."""
    print("=== TrumpProof Quick Validation ===", file=sys.stderr)

    # Test core functions
    h = dual_hash("trumpproof")
    assert ":" in h, "dual_hash must produce SHA256:BLAKE3 format"
    print(f"✓ dual_hash: {h[:32]}...", file=sys.stderr)

    # Emit test receipt
    r = emit_receipt(
        "test",
        {
            "tenant_id": TENANT_ID,
            "domain": "validation",
            "message": "TrumpProof validation successful",
        },
    )
    assert "receipt_type" in r
    assert r["tenant_id"] == TENANT_ID
    print("✓ emit_receipt: functional", file=sys.stderr)

    # Test constants
    print(f"✓ Tariff FY2025: ${TARIFF_FY2025_REVENUE / 1e9:.0f}B", file=sys.stderr)
    print(
        f"✓ Border allocation: ${BORDER_FOUR_YEAR_ALLOCATION / 1e9:.0f}B",
        file=sys.stderr,
    )
    print(f"✓ PIF exposure: ${PIF_TOTAL_EXPOSURE / 1e9:.1f}B", file=sys.stderr)

    print("\n=== PASS: Quick validation complete ===", file=sys.stderr)
    return 0


def emit_sample_receipt(receipt_type: str):
    """Emit sample receipt of given type."""
    samples = {
        "tariff": {"domain": "tariff", "revenue": TARIFF_FY2025_REVENUE},
        "border": {"domain": "border", "allocation": BORDER_FOUR_YEAR_ALLOCATION},
        "gulf": {"domain": "gulf", "pif_investment": 2_000_000_000},
        "golf": {"domain": "golf", "liv_investment": 4_580_000_000},
        "license": {"domain": "license", "annual_revenue": 36_000_000},
        "pif": {"domain": "cross_domain", "total_exposure": PIF_TOTAL_EXPOSURE},
    }

    data = samples.get(receipt_type, {"domain": receipt_type})
    data["tenant_id"] = TENANT_ID

    emit_receipt(receipt_type, data)
    return 0


def run_scenario(scenario_name: str):
    """Run specific scenario."""
    try:
        from src.sim import run_scenario as sim_run_scenario

        result = sim_run_scenario(scenario_name)
        print(
            json.dumps(
                {
                    "scenario": result.scenario,
                    "passed": result.passed,
                    "message": result.message,
                    "n_cycles": result.n_cycles,
                    "violations": len(result.violations),
                    "pif_domains": result.pif_domain_count,
                },
                indent=2,
            ),
            file=sys.stderr,
        )
        return 0 if result.passed else 1
    except Exception as e:
        print(f"Error running scenario: {e}", file=sys.stderr)
        return 1


def run_all_scenarios():
    """Run all 6 mandatory scenarios."""
    try:
        from src.sim import run_all_scenarios as sim_run_all

        results = sim_run_all()

        print("\n=== TrumpProof Scenario Results ===", file=sys.stderr)
        all_passed = True
        for name, result in results.items():
            status = "✓ PASS" if result.passed else "✗ FAIL"
            print(f"{status}: {name} - {result.message}", file=sys.stderr)
            if not result.passed:
                all_passed = False

        print(
            f"\n{'=== ALL SCENARIOS PASSED ===' if all_passed else '=== SOME SCENARIOS FAILED ==='}",
            file=sys.stderr,
        )
        return 0 if all_passed else 1
    except Exception as e:
        print(f"Error running scenarios: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
