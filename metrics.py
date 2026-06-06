import subprocess
import os
import csv

arcade_tools = "arcade_tools"
acdc_rsf = "output_acdc/acdc/tika_detect_parser_acdc.rsf"

# Set up the CSV file for clean, tabular data
csv_filename = "metrics_summary.csv"
with open(csv_filename, "w", newline='') as csvfile:
    writer = csv.writer(csvfile)
    # Write the header row
    writer.writerow(["Algorithm 1", "Algorithm 2", "K-Value", "A2A Score", "CVG (1 -> 2)", "CVG (2 -> 1)"])

    print(f"Calculating metrics across all threshold values (Saving to {csv_filename})...")

    # Loop through k=2 to 50 (k=1 is skipped as it is just one giant cluster)
    for k in range(2, 51):
        wca_rsf = f"output_wca/wca_{k}/tikadp-v1_UEMNM_{k}_clusters.rsf"
        limbo_rsf = f"output_limbo/limbo_{k}/tikadp-v1_IL_{k}_clusters.rsf"

        # Define the 3 comparisons we want to make for every K-value
        comparisons = [
            ("WCA", "Limbo", wca_rsf, limbo_rsf),
            ("WCA", "ACDC", wca_rsf, acdc_rsf),
            ("Limbo", "ACDC", limbo_rsf, acdc_rsf)
        ]

        for algo1_name, algo2_name, rsf1, rsf2 in comparisons:
            # Skip if any of the RSF files failed to generate
            if not os.path.exists(rsf1) or not os.path.exists(rsf2):
                continue
            
            # --- CALCULATE A2A ---
            a2a_run = subprocess.run(
                ["java", "-jar", f"{arcade_tools}/arcade_core_A2a.jar", rsf1, rsf2],
                capture_output=True, text=True
            )
            a2a_score = a2a_run.stdout.strip()

            # --- CALCULATE CVG ---
            cvg_run = subprocess.run(
                ["java", "-jar", f"{arcade_tools}/arcade_core_Cvg.jar", rsf1, rsf2],
                capture_output=True, text=True
            )
            
            # Parse the CVG output to extract the actual numbers
            # (CVG outputs two lines: Coverage from 1 to 2, and Coverage from 2 to 1)
            cvg_output = cvg_run.stdout.strip().split('\n')
            cvg_1_to_2 = "N/A"
            cvg_2_to_1 = "N/A"
            
            if len(cvg_output) >= 2:
                # Splits the string at "is" and grabs the number at the end
                cvg_1_to_2 = cvg_output[0].split("is")[-1].strip()
                cvg_2_to_1 = cvg_output[1].split("is")[-1].strip()

            # Write the results to the CSV
            writer.writerow([algo1_name, algo2_name, k, a2a_score, cvg_1_to_2, cvg_2_to_1])

print(f"A2A and CVG metric scores calculated and results stored in {csv_filename}")