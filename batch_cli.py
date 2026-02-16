#!/usr/bin/env python3
"""
CLI tool for batch converting Bambu Lab .3mf files to Snapmaker U1 format.
"""
import os
import sys
import glob
from app import is_bambu_file, parse_bambu_filaments, auto_map_filaments, convert_single_file

def batch_convert(input_dir, output_dir):
    """Convert all Bambu .3mf files in input_dir to output_dir."""

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Find all .3mf files
    pattern = os.path.join(input_dir, "*.3mf")
    files = glob.glob(pattern)

    print(f"Found {len(files)} .3mf files in {input_dir}")
    print(f"Output directory: {output_dir}")
    print("-" * 60)

    converted = 0
    skipped = 0
    errors = 0

    for filepath in files:
        filename = os.path.basename(filepath)
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_U1.3mf"
        output_path = os.path.join(output_dir, output_filename)

        # Check if it's a Bambu file
        if not is_bambu_file(filepath):
            print(f"SKIP: {filename} (not a Bambu file)")
            skipped += 1
            continue

        # Parse filaments
        filaments = parse_bambu_filaments(filepath)
        if len(filaments) > 4:
            print(f"WARN: {filename} has {len(filaments)} colors (will need pause/split)")

        # Auto-map filaments
        colors = auto_map_filaments(filaments)

        # Convert
        success, error = convert_single_file(filepath, output_path, colors)

        if success:
            print(f"OK:   {filename} -> {output_filename}")
            converted += 1
        else:
            print(f"ERR:  {filename} - {error}")
            errors += 1

    print("-" * 60)
    print(f"Done! Converted: {converted}, Skipped: {skipped}, Errors: {errors}")
    print(f"Output saved to: {output_dir}")

    return converted, skipped, errors

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 batch_cli.py <input_dir> <output_dir>")
        print("Example: python3 batch_cli.py /mnt/e/Downloads /mnt/e/3d/converted")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    if not os.path.isdir(input_dir):
        print(f"Error: Input directory does not exist: {input_dir}")
        sys.exit(1)

    batch_convert(input_dir, output_dir)
