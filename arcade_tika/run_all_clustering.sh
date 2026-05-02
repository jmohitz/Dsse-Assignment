#!/bin/bash
# =================================================================
# run_all_clustering.sh
# Run all ARCADE clustering algorithms for Tika Detect & Parser
# Execute this script from the arcade_tika directory:
#   bash run_all_clustering.sh
# =================================================================
set -e

TOOLS="/Users/mohit/Documents/DSSE-Week-1/arcade_tools"
BASE="/Users/mohit/Documents/DSSE-Week-1/arcade_tika"
DEPS="$BASE/detect_parser_focus.rsf"
VENV="$BASE/.venv/bin/python3"

echo "============================================="
echo " ARCADE Clustering Pipeline for Tika Detect & Parser"
echo "============================================="
echo ""

# ---------- WCA with UEMNM, k=9 ----------
echo "[1/7] WCA k=9 (UEMNM)..."
mkdir -p "$BASE/output_wca_9"
java -Xmx4096m -jar "$TOOLS/arcade_core_clusterer.jar" \
  algo=WCA language=java deps="$DEPS" measure=UEMNM \
  projname=tikadp projversion=v1 \
  projpath="$BASE/output_wca_9" \
  stop=PRESELECTED stopthreshold=9 \
  serial=ARCHSIZE serialthreshold=9
echo "  -> Done. Output in output_wca_9/"

# ---------- WCA with UEMNM, k=4 ----------
echo "[2/7] WCA k=4 (UEMNM)..."
mkdir -p "$BASE/output_wca_4"
java -Xmx4096m -jar "$TOOLS/arcade_core_clusterer.jar" \
  algo=WCA language=java deps="$DEPS" measure=UEMNM \
  projname=tikadp projversion=v1 \
  projpath="$BASE/output_wca_4" \
  stop=PRESELECTED stopthreshold=4 \
  serial=ARCHSIZE serialthreshold=4
echo "  -> Done. Output in output_wca_4/"

# ---------- WCA with UEMNM, k=15 ----------
echo "[3/7] WCA k=15 (UEMNM)..."
mkdir -p "$BASE/output_wca_15"
java -Xmx4096m -jar "$TOOLS/arcade_core_clusterer.jar" \
  algo=WCA language=java deps="$DEPS" measure=UEMNM \
  projname=tikadp projversion=v1 \
  projpath="$BASE/output_wca_15" \
  stop=PRESELECTED stopthreshold=15 \
  serial=ARCHSIZE serialthreshold=15
echo "  -> Done. Output in output_wca_15/"

# ---------- LIMBO k=9 ----------
echo "[4/7] LIMBO k=9 (IL)..."
mkdir -p "$BASE/output_limbo_9"
java -Xmx4096m -jar "$TOOLS/arcade_core_clusterer.jar" \
  algo=LIMBO language=java deps="$DEPS" measure=IL \
  projname=tikadp projversion=v1 \
  projpath="$BASE/output_limbo_9" \
  stop=PRESELECTED stopthreshold=9 \
  serial=ARCHSIZE serialthreshold=9
echo "  -> Done. Output in output_limbo_9/"

# ---------- LIMBO k=4 ----------
echo "[5/7] LIMBO k=4 (IL)..."
mkdir -p "$BASE/output_limbo_4"
java -Xmx4096m -jar "$TOOLS/arcade_core_clusterer.jar" \
  algo=LIMBO language=java deps="$DEPS" measure=IL \
  projname=tikadp projversion=v1 \
  projpath="$BASE/output_limbo_4" \
  stop=PRESELECTED stopthreshold=4 \
  serial=ARCHSIZE serialthreshold=4
echo "  -> Done. Output in output_limbo_4/"

# ---------- LIMBO k=15 ----------
echo "[6/7] LIMBO k=15 (IL)..."
mkdir -p "$BASE/output_limbo_15"
java -Xmx4096m -jar "$TOOLS/arcade_core_clusterer.jar" \
  algo=LIMBO language=java deps="$DEPS" measure=IL \
  projname=tikadp projversion=v1 \
  projpath="$BASE/output_limbo_15" \
  stop=PRESELECTED stopthreshold=15 \
  serial=ARCHSIZE serialthreshold=15
echo "  -> Done. Output in output_limbo_15/"

# ---------- ACDC ----------
echo "[7/7] ACDC (structural)..."
java -jar "$TOOLS/arcade_core-ACDC.jar" \
  "$DEPS" "$BASE/tika_detect_parser_acdc.rsf"
echo "  -> Done. Output: tika_detect_parser_acdc.rsf"

echo ""
echo "============================================="
echo " Copying best results to final names"
echo "============================================="

# Pick best WCA: try k=9 first
WCA_BEST=$(find "$BASE/output_wca_9" -name "*.rsf" | head -1)
if [ -n "$WCA_BEST" ]; then
  cp "$WCA_BEST" "$BASE/tika_detect_parser_wca.rsf"
  echo "  WCA: copied $WCA_BEST -> tika_detect_parser_wca.rsf"
fi

# Pick best LIMBO: try k=9 first
LIMBO_BEST=$(find "$BASE/output_limbo_9" -name "*.rsf" | head -1)
if [ -n "$LIMBO_BEST" ]; then
  cp "$LIMBO_BEST" "$BASE/tika_detect_parser_limbo.rsf"
  echo "  LIMBO: copied $LIMBO_BEST -> tika_detect_parser_limbo.rsf"
fi

echo ""
echo "============================================="
echo " Analyzing all results"
echo "============================================="

$VENV "$BASE/analyze_clusters.py"

echo ""
echo "=== ALL DONE ==="
