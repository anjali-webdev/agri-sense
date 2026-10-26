print("Loading corrupted CSV file...")

# Read all lines
with open('data/crop_dataset.csv', 'r') as f:
    lines = f.readlines()

print(f"Original file has {len(lines)} lines")

# The first line should be the header
header = lines[0].strip()
print(f"Header: {header}")

# Filter out duplicate header rows from the data
clean_lines = [header + '\n']
duplicate_count = 0

for i, line in enumerate(lines[1:], start=2):
    line_stripped = line.strip()
    if line_stripped == header:
        print(f"Found duplicate header at line {i}")
        duplicate_count += 1
    elif line_stripped:  # Keep non-empty lines
        clean_lines.append(line)

print(f"\nRemoved {duplicate_count} duplicate header row(s)")
print(f"Clean file will have {len(clean_lines)} lines (including header)")

# Save cleaned CSV
with open('data/crop_dataset.csv', 'w') as f:
    f.writelines(clean_lines)

print("✓ Cleaned CSV saved to data/crop_dataset.csv")

# Show first few lines
print("\nFirst 10 lines of cleaned data:")
for i, line in enumerate(clean_lines[:10], start=1):
    print(f"{i}: {line.strip()}")

# Count crops
crop_counts = {}
for line in clean_lines[1:]:  # Skip header
    parts = line.strip().split(',')
    if len(parts) >= 5:
        crop = parts[4]
        crop_counts[crop] = crop_counts.get(crop, 0) + 1

print(f"\nTotal data rows: {len(clean_lines) - 1}")
print("\nCrop distribution:")
for crop in sorted(crop_counts.keys()):
    print(f"  {crop}: {crop_counts[crop]}")
