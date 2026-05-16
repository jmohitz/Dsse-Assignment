#!/usr/bin/env python3
"""
Compare ARC cluster RSF files against Week 1 baselines (WCA k=4, Limbo k=4, ACDC)
using arcade_core_A2a.jar and arcade_core_Cvg.jar.

Appends results under a labeled section in metrics_results.txt.

Usage:
    python3 arc_metrics.py --arc-rsf output_arc_0.4_12/tikadp-v1_ARC_12_clusters.rsf
    python3 arc_metrics.py --arc-rsf <path> --label "Week 3 alpha=0.4 k=12"
    python3 arc_metrics.py --arc-rsf <path> --out custom_results.txt
"""

import argparse
import os
import subprocess
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
WORKTREE      = Path(__file__).resolve().parent
PROJECT_ROOT  = Path(os.environ.get("DSSE_ROOT", WORKTREE.parent.parent.parent))
ARCADE_TOOLS  = Path(os.environ.get("ARCADE_TOOLS", PROJECT_ROOT / "arcade_tools"))
WEEK1_BASE    = Path(os.environ.get("WEEK1_BASE",   PROJECT_ROOT / "arcade_tika"))

A2A_JAR = ARCADE_TOOLS / "arcade_core_A2a.jar"
CVG_JAR = ARCADE_TOOLS / "arcade_core_Cvg.jar"

WCA_K4_RSF   = WEEK1_BASE / "output_wca_4"    / "tikadp-v1_UEMNM_4_clusters.rsf"
LIMBO_K4_RSF = WEEK1_BASE / "output_limbo_4"  / "tikadp-v1_IL_4_clusters.rsf"
# ACDC was regenerated into output_acdc/ after the pull removed tika_detect_parser_acdc.rsf
ACDC_RSF     = WEEK1_BASE / "output_acdc"     / "tika_detect_parser_acdc.rsf"

DEFAULT_OUT = WORKTREE / "metrics_results.txt"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="A2A / CVG comparison for ARC RSF vs Week 1")
    p.add_argument("--arc-rsf", required=True, help="Path to ARC RSF file")
    p.add_argument("--label",   default=None,  help="Section header label")
    p.add_argument("--out",     default=str(DEFAULT_OUT), help="Output file (appended)")
    return p.parse_args()


def run_a2a(rsf1: Path, rsf2: Path) -> str:
    result = subprocess.run(
        ["java", "-jar", str(A2A_JAR), str(rsf1), str(rsf2)],
        capture_output=True, text=True
    )
    return result.stdout.strip() or result.stderr.strip()


def run_cvg(rsf1: Path, rsf2: Path) -> tuple[str, str]:
    result = subprocess.run(
        ["java", "-jar", str(CVG_JAR), str(rsf1), str(rsf2)],
        capture_output=True, text=True
    )
    lines = result.stdout.strip().split("\n")
    cvg_1_to_2 = lines[0].split("is")[-1].strip() if len(lines) >= 1 else "N/A"
    cvg_2_to_1 = lines[1].split("is")[-1].strip() if len(lines) >= 2 else "N/A"
    return cvg_1_to_2, cvg_2_to_1


def compare(arc_rsf: Path, baseline_rsf: Path, baseline_name: str) -> dict:
    if not baseline_rsf.exists():
        return {"baseline": baseline_name, "error": f"NOT FOUND: {baseline_rsf}"}

    a2a = run_a2a(arc_rsf, baseline_rsf)
    cvg_12, cvg_21 = run_cvg(arc_rsf, baseline_rsf)
    return {
        "baseline":   baseline_name,
        "a2a":        a2a,
        "cvg_arc_to_base": cvg_12,
        "cvg_base_to_arc": cvg_21,
    }


def format_row(row: dict) -> str:
    if "error" in row:
        return f"  vs {row['baseline']:20s}  ERROR: {row['error']}"
    return (
        f"  vs {row['baseline']:20s}  "
        f"A2A={row['a2a']:8s}  "
        f"CVG(ARC→base)={row['cvg_arc_to_base']:8s}  "
        f"CVG(base→ARC)={row['cvg_base_to_arc']:8s}"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(arc_rsf: Path, label: str | None = None, out_file: Path = DEFAULT_OUT) -> list[dict]:
    arc_rsf = arc_rsf.resolve()
    if not arc_rsf.exists():
        raise FileNotFoundError(f"ARC RSF not found: {arc_rsf}")
    for jar in (A2A_JAR, CVG_JAR):
        if not jar.exists():
            raise FileNotFoundError(f"ARCADE JAR not found: {jar}")

    if label is None:
        label = arc_rsf.parent.name

    baselines = [
        (WCA_K4_RSF,   "WCA k=4"),
        (LIMBO_K4_RSF, "Limbo k=4"),
        (ACDC_RSF,     "ACDC"),
    ]

    results = []
    print(f"\n{'='*60}")
    print(f"Metrics for: {arc_rsf.name}")
    print(f"{'='*60}")
    for baseline_path, baseline_name in baselines:
        print(f"  Running vs {baseline_name} …", end=" ", flush=True)
        row = compare(arc_rsf, baseline_path, baseline_name)
        results.append(row)
        print(format_row(row).strip())

    # Append to output file
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(out_file, "a") as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Week 3 ARC Metrics  |  {label}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"RSF: {arc_rsf}\n")
        f.write(f"{'='*60}\n")
        for row in results:
            f.write(format_row(row) + "\n")
        f.write("\n")

    print(f"\nAppended to: {out_file}")
    return results


if __name__ == "__main__":
    args = parse_args()
    run(Path(args.arc_rsf), args.label, Path(args.out))
