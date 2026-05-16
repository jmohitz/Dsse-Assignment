# Week 3 — ARC Clustering Pipeline

Standalone scripts that reproduce the Colab's ARC (Adaptive, Representation-based Clustering) locally, without the RAM pressure of a Colab session.

---

## Quick start

```bash
# From the repo root (this directory)
cd /Users/mohit/Documents/DSSE-Week-1/.claude/worktrees/cranky-curie-374972

# Install Python deps (once)
pip install scikit-learn numpy transformers torch sentence-transformers

# 1. Run clustering at the Colab's default settings (alpha=0.4, k=12)
python3 arc_clustering.py

# 2. Compare to Week 1 baselines (WCA k=4, Limbo k=4, ACDC)
python3 arc_metrics.py --arc-rsf output_arc_0.4_12/tikadp-v1_ARC_12_clusters.rsf

# 3. Full alpha + k sweep (takes ~10 min on CPU with codebert)
python3 arc_sweep.py
```

---

## Scripts

### `arc_clustering.py`

Reads `filtered_rsf.rsf`, loads Java source from the Tika checkout, computes embeddings, blends structural + semantic similarity, and saves an ARCADE-compatible RSF.

**Output:** `output_arc_{alpha}_{n_clusters}/tikadp-v1_ARC_{n_clusters}_clusters.rsf`
**Format:** `contain <cluster_id> <org.apache.tika.FullyQualifiedClassName>` — identical to WCA/Limbo.

**Structural matrix:** co-dependency count (how many times each pair co-appears as source/target in filtered_rsf.rsf), normalized by max. **Linkage:** `complete` — matching the Week 3 template notebook exactly.

| Flag | Default | Description |
|---|---|---|
| `--alpha` | 0.4 | Weight for structural similarity; `1-alpha` = semantic weight |
| `--n-clusters` | 12 | Number of clusters |
| `--model` | codebert | `codebert` (fast, 125M, CPU-friendly) or `nomic` (7B, slow) |
| `--force` | off | Recompute even if RSF already exists |

**Embedding cache:** Lives in `.embedding_cache/`. Re-runs skip recomputation as long as the class list hasn't changed.

### `arc_metrics.py`

Runs `arcade_core_A2a.jar` and `arcade_core_Cvg.jar` to compare an ARC RSF against WCA k=4, Limbo k=4, and ACDC. Appends results to `metrics_results.txt`.

| Flag | Default | Description |
|---|---|---|
| `--arc-rsf` | (required) | Path to ARC RSF file |
| `--label` | (dir name) | Section heading in output file |
| `--out` | `metrics_results.txt` | Output file (appended) |

### `arc_sweep.py`

Orchestrates both sweeps:
- **Alpha sweep:** `{0.0, 0.2, 0.4, 0.6, 0.8, 1.0}` at fixed `k=12`
- **k sweep:** `{4, 8, 12, 16, 20}` at fixed `alpha=0.4`

Prints a summary table of cluster size stats and A2A scores at the end.

| Flag | Description |
|---|---|
| `--model codebert\|nomic` | Embedding model |
| `--alpha-only` | Run only the alpha sweep |
| `--k-only` | Run only the k sweep |
| `--force` | Recompute all RSF files |

---

## Using the larger nomic-embed-code model

The Colab used `nomic-ai/nomic-embed-code` (7B params). On a Mac without a GPU, this runs in float16 on CPU and takes ~30–60 minutes for 157 classes. Use it when you want exact Colab parity:

```bash
python3 arc_clustering.py --model nomic --alpha 0.4 --n-clusters 12
```

Once the embeddings are cached (`.embedding_cache/embeddings_nomic.npy`), all subsequent alpha/k runs reuse them instantly.

---

## Directory layout

```
<repo>/
├── filtered_rsf.rsf              # 551 deps, 157 classes (Week 1 filtered input)
├── arc_clustering.py             # ARC clustering
├── arc_metrics.py                # A2A/CVG comparison
├── arc_sweep.py                  # Alpha + k sweep driver
├── metrics_results.txt           # Appended results (Week 2 + Week 3)
├── .embedding_cache/             # Cached numpy embeddings (gitignored)
└── output_arc_{alpha}_{k}/
    └── tikadp-v1_ARC_{k}_clusters.rsf
```

Week 1 RSF files read from:
```
../../arcade_tika/
├── output_wca_4/tikadp-v1_UEMNM_4_clusters.rsf
├── output_limbo_4/tikadp-v1_IL_4_clusters.rsf
└── output_acdc/tika_detect_parser_acdc.rsf   ← regenerated (see below)
```

ARCADE JARs: `../../arcade_tools/arcade_core_A2a.jar`, `arcade_core_Cvg.jar`

> **ACDC note:** `tika_detect_parser_acdc.rsf` was removed from the repo in the Week 2 cleanup.
> Regenerate it once with:
> ```bash
> java -jar ../../arcade_tools/arcade_core-ACDC.jar \
>   filtered_rsf.rsf \
>   ../../arcade_tika/output_acdc/tika_detect_parser_acdc.rsf
> ```

Override paths with env vars `DSSE_ROOT`, `TIKA_SRC`, `ARCADE_TOOLS`, `WEEK1_BASE`.

---

## Interpreting results

- **A2A** (Architecture-to-Architecture): Measures structural overlap between two decompositions. Ranges from 0 (no match) to 1 (identical). Values > 0.5 indicate meaningful agreement.
- **CVG** (Coverage): Directional — CVG(ARC→base) measures what fraction of ARC clusters are well-covered by the baseline, and vice versa.
- A large **max cluster** (like the 100+ class mega-core seen in Limbo/ACDC) indicates classes with dense, highly-connected structural relationships that resist separation.
- **alpha → 0**: pure semantic clustering (ignores dependency graph)
- **alpha → 1**: pure structural clustering (ignores source code)
- **alpha = 0.4**: the Colab default — slight structural lean
