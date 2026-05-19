#!/usr/bin/env python3
"""
ARC clustering for Apache Tika detect/parser subsystem.

Combines structural similarity (Jaccard over dependency neighborhoods from
filtered_rsf.rsf) with semantic similarity (source-code embeddings) and
runs AgglomerativeClustering on the blended distance matrix.

Output: output_arc_{alpha}_{n_clusters}/tikadp-v1_ARC_{n_clusters}_clusters.rsf
Format: contain <cluster_id> <fully.qualified.ClassName>   (matches ARCADE/WCA/Limbo)

Usage:
    python3 arc_clustering.py                          # alpha=0.4, k=12, codebert
    python3 arc_clustering.py --alpha 0.6 --n-clusters 8
    python3 arc_clustering.py --model nomic            # 7B model, slow on CPU
    python3 arc_clustering.py --force                  # recompute even if RSF exists
"""

import argparse
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------------------
# Paths  (override with env vars DSSE_ROOT, TIKA_SRC if layout differs)
# ---------------------------------------------------------------------------
import os

WORKTREE     = Path(__file__).resolve().parent
PROJECT_ROOT = Path(os.environ.get("DSSE_ROOT",  WORKTREE.parent.parent.parent))
TIKA_SRC     = Path(os.environ.get("TIKA_SRC",   PROJECT_ROOT / "arcade_tika" / "tika"))
FILTERED_RSF = WORKTREE / "filtered_rsf.rsf"
CACHE_DIR    = WORKTREE / ".embedding_cache"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_args():
    p = argparse.ArgumentParser(description="ARC clustering for Tika detect/parser")
    p.add_argument("--alpha",      type=float, default=0.4,
                   help="Structural weight [0,1]; 1-alpha = semantic weight (default 0.4)")
    p.add_argument("--n-clusters", type=int,   default=12,
                   help="Number of clusters (default 12)")
    p.add_argument("--model",      choices=["codebert", "nomic"], default="codebert",
                   help="Embedding model: codebert (fast, CPU) or nomic (7B, slow, default codebert)")
    p.add_argument("--force",      action="store_true",
                   help="Rerun even if RSF output already exists")
    return p.parse_args()


