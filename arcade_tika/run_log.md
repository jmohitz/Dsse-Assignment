# Run Log — ARCADE Architecture Recovery for Apache Tika (Week 1)

All commands executed from `/Users/mohit/Documents/DSSE-Week-1/arcade_tika/`.

---

## Environment

```
java version "26" (build 26+35-2893) — HotSpot 64-bit
Apache Maven 3.9.15
OS: macOS Darwin 25.4.0 (arm64)
```

---

## Step 0 — Setup

**Decision:** Working directory is `arcade_tika/` inside `DSSE-Week-1/`.

Reference files confirmed present:
- `/Users/mohit/Documents/DSSE-Week-1/Arcade documentation.pdf`
- `/Users/mohit/Documents/DSSE-Week-1/Projects_Parts_under_focus.xlsx`

ARCADE tools confirmed present at `/Users/mohit/Documents/DSSE-Week-1/arcade_tools/`:
- `arcade_core_JavaParser.jar` (16 MB)
- `arcade_core_clusterer.jar` (16 MB)
- `arcade_core-ACDC.jar` (16 MB)

---

## Step 1 — Compile Apache Tika

```bash
git clone https://github.com/apache/tika.git
cd tika
mvn -DskipTests package -pl tika-core,tika-parsers/tika-parsers-standard/tika-parsers-standard-package
```

**Result:** `tika-core-4.0.0-SNAPSHOT.jar` produced at:
`tika/tika-core/target/tika-core-4.0.0-SNAPSHOT.jar`

---

## Step 2 — Identify "Detect & Parser" Scope (Group 6)

Opened `Projects_Parts_under_focus.xlsx` → Row for **Apache Tika / Group 6 / Detect & parser**.

**Package prefixes extracted:**
```
org.apache.tika.detect
org.apache.tika.parser
```

Saved to `focus_scope.txt` (one prefix per line).

---

## Step 3 — Generate Master Dependency Graph

```bash
java -jar /Users/mohit/Documents/DSSE-Week-1/arcade_tools/arcade_core_JavaParser.jar \
  /Users/mohit/Documents/DSSE-Week-1/arcade_tika/tika/tika-core/src/main/java \
  /Users/mohit/Documents/DSSE-Week-1/arcade_tika/tika_master.rsf \
  /Users/mohit/Documents/DSSE-Week-1/arcade_tika/tika_master.fv
```

**Output:** `tika_master.rsf` — 1,229 lines (dependency edges), format: `depends SourceClass TargetClass`

---

## Step 4 — Filter to Detect & Parser

```bash
python3 filter_rsf.py tika_master.rsf detect_parser_focus.rsf
```

Script logic: keeps lines where `source` OR `target` starts with `org.apache.tika.detect` or `org.apache.tika.parser`.

**Result:**
- Lines before filtering: 1,229
- Lines after filtering:    553
- Unique classes in detect/parser scope: 79
- Total unique classes in filtered graph: 158

---

## Step 5a — WCA Clustering

Algorithm: **Weighted Combined Algorithm (WCA)**  
Measure: **UEMNM** (Unidirectional Evolutionary Module Neighborhood Measure)  
Clusterer: `arcade_core_clusterer.jar`  

Three target cluster counts tried: k=4, k=9, k=15

### k=4

```bash
java -Xmx4096m -jar /Users/mohit/Documents/DSSE-Week-1/arcade_tools/arcade_core_clusterer.jar \
  algo=WCA language=java deps=detect_parser_focus.rsf measure=UEMNM \
  projname=tikadp projversion=v1 projpath=output_wca_4 \
  stop=PRESELECTED stopthreshold=4 serial=ARCHSIZE serialthreshold=4
```
Output: `output_wca_4/tikadp-v1_UEMNM_4_clusters.rsf`  
Clusters: 4 | Sizes: [155, 1, 1, 1] | min=1, median=1, max=155

### k=9

```bash
java -Xmx4096m -jar /Users/mohit/Documents/DSSE-Week-1/arcade_tools/arcade_core_clusterer.jar \
  algo=WCA language=java deps=detect_parser_focus.rsf measure=UEMNM \
  projname=tikadp projversion=v1 projpath=output_wca_9 \
  stop=PRESELECTED stopthreshold=9 serial=ARCHSIZE serialthreshold=9
```
Output: `output_wca_9/tikadp-v1_UEMNM_9_clusters.rsf`  
Clusters: 9 | Sizes: [150, 1, 1, 1, 1, 1, 1, 1, 1] | min=1, median=1, max=150

### k=15

