#!/bin/bash
set -e

TOOLS="/Users/mohit/Documents/DSSE-Week-1/arcade_tools"
BASE="/Users/mohit/Documents/DSSE-Week-1/arcade_tika"
DEPS="$BASE/detect_parser_focus.rsf"

echo "=== WCA k=4 (UEMNM) ==="
rm -rf "$BASE/output_wca_4" && mkdir -p "$BASE/output_wca_4"
java -Xmx4096m -jar "$TOOLS/arcade_core_clusterer.jar" algo=WCA language=java deps="$DEPS" measure=UEMNM projname=tikadp projversion=v1 projpath="$BASE/output_wca_4" stop=PRESELECTED stopthreshold=4 serial=ARCHSIZE serialthreshold=4
echo "WCA k=4 done"
ls -la "$BASE/output_wca_4/"

echo ""
echo "=== WCA k=15 (UEMNM) ==="
rm -rf "$BASE/output_wca_15" && mkdir -p "$BASE/output_wca_15"
java -Xmx4096m -jar "$TOOLS/arcade_core_clusterer.jar" algo=WCA language=java deps="$DEPS" measure=UEMNM projname=tikadp projversion=v1 projpath="$BASE/output_wca_15" stop=PRESELECTED stopthreshold=15 serial=ARCHSIZE serialthreshold=15
echo "WCA k=15 done"
ls -la "$BASE/output_wca_15/"

echo ""
echo "=== LIMBO k=9 ==="
rm -rf "$BASE/output_limbo_9" && mkdir -p "$BASE/output_limbo_9"
java -Xmx4096m -jar "$TOOLS/arcade_core_clusterer.jar" algo=LIMBO language=java deps="$DEPS" measure=IL projname=tikadp projversion=v1 projpath="$BASE/output_limbo_9" stop=PRESELECTED stopthreshold=9 serial=ARCHSIZE serialthreshold=9
echo "LIMBO k=9 done"
ls -la "$BASE/output_limbo_9/"

echo ""
echo "=== LIMBO k=4 ==="
rm -rf "$BASE/output_limbo_4" && mkdir -p "$BASE/output_limbo_4"
java -Xmx4096m -jar "$TOOLS/arcade_core_clusterer.jar" algo=LIMBO language=java deps="$DEPS" measure=IL projname=tikadp projversion=v1 projpath="$BASE/output_limbo_4" stop=PRESELECTED stopthreshold=4 serial=ARCHSIZE serialthreshold=4
echo "LIMBO k=4 done"
ls -la "$BASE/output_limbo_4/"

echo ""
echo "=== LIMBO k=15 ==="
rm -rf "$BASE/output_limbo_15" && mkdir -p "$BASE/output_limbo_15"
java -Xmx4096m -jar "$TOOLS/arcade_core_clusterer.jar" algo=LIMBO language=java deps="$DEPS" measure=IL projname=tikadp projversion=v1 projpath="$BASE/output_limbo_15" stop=PRESELECTED stopthreshold=15 serial=ARCHSIZE serialthreshold=15
echo "LIMBO k=15 done"
ls -la "$BASE/output_limbo_15/"

echo ""
echo "=== ACDC ==="
java -jar "$TOOLS/arcade_core-ACDC.jar" "$DEPS" "$BASE/tika_detect_parser_acdc.rsf"
echo "ACDC done"
ls -la "$BASE/tika_detect_parser_acdc.rsf"

echo ""
echo "=== ALL CLUSTERING COMPLETE ==="
