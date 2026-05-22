import subprocess, os, shutil

arcade_tools = "arcade_tools"
rsf = "filtered_rsf.rsf"

wca_runs = [("WCA", "UEMNM", k) for k in range(2, 51)]
limbo_runs = [("LIMBO", "IL", k) for k in range(2, 51)]

for algo, measure, k in wca_runs:
    out = f"output_{algo.lower()}_{k}"
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    print(f"Clustering for {algo}, k={k}, measure = {measure} with stopping criterion as PRESELECTED.")
    subprocess.run([
        "java", "-Xmx4096m", "-jar", f"{arcade_tools}/arcade_core_clusterer.jar",
        f"algo={algo}", "language=java", f"deps={rsf}",
        f"measure={measure}", "projname=tikadp", "projversion=v1",
        f"projpath={out}", "stop=PRESELECTED", f"stopthreshold={k}", "serial=ARCHSIZE", f"serialthreshold={k}"
    ], check=True)
    print(f"Clustering completed. Output stored in : {out}/")


for algo, measure, k in limbo_runs:
    out = f"output_{algo.lower()}_{k}"
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    print(f"Clustering for {algo}, k={k}, measure = {measure} with stopping criterion as PRESELECTED")
    subprocess.run([
        "java", "-Xmx4096m", "-jar", f"{arcade_tools}/arcade_core_clusterer.jar",
        f"algo={algo}", "language=java", f"deps={rsf}",
        f"measure={measure}", "projname=tikadp", "projversion=v1",
        f"projpath={out}", "stop=PRESELECTED", f"stopthreshold={k}", "serial=ARCHSIZE", f"serialthreshold={k}"
    ], check=True)
    print(f"Clustering completed. Output stored in : {out}/")


# ACDC (separate jar, different syntax)
print("Clustering for ACDC")
acdc_out = "acdc/tika_detect_parser_acdc.rsf"
if os.path.exists("acdc"):
    shutil.rmtree("acdc")
os.makedirs("acdc")
subprocess.run([
    "java", "-jar", f"{arcade_tools}/arcade_core-ACDC.jar",
    rsf, acdc_out
], check=True)
print(f"Clustering completed. Output stored in : {acdc_out}")

print("All Clustering Algorithms completed")