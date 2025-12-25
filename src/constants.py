"""TrumpProof Constants

All verified dollar exposures and thresholds.
No receipt → not real. These are the documented numbers.
"""

# === TENANT ===
TENANT_ID = "trumpproof"

# === DOLLAR EXPOSURES (verified) ===
TARIFF_FY2025_REVENUE = 195_000_000_000        # $195B
TARIFF_REFUND_LIABILITY = 90_000_000_000       # $90B
BORDER_FOUR_YEAR_ALLOCATION = 170_100_000_000  # $170.1B
BORDER_ICE_FY2025 = 28_700_000_000             # $28.7B
GULF_PIF_INVESTMENT = 2_000_000_000            # $2B
GULF_AFFINITY_AUM = 5_400_000_000              # $5.4B
GULF_FEES_COLLECTED = 157_000_000              # $157M
GOLF_ANNUAL_REVENUE = 354_000_000              # $354M
GOLF_LIV_PIF_INVESTMENT = 4_580_000_000        # $4.58B
LICENSE_ANNUAL_REVENUE = 36_000_000            # $36M

# === THRESHOLDS ===
FAVORITISM_THRESHOLD = 0.15        # 15% deviation from baseline approval rate
OPACITY_CRITICAL = 0.80            # 80% opacity score = critical
FEE_TO_RETURNS_EXCESSIVE = 10.0    # 10:1 fee-to-returns ratio = excessive
EMOLUMENTS_DISCLOSURE_THRESHOLD = 10_000  # $10K disclosure threshold

# === TIMING ===
LOOP_CYCLE_SECONDS = 60
HARVEST_PERIOD_DAYS = 30

# === MODULE PRIORITY (by genuine value) ===
MODULE_PRIORITY = [
    "border",     # HIGHEST: life-safety, constitutional verification
    "tariff",     # HIGH: policy outcome verification, $90B liability
    "gulf",       # Medium: disclosure enforcement
    "golf",       # Medium: emoluments verification
    "license",    # LOW: CTA infrastructure destroyed
]

# === TOTAL EXPOSURE ===
TOTAL_EXPOSURE = (
    TARIFF_FY2025_REVENUE +
    BORDER_FOUR_YEAR_ALLOCATION +
    GULF_AFFINITY_AUM +
    GOLF_ANNUAL_REVENUE +
    LICENSE_ANNUAL_REVENUE
)  # $371B+

# === SAUDI PIF TOTAL EXPOSURE ===
PIF_TOTAL_EXPOSURE = (
    GULF_PIF_INVESTMENT +      # $2B to Kushner
    GOLF_LIV_PIF_INVESTMENT    # $4.58B to LIV Golf
)  # $6.58B+ documented
