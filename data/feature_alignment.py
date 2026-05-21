#!/usr/bin/env python3
"""
Generate a PaySim-to-Elliptic feature alignment report.
"""

import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
if str(DATA_DIR) not in sys.path:
    sys.path.append(str(DATA_DIR))

from paysim_adapter import paysim_feature_coverage  # noqa: E402


def main() -> None:
    report = paysim_feature_coverage()
    output_path = DATA_DIR / "feature_alignment_report.json"
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print("\n" + "=" * 60)
    print("FEATURE ALIGNMENT REPORT")
    print("=" * 60)
    print(json.dumps(report, indent=2))
    print(f"\n✓ Saved report to {output_path}")


if __name__ == "__main__":
    main()
