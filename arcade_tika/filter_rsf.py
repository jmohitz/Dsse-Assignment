#!/usr/bin/env python3
import sys

prefixes = ["org.apache.tika.detect", "org.apache.tika.parser"]

input_file = sys.argv[1] if len(sys.argv) > 1 else "/Users/mohit/Documents/DSSE-Week-1/arcade_tika/tika_master.rsf"
output_file = sys.argv[2] if len(sys.argv) > 2 else "/Users/mohit/Documents/DSSE-Week-1/arcade_tika/detect_parser_focus.rsf"

with open(input_file, 'r') as f:
    lines = f.readlines()

filtered = []
focus_classes = set()
all_classes = set()

for line in lines:
    parts = line.strip().split()
    if len(parts) != 3:
        continue
    relation, src, tgt = parts
    src_match = any(src.startswith(p) for p in prefixes)
    tgt_match = any(tgt.startswith(p) for p in prefixes)
    if src_match or tgt_match:
        filtered.append(line)
        all_classes.add(src)
        all_classes.add(tgt)
        if src_match:
            focus_classes.add(src)
        if tgt_match:
            focus_classes.add(tgt)

with open(output_file, 'w') as f:
    f.writelines(filtered)

print("Total lines in master RSF: " + str(len(lines)))
print("Lines after filtering: " + str(len(filtered)))
print("Unique classes in focus scope (detect/parser): " + str(len(focus_classes)))
print("Total unique classes in filtered graph: " + str(len(all_classes)))
print("")
print("Focus classes:")
for c in sorted(focus_classes):
    print("  " + c)
