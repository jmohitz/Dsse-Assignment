import os
import glob
import csv

results = []

# Dynamically find all WCA and Limbo output folders
for folder in sorted(glob.glob("output_*/*_*")):
    if folder.startswith("output_arc/") or folder.startswith(f"output_arc{os.sep}"):
        continue
    if os.path.isdir(folder):
        folder_name = os.path.basename(folder)
        parts = folder_name.split('_')
        if len(parts) >= 2:
            algo = parts[0].upper()  # Extracts "WCA" or "LIMBO"
            k_val = parts[1]         # Extracts the threshold value
            
            label = f"{algo}_k={k_val}"
            pattern = f"{folder}/*.rsf"
            results.append((label, algo, k_val, pattern))

acdc_dir = "output_acdc/acdc"
if os.path.exists(acdc_dir):
    results.append(("ACDC", "ACDC", "N/A", f"{acdc_dir}/*.rsf"))

# --- SETUP DIRECTORIES & CSV ---
os.makedirs("cluster_details", exist_ok=True)
# Open a CSV file for writing the summary stats
with open('clustering_summary.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    # Write the CSV Header
    writer.writerow(['Algorithm', 'K-Value', 'Actual Clusters', 'Total Classes', 'Min Size', 'Median Size', 'Max Size', 'Distribution'])

    print("Analyzing clusters and generating reports...")

    # Loop through all dynamically found results
    for label, algo, k_val, pattern in results:
        files = glob.glob(pattern) if "*" in pattern else ([pattern] if os.path.exists(pattern) else [])
        if not files:
            print(f"Skipping {label}: No output found")
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
            total = sum(sizes) if sizes else 0

            # 1. WRITE TO SUMMARY CSV
            if sizes:
                min_sz = min(sizes)
                med_sz = sizes[len(sizes)//2]
                max_sz = max(sizes)
            else:
                min_sz = med_sz = max_sz = 0

            writer.writerow([algo, k_val, len(clusters), total, min_sz, med_sz, max_sz, str(sizes)])

            # 2. WRITE TO INDIVIDUAL DETAIL TEXT FILE
            detail_filename = f"cluster_details/{label}_details.txt"
            with open(detail_filename, "w") as detail_file:
                detail_file.write(f"--- {label} ---\n")
                detail_file.write(f"File: {os.path.basename(f)}\n")
                detail_file.write(f"Actual Clusters: {len(clusters)}\n")
                detail_file.write(f"Total Classes: {total}\n")
                detail_file.write(f"Size distribution: {sizes}\n\n")
                detail_file.write("--- CLUSTER CONTENTS ---\n\n")
                
                for name in sorted(clusters):
                    members = clusters[name]
                    detail_file.write(f"{name} ({len(members)} classes):\n")
                    for c in sorted(members):
                        detail_file.write(f"  - {c}\n")
                    detail_file.write("\n")

print("Stored high level information for each clustering result in .csv and in-depth information in cluster_details folder")