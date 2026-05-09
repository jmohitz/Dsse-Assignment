import subprocess
import os
import sys

sys.stdout = open("metrics_results.txt", "w")

arcade_tools = "arcade_tools"

wca_4 = "output_wca_4/tikadp-v1_UEMNM_4_clusters.rsf"
wca_9 = "output_wca_9/tikadp-v1_UEMNM_9_clusters.rsf"
wca_15 = "output_wca_15/tikadp-v1_UEMNM_15_clusters.rsf"

limbo_4 = "output_limbo_4/tikadp-v1_IL_4_clusters.rsf"
limbo_9 = "output_limbo_9/tikadp-v1_IL_9_clusters.rsf"
limbo_15 = "output_limbo_15/tikadp-v1_IL_15_clusters.rsf"

acdc = "acdc/tika_detect_parser_acdc.rsf"

comparisons = [
    ("WCA 9 vs Limbo 9", wca_9, limbo_9),
    ("WCA 4 vs Limbo 4", wca_4, limbo_4),
    ("WCA 15 vs Limbo 15", wca_15, limbo_15),
    ("WCA 4 vs ACDC", wca_4, acdc),
    ("Limbo 4 vs ACDC", limbo_4, acdc)
]

print("Calculating metrics a2a and cvg")

for compare, algo1, algo2 in comparisons:
    if not os.path.exists(algo1) or not os.path.exists(algo2):
        print(f"Skipping {compare}: Missing one or both RSF files.")
        continue
    
    print(f"Comparing:  {compare}")

    a2a = subprocess.run(
        ["java", "-jar", f"{arcade_tools}/arcade_core_A2a.jar", algo1, algo2],
        capture_output=True, text=True
    )

    print(f"A2A comparison: {a2a.stdout.strip()}")

    cvg = subprocess.run(
        ["java", "-jar", f"{arcade_tools}/arcade_core_Cvg.jar", algo1, algo2],
        capture_output=True, text=True
    )
    print(f"CVG comparison: {cvg.stdout.strip()}")

sys.stdout.close()
sys.stdout = sys.__stdout__

print("Finding metrics completed. Results stored in : metrics_results.txt")