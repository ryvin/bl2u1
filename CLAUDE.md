# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bambu Lab to Snapmaker U1 Converter - A Flask web application that converts Bambu Lab/Bambu Studio .3mf files to Snapmaker U1 compatible format, preserving multi-color painting and filament assignments.

## Commands

```bash
# Install dependencies
pip install flask

# Run the application (starts on port 8080)
python app.py

# The app will be available at http://localhost:8080
```

## Architecture

### Single-File Flask Backend (`app.py`)
- **Single File Routes**: `/` (UI), `/analyze` (POST), `/convert` (POST), `/download/<filename>` (serves files), `/filament-types` (returns filament profiles)
- **Batch Routes**: `/batch-analyze` (POST - analyzes multiple files), `/batch-convert` (POST - converts all and returns ZIP)
- **File handling**: Uploads stored in `uploads/` with UUID-based session IDs, auto-cleaned after 8 hours
- **3MF Processing**: Uses zipfile + xml.etree.ElementTree to modify internal XML/JSON configs

### Frontend (`templates/index.html`)
- Single-page app using Tailwind CSS (CDN) and Font Awesome
- **Single File Mode**: upload → configure filaments → download
- **Batch Mode**: select folder → preview files → convert all → download ZIP

### Template 3MF Files
- `u1_template.3mf` - Base U1 printer profile (supports disabled)
- `u1_template_supports.3mf` - U1 profile with Tree Supports (auto) enabled
- `filament_types.3mf` - Reference file containing available Snapmaker U1 filament profiles

### Conversion Logic (in `convert_single_file()`)
1. Reads original Bambu .3mf and extracts project settings
2. Detects if supports were enabled via `different_settings_to_system` array
3. Selects appropriate U1 template based on support detection
4. Modifies three internal configs:
   - `Metadata/slice_info.config` (XML) - printer model, filament mappings
   - `Metadata/model_settings.config` (XML) - extruder references for painted regions
   - `Metadata/project_settings.config` (JSON) - printer settings, filament colors/types
5. Pads to 4 filaments (U1 hardware requirement) with white PLA
6. Writes new .3mf archive

### Batch Conversion
- **`is_bambu_file(filepath)`**: Checks if a .3mf is from Bambu Lab (not already Snapmaker)
- **`auto_map_filaments(filaments)`**: Automatically maps filament types to closest U1 profiles (PLA→PLA, PETG→PETG-HF, etc.)
- **Workflow**: Upload folder → Filter to valid Bambu files → Auto-map filaments → Convert all → Create ZIP archive
- **Output**: Each file renamed `original_name_U1.3mf`, bundled in a single ZIP download

### Key Data Structures
- Filament mapping: `{original_id: {color: "#RRGGBB", type: "PLA"}}` passed from frontend
- ID remapping: Original Bambu filament IDs → sequential 1-based U1 IDs (critical for extruder references)
- Batch files list: `[{filename, filaments, auto_colors}, ...]` for batch preview

### Testing
```bash
# Run Playwright tests
python3 -m pytest test_batch.py -v
```
