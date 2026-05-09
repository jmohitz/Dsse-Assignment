import subprocess, os, shutil
 
arcade_tools = "arcade_tools"
rsf = "filtered_rsf.rsf"
 

wca_runs_1 = [
    ("WCA", "UEMNM", 10),
    ("WCA", "UEMNM", 20),
    ("WCA", "UEMNM", 60),
    
]

wca_runs_2 = [
    ("WCA", "UEMNM", 4),
    ("WCA", "UEMNM", 9),
    ("WCA", "UEMNM", 15),
    
]
limbo_runs = [
    ("LIMBO", "IL", 4),
    ("LIMBO", "IL", 9),
    ("LIMBO", "IL", 15),
]

for algo, measure, k in wca_runs_1:
    out = f"output_{algo.lower()}_{k}"
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    print(f"Clustering for {algo}, k={k}, measure = {measure} with stopping criterion as ARCHSIZEFRACTION")
    subprocess.run([
        "java", "-Xmx4096m", "-jar", f"{arcade_tools}/arcade_core_clusterer.jar",
        f"algo={algo}", "language=java", f"deps={rsf}",
        f"measure={measure}", "projname=tikadp", "projversion=v1",
        f"projpath={out}", "stop=ARCHSIZEFRACTION", f"stopthreshold={k}", "serial=ARCHSIZE", f"serialthreshold={k}"
    ], check=True)
    print(f"Clustering completed. Output store in : {out}/")


for algo, measure, k in wca_runs_2:
    out = f"output_{algo.lower()}_{k}"
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    print(f"Clustering for {algo}, k={k}, measure = {measure} with stopping criterion as PRESELECTED. File level = false")
    subprocess.run([
        "java", "-Xmx4096m", "-jar", f"{arcade_tools}/arcade_core_clusterer.jar",
        f"algo={algo}", "language=java", f"deps={rsf}",
        f"measure={measure}", "projname=tikadp", "projversion=v1",
        f"projpath={out}", "stop=ARCHSIZEFRACTION", f"stopthreshold={k}", "serial=ARCHSIZE", f"serialthreshold={k}",
        "filelevel=false", "packageprefix=org.apache.tika"
    ], check=True)
    print(f"Clustering completed. Output store in : {out}/")


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