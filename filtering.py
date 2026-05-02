import sys
 
filters = ["org.apache.tika.detect", "org.apache.tika.parser"]
 
input_file = sys.argv[1] if len(sys.argv) > 1 else "tika-core.rsf"
output_file = sys.argv[2] if len(sys.argv) > 2 else "filtered_rsf.rsf"
 
with open(input_file) as f:
    lines = f.readlines()
 
filtered = []
for line in lines:
    parts = line.split()
    if len(parts) != 3:
        continue
    _, src, tgt = parts
    if any(src.startswith(x) or tgt.startswith(x) for x in filters):
        filtered.append(line)
 
with open(output_file, 'w') as f:
    f.writelines(filtered)
 
print(f"Filtered {len(filtered)} / {len(lines)} lines")