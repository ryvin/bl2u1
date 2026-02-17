# GUI Enhancements Design

**Date:** 2026-02-16
**Status:** Approved

## Overview

Enhance the Bambu to Snapmaker U1 converter web UI with:
- Configurable output folder with folder browser
- Conversion history tracking (server-side)
- New file detection with badge notifications
- Smart duplicate handling

## Requirements Summary

| Requirement | Solution |
|-------------|----------|
| Output folder selection | Text input + folder tree browser modal |
| Remember settings | Server-side JSON, persists across sessions |
| Output file naming | `filename_U1.3mf` (matches CLI behavior) |
| Duplicate handling | Hash-based: skip exact dupes, version suffix for changes |
| New file detection | Badge on Batch tab, compare against history |
| Source monitoring | Configurable source folder in settings |

## UI Design

### Header Changes
- Add settings gear icon (⚙️) next to info button
- Batch Convert tab shows badge: `Batch Convert (3 new)`

### Settings Panel (Slide-out)
```
┌─────────────────────────────────┐
│ ⚙️ Settings              [X]   │
├─────────────────────────────────┤
│ Output Folder:                  │
│ [E:\3d\converted_u1    ] [📁]  │
│                                 │
│ Source Folder (for monitoring): │
│ [E:\Downloads          ] [📁]  │
│                                 │
│ [✓] Auto-detect new files      │
│ [✓] Delete exact duplicates    │
│                                 │
│ History: 145 files converted    │
│ [View History] [Clear History]  │
└─────────────────────────────────┘
```

### Folder Browser Modal
- Tree view of server directories
- Expandable folders with lazy loading
- "Select" button confirms choice

## Data Storage

### File: `conversion_history.json`
```json
{
  "settings": {
    "output_folder": "E:\\3d\\converted_u1",
    "source_folder": "E:\\Downloads",
    "auto_detect": true,
    "delete_duplicates": true
  },
  "converted": [
    {
      "source": "cat.3mf",
      "source_hash": "abc123...",
      "output": "cat_U1.3mf",
      "timestamp": "2026-02-16T10:30:00",
      "filaments": 3
    }
  ]
}
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/settings` | GET | Get current settings |
| `/settings` | POST | Update settings |
| `/history` | GET | List converted files |
| `/history/clear` | POST | Clear history |
| `/browse` | GET | List directory contents (path param) |
| `/check-new` | GET | Find unconverted files in source folder |

## Duplicate Detection Logic

1. Calculate MD5 hash of source file
2. Check history for matching `source_hash`:
   - **Match found:** Skip (already converted)
   - **No match, output exists:** Create versioned file (`_v2`, `_v3`)
   - **No match, no output:** Convert normally

## User Workflows

### First-time Setup
1. Open app → default output folder is `./converted_u1`
2. Click ⚙️ Settings
3. Click 📁 to browse → select output folder
4. Click 📁 for source → select source folder
5. Settings auto-save

### Batch Convert with New Files
1. Open app → badge shows `Batch Convert (5 new)`
2. Click Batch Convert tab
3. See "5 new files ready to convert" with list
4. Click "Convert All"
5. Files saved as `filename_U1.3mf`
6. History updated, badge clears

### Re-convert Modified File
1. User modifies source file
2. Open app → detects hash changed
3. Shows file as "modified" in new files list
4. Convert → creates `filename_U1_v2.3mf`

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Output folder doesn't exist | Offer to create it |
| Can't write to output | Show error with path |
| Source folder invalid | Warning, disable monitoring |
| File locked | Skip with warning, continue others |
| Large batch | Progress bar, allow cancel |

## Constraints

- History capped at 1000 entries
- Clear history requires confirmation
- Folder browser limited to server filesystem
