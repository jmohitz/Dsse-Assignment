#!/usr/bin/env python3
"""
Sweep alpha and n_clusters for ARC clustering, then compare metrics vs Week 1.

Sweep 1: alpha in {0.0, 0.2, 0.4, 0.6, 0.8, 1.0}  at fixed n_clusters=12
Sweep 2: n_clusters in {4, 8, 12, 16, 20}           at fixed alpha=0.4

Calls arc_clustering.py and arc_metrics.py internally (imports them directly).

Usage:
    python3 arc_sweep.py                     # codebert, full sweep
    python3 arc_sweep.py --model nomic       # use nomic-embed-code
    python3 arc_sweep.py --alpha-only        # only alpha sweep
    python3 arc_sweep.py --k-only            # only k sweep
    python3 arc_sweep.py --force             # recompute even if RSF exists
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------------------

ALPHA_SWEEP = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
K_SWEEP     = [4, 8, 12, 16, 20]
FIXED_K     = 12
FIXED_ALPHA = 0.4

WORKTREE = Path(__file__).resolve().parent


def parse_args():
    p = argparse.ArgumentParser(description="ARC alpha/k sweep + metrics comparison")
    p.add_argument("--model",      choices=["codebert", "nomic"], default="codebert")
    p.add_argument("--alpha-only", action="store_true",  help="Run only alpha sweep")
    p.add_argument("--k-only",     action="store_true",  help="Run only k sweep")
    p.add_argument("--force",      action="store_true",  help="Recompute existing RSF files")
    return p.parse_args()


# ---------------------------------------------------------------------------
# Cluster-size stats (computed from RSF without re-running clustering)
# ---------------------------------------------------------------------------

def rsf_stats(rsf_path: Path) -> dict:
    if not rsf_path.exists():
        return {"error": "missing"}
    sizes: Counter = Counter()
    with open(rsf_path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 3 and parts[0] == "contain":
                sizes[parts[1]] += 1
    if not sizes:
        return {"error": "empty"}
    sv = sorted(sizes.values(), reverse=True)
    return {
        "n_clusters": len(sizes),
        "total":      sum(sv),
        "min":        min(sv),
        "median":     sv[len(sv) // 2],
        "max":        max(sv),
        "sizes":      sv,
    }


# ---------------------------------------------------------------------------
# Summary table helpers
# ---------------------------------------------------------------------------

def print_header(title: str) -> None:
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}")


def print_table(rows: list[dict]) -> None:
    hdr = (
        f"{'Config':25s}  {'k':>3}  {'min':>4}  {'med':>4}  {'max':>4}  "
        f"{'A2A/WCA':>10}  {'A2A/Limbo':>10}  {'A2A/ACDC':>10}"
    )
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        stats = r.get("stats", {})
        mets  = r.get("metrics", {})

        def _a2a(name):
            for m in mets:
                if m.get("baseline") == name:
                    return m.get("a2a", "N/A")
            return "N/A"

        print(
            f"{r['label']:25s}  "
            f"{stats.get('n_clusters','?'):>3}  "
            f"{stats.get('min','?'):>4}  "
            f"{stats.get('median','?'):>4}  "
            f"{stats.get('max','?'):>4}  "
            f"{_a2a('WCA k=4'):>10}  "
            f"{_a2a('Limbo k=4'):>10}  "
            f"{_a2a('ACDC'):>10}"
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    # Import our sibling scripts
    sys.path.insert(0, str(WORKTREE))
    import arc_clustering
    import arc_metrics

    run_alpha = not args.k_only
    run_k     = not args.alpha_only

    all_rows: list[dict] = []

    # ------------------------------------------------------------------
    # Sweep 1: alpha at fixed k=12
    # ------------------------------------------------------------------
    if run_alpha:
        print_header(f"Alpha sweep  (n_clusters={FIXED_K}, model={args.model})")
        alpha_rows = []
        for alpha in ALPHA_SWEEP:
            label = f"alpha={alpha:.1f} k={FIXED_K}"
            print(f"\n>>> {label}")
            rsf = arc_clustering.run(alpha, FIXED_K, args.model, args.force)
            stats = rsf_stats(rsf)
            mets  = arc_metrics.run(rsf, label)
            alpha_rows.append({"label": label, "stats": stats, "metrics": mets})

        print_header("Alpha sweep summary")
        print_table(alpha_rows)
        all_rows.extend(alpha_rows)

    # ------------------------------------------------------------------
    # Sweep 2: k at fixed alpha=0.4
    # ------------------------------------------------------------------
    if run_k:
        print_header(f"k sweep  (alpha={FIXED_ALPHA}, model={args.model})")
        k_rows = []
        for k in K_SWEEP:
            if run_alpha and k == FIXED_K:
                # already computed — reuse
                rsf = WORKTREE / f"output_arc_{FIXED_ALPHA}_{k}" / f"tikadp-v1_ARC_{k}_clusters.rsf"
                label = f"alpha={FIXED_ALPHA:.1f} k={k}"
                stats = rsf_stats(rsf)
                mets  = arc_metrics.run(rsf, label)
            else:
                label = f"alpha={FIXED_ALPHA:.1f} k={k}"
                print(f"\n>>> {label}")
                rsf = arc_clustering.run(FIXED_ALPHA, k, args.model, args.force)
                stats = rsf_stats(rsf)
                mets  = arc_metrics.run(rsf, label)
            k_rows.append({"label": label, "stats": stats, "metrics": mets})

        print_header("k sweep summary")
        print_table(k_rows)
        all_rows.extend(k_rows)

    # ------------------------------------------------------------------
    # Size distributions in detail
    # ------------------------------------------------------------------
    print_header("Cluster size distributions (all configs)")
    for r in all_rows:
        s = r.get("stats", {})
        if "error" not in s:
            print(f"  {r['label']:30s}: {s.get('sizes', [])}")

    print("\nSweep complete.")


if __name__ == "__main__":
    main()
