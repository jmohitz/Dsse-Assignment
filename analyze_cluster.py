import os, glob
from collections import Counter
import sys

sys.stdout = open("cluster_results.txt", "w")
results = [
    ("WCA k=4", f"output_wca_4/*.rsf"),
    ("WCA k=9", f"output_wca_9/*.rsf"),
    ("WCA k=15", f"output_wca_15/*.rsf"),
    ("LIMBO k=4", f"output_limbo_4/*.rsf"),
    ("LIMBO k=9", f"output_limbo_9/*.rsf"),
    ("LIMBO k=15",f"output_limbo_15/*.rsf"),
    ("ACDC", f"acdc/*.rsf"),
]

for label, pattern in results:
    files = glob.glob(pattern) if "*" in pattern else ([pattern] if os.path.exists(pattern) else [])
    if not files:
        print()
        print("--- " + label + ": No output found ---")
        continue

    for f in files:
        clusters = {}
        for line in open(f):
            parts = line.split()
            if len(parts) >= 3 and parts[0] == "contain":
                cluster = parts[1]
                if cluster not in clusters:
                    clusters[cluster] = []
                clusters[cluster].append(parts[2])

        sizes = sorted([len(v) for v in clusters.values()], reverse=True)
        total = sum(sizes)

        # Summary stats
        print()
        print("--- " + label + " ---")
        print("  File: " + os.path.basename(f))
        print("  Clusters: " + str(len(clusters)))
        print("  Total classes: " + str(total))
        print("  Cluster sizes: min=" + str(min(sizes)) + ", median=" + str(sizes[len(sizes)//2]) + ", max=" + str(max(sizes)))
        print("  Size distribution: " + str(sizes))

        # Full cluster details
        print()
        for name in sorted(clusters):
            members = clusters[name]
            print("  " + name + " (" + str(len(members)) + " classes)")
            for c in sorted(members):
                print("    - " + c)
            print()

sys.stdout.close()
sys.stdout = sys.__stdout__
print("Results saved to cluster_results.txt")