```bash
java -Xmx4096m -jar /Users/mohit/Documents/DSSE-Week-1/arcade_tools/arcade_core_clusterer.jar \
  algo=WCA language=java deps=detect_parser_focus.rsf measure=UEMNM \
  projname=tikadp projversion=v1 projpath=output_wca_15 \
  stop=PRESELECTED stopthreshold=15 serial=ARCHSIZE serialthreshold=15
```
Output: `output_wca_15/tikadp-v1_UEMNM_15_clusters.rsf`  
Clusters: 15 | Sizes: [144, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1] | min=1, median=1, max=144

**Chosen for final:** k=9 — middle value is the standard choice; all three show the same highly concentrated pattern (one dominant cluster + singletons), which is expected WCA behavior on a strongly hub-centric dependency graph.

```bash
cp output_wca_9/tikadp-v1_UEMNM_9_clusters.rsf tika_detect_parser_wca.rsf
```

---

## Step 5b — LIMBO Clustering

Algorithm: **LIMBO (Scalable Clustering of Software Components)**  
Measure: **IL** (Information Loss)  
Clusterer: `arcade_core_clusterer.jar`

Three target cluster counts tried: k=4, k=9, k=15

### k=4

```bash
java -Xmx4096m -jar /Users/mohit/Documents/DSSE-Week-1/arcade_tools/arcade_core_clusterer.jar \
  algo=LIMBO language=java deps=detect_parser_focus.rsf measure=IL \
  projname=tikadp projversion=v1 projpath=output_limbo_4 \
  stop=PRESELECTED stopthreshold=4 serial=ARCHSIZE serialthreshold=4
```
Output: `output_limbo_4/tikadp-v1_IL_4_clusters.rsf`  
Clusters: 4 | Sizes: [114, 32, 7, 5] | min=5, median=7, max=114

### k=9

```bash
java -Xmx4096m -jar /Users/mohit/Documents/DSSE-Week-1/arcade_tools/arcade_core_clusterer.jar \
  algo=LIMBO language=java deps=detect_parser_focus.rsf measure=IL \
  projname=tikadp projversion=v1 projpath=output_limbo_9 \
  stop=PRESELECTED stopthreshold=9 serial=ARCHSIZE serialthreshold=9
```
Output: `output_limbo_9/tikadp-v1_IL_9_clusters.rsf`  
Clusters: 9 | Sizes: [82, 32, 12, 11, 9, 4, 3, 3, 2] | min=2, median=9, max=82

### k=15

```bash
java -Xmx4096m -jar /Users/mohit/Documents/DSSE-Week-1/arcade_tools/arcade_core_clusterer.jar \
  algo=LIMBO language=java deps=detect_parser_focus.rsf measure=IL \
  projname=tikadp projversion=v1 projpath=output_limbo_15 \
  stop=PRESELECTED stopthreshold=15 serial=ARCHSIZE serialthreshold=15
```
Output: `output_limbo_15/tikadp-v1_IL_15_clusters.rsf`  
Clusters: 15 | Sizes: [39, 32, 24, 11, 9, 6, 6, 6, 6, 4, 4, 3, 3, 3, 2] | min=2, median=6, max=39

**Chosen for final:** k=15 — produces the most balanced distribution (max cluster only 39 vs 114 for k=4). Better granularity for architectural analysis; sizes are roughly comparable, giving interpretable cluster structure.

```bash
cp output_limbo_15/tikadp-v1_IL_15_clusters.rsf tika_detect_parser_limbo.rsf
```

---

## Step 5c — ACDC Clustering

Algorithm: **ACDC (Algorithm for Comprehension-Driven Clustering)**  
Tool: `arcade_core-ACDC.jar`  
Parameters: default structural (no tuning required per Arcade documentation)

```bash
java -jar /Users/mohit/Documents/DSSE-Week-1/arcade_tools/arcade_core-ACDC.jar \
  /Users/mohit/Documents/DSSE-Week-1/arcade_tika/detect_parser_focus.rsf \
  /Users/mohit/Documents/DSSE-Week-1/arcade_tika/tika_detect_parser_acdc.rsf
```

Output: `tika_detect_parser_acdc.rsf`  
Clusters: 4 | Sizes: [110, 33, 13, 2] | min=2, median=13, max=110

---

## Step 6 — Validation

Sanity check: all three final RSF files cover exactly 158 classes (matching the filtered graph). No class is unclustered.

```bash
python3 analyze_clusters.py
```

Final deliverable files confirmed:
- `tika_detect_parser_wca.rsf`   — 9 clusters, 158 classes
- `tika_detect_parser_limbo.rsf` — 15 clusters, 158 classes
- `tika_detect_parser_acdc.rsf`  — 4 clusters, 158 classes
