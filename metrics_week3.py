import subprocess
import os
import csv
from pathlib import Path

# Paths to your tools and static ACDC file
arcade_tools = Path("arcade_tools")
acdc_rsf = Path("output_acdc/acdc/tika_detect_parser_acdc.rsf")

# Set up the CSV file with the new 'Alpha' column
csv_filename = "metrics_week3_summary.csv"

def get_metrics(rsf1, rsf2):
    """Helper function to run the java commands and parse the output."""
    if not os.path.exists(rsf1) or not os.path.exists(rsf2):
        return "N/A", "N/A", "N/A"
    
    # --- CALCULATE A2A ---
    a2a_score = "Error"
    try:
        a2a_run = subprocess.run(
            ["java", "-jar", str(arcade_tools / "arcade_core_A2a.jar"), str(rsf1), str(rsf2)],
            capture_output=True, text=True
        )
        a2a_score = a2a_run.stdout.strip()
    except Exception as e:
        pass

    # --- CALCULATE CVG ---
    cvg_1_to_2 = "N/A"
    cvg_2_to_1 = "N/A"
    try:
        cvg_run = subprocess.run(
            ["java", "-jar", str(arcade_tools / "arcade_core_Cvg.jar"), str(rsf1), str(rsf2)],
            capture_output=True, text=True
        )
        cvg_output = cvg_run.stdout.strip().split('\n')
        if len(cvg_output) >= 2:
            cvg_1_to_2 = cvg_output[0].split("is")[-1].strip()
            cvg_2_to_1 = cvg_output[1].split("is")[-1].strip()
    except Exception as e:
        pass

    return a2a_score, cvg_1_to_2, cvg_2_to_1


if __name__ == "__main__":
    print(f"Calculating metrics... (Saving to {csv_filename})")

    with open(csv_filename, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Added the 'Alpha' column
        writer.writerow(["Algorithm 1", "Algorithm 2", "Alpha", "K-Value", "A2A Score", "CVG (1 -> 2)", "CVG (2 -> 1)"])

        for k in range(2, 51):
            wca_rsf = Path(f"output_wca/wca_{k}/tikadp-v1_UEMNM_{k}_clusters.rsf")
            limbo_rsf = Path(f"output_limbo/limbo_{k}/tikadp-v1_IL_{k}_clusters.rsf")
            
            # 1. Baseline Comparisons (No Alpha)
            baselines = [
                ("WCA", "Limbo", wca_rsf, limbo_rsf),
                ("WCA", "ACDC", wca_rsf, acdc_rsf),
                ("Limbo", "ACDC", limbo_rsf, acdc_rsf)
            ]
            
            for alg1, alg2, p1, p2 in baselines:
                a2a, cvg1, cvg2 = get_metrics(p1, p2)
                if a2a != "N/A":
                    writer.writerow([alg1, alg2, "N/A", k, a2a, cvg1, cvg2])

            # 2. ARC Comparisons (Loops through the 4 Alpha values)
            for alpha in [0.2, 0.4, 0.6, 0.8]:
                # Dynamic path matching your new nested folder structure
                arc_rsf = Path(f"output_arc/alpha_{alpha}/arc_{k}/tikadp-v1_ARC_{k}_clusters.rsf")
                
                arc_comps = [
                    ("ARC", "WCA", arc_rsf, wca_rsf),
                    ("ARC", "Limbo", arc_rsf, limbo_rsf),
                    ("ARC", "ACDC", arc_rsf, acdc_rsf)
                ]
                
                for alg1, alg2, p1, p2 in arc_comps:
                    a2a, cvg1, cvg2 = get_metrics(p1, p2)
                    if a2a != "N/A":
                        writer.writerow([alg1, alg2, alpha, k, a2a, cvg1, cvg2])

    print(f"\nSUCCESS: A2A and CVG metrics calculated and stored in {csv_filename}")