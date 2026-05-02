# Architecture Recovery — Apache Tika: Detect & Parser (Week 1)

## 1. Scope: "Detect & Parser" Component (Group 6)

### What the xlsx says

From `Projects_Parts_under_focus.xlsx`, **Group 6 / Apache Tika / Detect & parser** maps to two top-level package prefixes:

```
org.apache.tika.detect
org.apache.tika.parser
```

These are the canonical detection and parsing interfaces/implementations in `tika-core`. The `detect` package contains `Detector`, `DefaultDetector`, `CompositeDetector`, and related classes that sniff MIME types. The `parser` package contains `Parser`, `AutoDetectParser`, `CompositeParser`, `ParseContext`, and the full parser interface hierarchy.

**Why only these two?** The xlsx scope for Group 6 is strictly `detect` and `parser` — neighboring packages like `tika-parsers-standard` (concrete format parsers), `tika-language`, or `tika-server` are explicitly out of scope for this group.

---

## 2. Counts

| Metric | Value |
|--------|-------|
| Total dependency edges in master RSF | 1,229 |
| Edges after filtering to detect+parser | 553 |
| Unique classes in detect/parser scope | 79 |
| Total unique classes in filtered graph (including dependencies) | 158 |

The filtered graph includes 158 total classes: 79 that belong to `detect`/`parser` directly, plus 79 external classes they depend on (e.g., `org.apache.tika.Tika`, `org.apache.tika.config.*`, `org.apache.tika.mime.*`). All are included because the filter rule keeps any edge where **either endpoint** is in scope.

---

## 3. WCA Clustering

**Algorithm:** Weighted Combined Algorithm (WCA)  
**Measure:** UEMNM (Unidirectional Evolutionary Module Neighborhood Measure)  
**Tool:** `arcade_core_clusterer.jar`

### Parameter sweep

| k (target clusters) | Actual clusters | Sizes |
|---------------------|-----------------|-------|
| 4 | 4 | [155, 1, 1, 1] |
| **9 (chosen)** | **9** | **[150, 1, 1, 1, 1, 1, 1, 1, 1]** |
| 15 | 15 | [144, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1] |

**Chosen: k=9.** All three runs produce the same structural pattern: one dominant cluster absorbing nearly all classes, and k−1 singletons. This is WCA's known behavior on graphs with a strong hub topology — the agglomerative merging converges to one large component before the stop criterion triggers. k=9 (≈√158 ÷ 1.4) represents the conventional middle-ground choice and was selected as the kept run.

**File:** `tika_detect_parser_wca.rsf` — 9 clusters, 158 classes

---

## 4. LIMBO Clustering

**Algorithm:** LIMBO (Scalable Clustering)  
**Measure:** IL (Information Loss)  
**Tool:** `arcade_core_clusterer.jar`

### Parameter sweep

| k (target clusters) | Actual clusters | Sizes |
|---------------------|-----------------|-------|
| 4 | 4 | [114, 32, 7, 5] |
| 9 | 9 | [82, 32, 12, 11, 9, 4, 3, 3, 2] |
| **15 (chosen)** | **15** | **[39, 32, 24, 11, 9, 6, 6, 6, 6, 4, 4, 3, 3, 3, 2]** |

**Chosen: k=15.** This run produces the most interpretable, balanced distribution. The largest cluster is only 39 classes (vs 114 at k=4), and the size range [2–39] is reasonable for manual inspection. k=4 and k=9 both have one oversized dominant cluster that limits analytical value. LIMBO clearly outperforms WCA in producing balanced partitions for this graph.

**File:** `tika_detect_parser_limbo.rsf` — 15 clusters, 158 classes

---

## 5. ACDC Clustering

**Algorithm:** ACDC (Algorithm for Comprehension-Driven Clustering)  
**Tool:** `arcade_core-ACDC.jar`  
**Parameters:** default structural (no tuning; algorithm is deterministic and parameter-free per Arcade documentation)

| Clusters | Sizes |
|----------|-------|
| 4 | [110, 33, 13, 2] |

ACDC uses structural patterns (subsystems, shared libraries) to form clusters. It produced 4 clusters: one dominant cluster of 110, one medium cluster of 33 (likely the pure `detect` classes), and two small groups. The result is structurally interpretable but still skewed toward the large cluster.

**File:** `tika_detect_parser_acdc.rsf` — 4 clusters, 158 classes

---

## 6. Summary Table

| Algorithm | Chosen k | Clusters | min | median | max | Notes |
|-----------|----------|----------|-----|--------|-----|-------|
| WCA (UEMNM) | 9 | 9 | 1 | 1 | 150 | Hub-dominated; all k values show same pattern |
| LIMBO (IL) | 15 | 15 | 2 | 6 | 39 | Most balanced; best for analysis |
| ACDC (structural) | default | 4 | 2 | 13 | 110 | Structurally grounded; parameter-free |

---

## 7. Issues Encountered

1. **WCA produces highly imbalanced clusters.** All three k values yield one massive cluster and k−1 singletons. This is not an error — it reflects that `org.apache.tika.Tika` and related core classes form a dense dependency hub. WCA's greedy merge strategy concentrates them into one cluster. Documented, kept k=9 as the representative run.

2. **Java version.** System has both Java 26 (JDK) and Java 25 (Homebrew). ARCADE jars ran without issues under the default `java` command (Java 26).

3. **One WCA result pre-existed** (`output_wca/tika_detect_parser-main_UEM_9_clusters.rsf` with measure=UEM, not UEMNM). This was generated in a prior session. Fresh runs with UEMNM confirm identical structure. The deliverable `tika_detect_parser_wca.rsf` uses the fresh UEMNM k=9 run.

---

## 8. Artifact Inventory

| File | Size | Description |
|------|------|-------------|
| `tika/tika-core/target/tika-core-4.0.0-SNAPSHOT.jar` | ~2 MB | Compiled Tika core jar |
| `tika_master.rsf` | 113 KB | Full system dependency graph (1,229 edges) |
| `tika_master.fv` | 54 KB | Feature vector output from JavaParser |
| `detect_parser_focus.rsf` | 50 KB | Filtered graph (553 edges, 158 classes) |
| `focus_scope.txt` | 46 B | Package prefixes for Group 6 |
| `tika_detect_parser_wca.rsf` | 8.5 KB | WCA result (9 clusters) |
| `tika_detect_parser_limbo.rsf` | 8.5 KB | LIMBO result (15 clusters) |
| `tika_detect_parser_acdc.rsf` | 12 KB | ACDC result (4 clusters) |
| `run_log.md` | — | Chronological command log |
| `README.md` | — | This report |

---

## 9. How to Reproduce

All commands can be re-run from `arcade_tika/`:

```bash
# Re-filter (if master RSF changes)
python3 filter_rsf.py tika_master.rsf detect_parser_focus.rsf

# Run all clustering (WCA x3, LIMBO x3, ACDC)
bash run_all_clustering.sh

# Analyze results
python3 analyze_clusters.py
```

Or run individual algorithms as shown in `run_log.md`.
