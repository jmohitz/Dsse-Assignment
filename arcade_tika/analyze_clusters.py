#!/usr/bin/env python3
"""
Analyze all ARCADE clustering outputs.
Reads RSF files from output directories, counts clusters and sizes.
"""
import os
import glob
from collections import Counter

BASE = "/Users/mohit/Documents/DSSE-Week-1/arcade_tika"

def analyze_rsf(filepath):
    """Analyze a clustering RSF file and return stats."""
    clusters = Counter()
    classes = []
    with open(filepath, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3 and parts[0] == 'contain':
                cluster_id = parts[1]
                class_name = parts[2]
                clusters[cluster_id] += 1
                classes.append(class_name)
    
    sizes = sorted(clusters.values(), reverse=True)
    n_clusters = len(clusters)
    total_classes = len(classes)
    min_size = min(sizes) if sizes else 0
    max_size = max(sizes) if sizes else 0
    median_idx = len(sizes) // 2
    median_size = sizes[median_idx] if sizes else 0
    
    return {
        'file': filepath,
        'n_clusters': n_clusters,
        'total_classes': total_classes,
        'min_size': min_size,
        'max_size': max_size,
        'median_size': median_size,
        'sizes': sizes,
        'cluster_ids': dict(clusters)
    }

def main():
    # Find all RSF outputs
    patterns = [
        ("WCA k=9 (UEM)", os.path.join(BASE, "output_wca", "*.rsf")),
        ("WCA k=9 (UEMNM)", os.path.join(BASE, "output_wca_9", "*.rsf")),
        ("WCA k=4 (UEMNM)", os.path.join(BASE, "output_wca_4", "*.rsf")),
        ("WCA k=15 (UEMNM)", os.path.join(BASE, "output_wca_15", "*.rsf")),
        ("LIMBO k=4", os.path.join(BASE, "output_limbo_4", "*.rsf")),
        ("LIMBO k=9", os.path.join(BASE, "output_limbo_9", "*.rsf")),
        ("LIMBO k=15", os.path.join(BASE, "output_limbo_15", "*.rsf")),
        ("ACDC", os.path.join(BASE, "tika_detect_parser_acdc.rsf")),
    ]
    
    # Also check final outputs
    final_files = [
        ("FINAL WCA", os.path.join(BASE, "tika_detect_parser_wca.rsf")),
        ("FINAL LIMBO", os.path.join(BASE, "tika_detect_parser_limbo.rsf")),
        ("FINAL ACDC", os.path.join(BASE, "tika_detect_parser_acdc.rsf")),
    ]
    
    print("=" * 70)
    print("ARCADE Clustering Analysis Results")
    print("=" * 70)
    
    for label, pattern in patterns:
        files = glob.glob(pattern) if "*" in pattern else ([pattern] if os.path.exists(pattern) else [])
        if not files:
            print(f"\n--- {label}: No output found ---")
            continue
        for f in files:
            stats = analyze_rsf(f)
            print(f"\n--- {label} ---")
            print(f"  File: {os.path.basename(f)}")
            print(f"  Clusters: {stats['n_clusters']}")
            print(f"  Total classes: {stats['total_classes']}")
            print(f"  Cluster sizes: min={stats['min_size']}, median={stats['median_size']}, max={stats['max_size']}")
            print(f"  Size distribution: {stats['sizes']}")
    
    print("\n" + "=" * 70)
    print("Final Deliverable Files:")
    print("=" * 70)
    for label, path in final_files:
        if os.path.exists(path):
            stats = analyze_rsf(path)
            print(f"  {label}: {stats['n_clusters']} clusters, {stats['total_classes']} classes")
        else:
            print(f"  {label}: NOT FOUND at {path}")

if __name__ == "__main__":
    main()
