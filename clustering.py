import subprocess, os, shutil
 
arcade_tools = "arcade_tools"
rsf = "filtered_rsf.rsf"
 
runs = [
    ("WCA", "UEMNM", 4),
    ("WCA", "UEMNM", 9),
    ("WCA", "UEMNM", 15),
    ("LIMBO", "IL", 4),
    ("LIMBO", "IL", 9),
    ("LIMBO", "IL", 15),
]

for algo, measure, k in runs:
    out = f"output_{algo.lower()}_{k}"
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    print(f"Clustering for {algo}, k={k}, measure = {measure}")
    subprocess.run([
        "java", "-Xmx4096m", "-jar", f"{arcade_tools}/arcade_core_clusterer.jar",
        f"algo={algo}", "language=java", f"deps={rsf}",
        f"measure={measure}", "projname=tikadp", "projversion=v1",
        f"projpath={out}", "stop=PRESELECTED", f"stopthreshold={k}", "serial=ARCHSIZE", f"serialthreshold={k}"
    ], check=True)
    print(f"Clustering completed. Output store in : {out}/")
 
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
print(f" Clustering completed. Output store in : {acdc_out}/")
 
print("All Clustering Algorithms completed")