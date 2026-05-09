import os
import glob
from collections import Counter
import sys

# Redirect standard output to a file
sys.stdout = open("cluster_results.txt", "w")

results = []

# Dynamically find all WCA and Limbo output folders
# Looks for folders like "output_wca_0.1", "output_limbo_15", etc.
for folder in sorted(glob.glob("output_*_*")):
    if os.path.isdir(folder):
        parts = folder.split('_')
        if len(parts) >= 3:
            algo = parts[1].upper()  # Extracts "WCA" or "LIMBO"
            k_val = parts[2]         # Extracts the threshold value
            
            label = f"{algo} k={k_val}"
            pattern = f"{folder}/*.rsf"
            results.append((label, pattern))

# Add ACDC explicitly if the folder exists in your directory
if os.path.exists("acdc"):
    results.append(("ACDC", "acdc/*.rsf"))

# Loop through all dynamically found results
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
            # Look for lines that establish a class belongs to a cluster
            if len(parts) >= 3 and parts[0] == "contain":
                cluster = parts[1]
                if cluster not in clusters:
                    clusters[cluster] = []
                clusters[cluster].append(parts[2])

        sizes = sorted([len(v) for v in clusters.values()], reverse=True)
        total = sum(sizes) if sizes else 0

        # Summary stats
        print()
        print("--- " + label + " ---")
        print("  File: " + os.path.basename(f))
        print("  Clusters: " + str(len(clusters)))
        print("  Total classes: " + str(total))
        
        # Protect against empty cluster edge cases to avoid index errors
        if sizes:
            print("  Cluster sizes: min=" + str(min(sizes)) + ", median=" + str(sizes[len(sizes)//2]) + ", max=" + str(max(sizes)))
            print("  Size distribution: " + str(sizes))
        else:
             print("  Cluster sizes: N/A (Empty)")

        # Full cluster details
        print()
        for name in sorted(clusters):
            members = clusters[name]
            print("  " + name + " (" + str(len(members)) + " classes)")
            for c in sorted(members):
                print("    - " + c)
            print()

# Safely close the file and restore terminal output
sys.stdout.close()
sys.stdout = sys.__stdout__
print("Results saved to cluster_results.txt")