def extract_classes(rsf_path: Path) -> list[str]:
    classes: set[str] = set()
    with open(rsf_path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 3:
                classes.add(parts[1])
                classes.add(parts[2])
    return sorted(classes)


def build_structural_matrix(rsf_path: Path, classes: list[str]) -> np.ndarray:
    """NxN co-dependency count matrix, normalized to [0,1] by max value.

    For each pair (i, j), counts how many times they appear together as
    source/target in the same dependency edge (undirected). Diagonal = 1.
    Matches the Week 3 template notebook approach.
    """
    class_idx = {c: i for i, c in enumerate(classes)}
    n = len(classes)
    mat = np.zeros((n, n), dtype=np.float32)

    with open(rsf_path) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 3 and parts[1] in class_idx and parts[2] in class_idx:
                i = class_idx[parts[1]]
                j = class_idx[parts[2]]
                mat[i][j] += 1
                mat[j][i] += 1

    # Normalize by max so values are in [0, 1]
    max_val = mat.max()
    if max_val > 0:
        mat /= max_val

    np.fill_diagonal(mat, 1.0)
    return mat


def find_java_source(fqn: str, tika_src: Path) -> Path | None:
    """Map org.apache.tika.X.ClassName (or ClassName$Inner) to .java in main src."""
    outer = fqn.split("$")[0]                      # drop inner-class suffix
    path_suffix = outer.replace(".", "/") + ".java"
    simple_name = outer.split(".")[-1] + ".java"

    # Prefer an exact path match under src/main/java
    for hit in tika_src.rglob(simple_name):
        if "/main/" in str(hit) and str(hit).endswith(path_suffix):
            return hit
    # Fallback: any main-src file with the right simple name
    for hit in tika_src.rglob(simple_name):
        if "/main/" in str(hit):
            return hit
    return None


# ---------------------------------------------------------------------------
# Embedding functions (cached)
# ---------------------------------------------------------------------------

def _cache_paths(model_key: str) -> tuple[Path, Path]:
    return CACHE_DIR / f"embeddings_{model_key}.npy", CACHE_DIR / f"classes_{model_key}.txt"


def _load_cache(model_key: str, classes: list[str]) -> np.ndarray | None:
    emb_path, cls_path = _cache_paths(model_key)
    if emb_path.exists() and cls_path.exists():
        if cls_path.read_text().splitlines() == classes:
            print(f"  Loading cached embeddings from {emb_path.name}")
            return np.load(emb_path)
    return None


def _save_cache(model_key: str, classes: list[str], embs: np.ndarray) -> None:
    CACHE_DIR.mkdir(exist_ok=True)
    emb_path, cls_path = _cache_paths(model_key)
    np.save(emb_path, embs)
    cls_path.write_text("\n".join(classes))
    print(f"  Cached embeddings to {emb_path}")


def _read_source(fqn: str) -> str:
    src = find_java_source(fqn, TIKA_SRC)
    if src:
        return src.read_text(errors="replace")
    print(f"  [WARN] No source found for {fqn} — using class-name stub")
    return f"public class {fqn.split('.')[-1].split('$')[0]} {{}}"


def compute_embeddings_codebert(classes: list[str]) -> np.ndarray:
    cached = _load_cache("codebert", classes)
    if cached is not None:
        return cached

    import torch
    from transformers import AutoModel, AutoTokenizer

    print("  Loading microsoft/codebert-base …")
    tokenizer = AutoTokenizer.from_pretrained("microsoft/codebert-base")
    model = AutoModel.from_pretrained("microsoft/codebert-base")
    model.eval()

    embs = []
    for i, fqn in enumerate(classes):
        code = _read_source(fqn)[:4096]   # keep first ~4k chars
        inputs = tokenizer(code, return_tensors="pt", truncation=True,
                           max_length=512, padding=True)
        with torch.no_grad():
            out = model(**inputs)
        emb = out.last_hidden_state.mean(dim=1).squeeze().numpy()
        embs.append(emb)
        if (i + 1) % 25 == 0 or (i + 1) == len(classes):
            print(f"  Embedded {i+1}/{len(classes)}")

    arr = np.array(embs, dtype=np.float32)
    _save_cache("codebert", classes, arr)
    return arr


def compute_embeddings_nomic(classes: list[str]) -> np.ndarray:
    cached = _load_cache("nomic", classes)
    if cached is not None:
        return cached

    import torch
    from transformers import AutoModel, AutoTokenizer

    print("  Loading nomic-ai/nomic-embed-code (7B params — expect minutes on CPU) …")
    tokenizer = AutoTokenizer.from_pretrained("nomic-ai/nomic-embed-code",
                                              trust_remote_code=True)
    model = AutoModel.from_pretrained("nomic-ai/nomic-embed-code",
                                      trust_remote_code=True,
                                      torch_dtype=torch.float16)
    model.eval()

    embs = []
    for i, fqn in enumerate(classes):
        code = _read_source(fqn)[:4096]
        inputs = tokenizer(code, return_tensors="pt", truncation=True,
                           max_length=512, padding=True)
        with torch.no_grad():
            out = model(**inputs)
        emb = out.last_hidden_state.mean(dim=1).squeeze().float().numpy()
        embs.append(emb)
        if (i + 1) % 10 == 0 or (i + 1) == len(classes):
            print(f"  Embedded {i+1}/{len(classes)}")

    arr = np.array(embs, dtype=np.float32)
    _save_cache("nomic", classes, arr)
    return arr


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(alpha: float, n_clusters: int, model: str, force: bool = False) -> Path:
    """Run ARC clustering and return path to written RSF file."""
    out_dir = WORKTREE / f"output_arc_{alpha}_{n_clusters}"
    rsf_path = out_dir / f"tikadp-v1_ARC_{n_clusters}_clusters.rsf"

    if rsf_path.exists() and not force:
        print(f"  RSF already exists ({rsf_path}), skipping. Use --force to rerun.")
        return rsf_path

    print(f"\n{'='*60}")
    print(f"ARC  alpha={alpha}  k={n_clusters}  model={model}")
    print(f"{'='*60}")

    classes = extract_classes(FILTERED_RSF)
    n = len(classes)
    print(f"Classes: {n}")

    # Structural matrix
    print("Building structural similarity matrix (co-dependency count, normalized) …")
    struct_mat = build_structural_matrix(FILTERED_RSF, classes)

    # Semantic matrix
    print(f"Computing embeddings via {model} …")
    if model == "nomic":
        embs = compute_embeddings_nomic(classes)
    else:
        embs = compute_embeddings_codebert(classes)

    print("Building semantic similarity matrix …")
    sem_mat = cosine_similarity(embs).astype(np.float32)
    sem_mat = (sem_mat + 1.0) / 2.0   # shift [-1,1] → [0,1]

    # Combine and cluster
    combined = alpha * struct_mat + (1.0 - alpha) * sem_mat
    distance_mat = np.clip(1.0 - combined, 0.0, None)

    print(f"AgglomerativeClustering (complete linkage, k={n_clusters}) …")
    labels = AgglomerativeClustering(
        n_clusters=n_clusters,
        metric="precomputed",
        linkage="complete"
    ).fit_predict(distance_mat)

    # Write RSF
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(rsf_path, "w") as f:
        for cls, lbl in zip(classes, labels):
            f.write(f"contain {lbl} {cls}\n")
    print(f"Saved: {rsf_path}")

    # Print stats
    _print_stats(classes, labels)

    return rsf_path


def _print_stats(classes: list[str], labels: np.ndarray) -> None:
    sizes = Counter(int(l) for l in labels)
    sorted_sizes = sorted(sizes.items(), key=lambda x: x[1], reverse=True)
    sz_vals = [v for _, v in sorted_sizes]
    median = sz_vals[len(sz_vals) // 2]

    print(f"\nTotal classes : {len(classes)}")
    print(f"Cluster sizes (descending):")
    for cid, sz in sorted_sizes:
        print(f"  cluster {cid:2d}: {sz:3d} classes")
    print(f"Min={min(sz_vals)}  Median={median}  Max={max(sz_vals)}")

    largest_id = sorted_sizes[0][0]
    members = [c for c, l in zip(classes, labels) if int(l) == largest_id]
    print(f"\nLargest cluster (cluster {largest_id}, {sorted_sizes[0][1]} classes):")
    for m in members:
        print(f"  {m}")


if __name__ == "__main__":
    args = parse_args()
    run(args.alpha, args.n_clusters, args.model, args.force)
