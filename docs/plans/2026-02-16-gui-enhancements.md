# GUI Enhancements Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add configurable output folder, conversion history tracking, new file detection, and folder browser to the converter web UI.

**Architecture:** Server-side JSON storage for settings/history, new Flask API endpoints for settings/browsing/history, enhanced frontend with settings panel and folder browser modal.

**Tech Stack:** Flask (Python), Tailwind CSS, vanilla JavaScript, MD5 hashing for duplicate detection.

---

### Task 1: Add History Storage Module

**Files:**
- Create: `history.py`
- Test: `test_history.py`

**Step 1: Write the failing test**

```python
# test_history.py
import os
import tempfile
import pytest
from history import HistoryManager

def test_load_empty_history():
    with tempfile.TemporaryDirectory() as tmpdir:
        hm = HistoryManager(os.path.join(tmpdir, 'history.json'))
        assert hm.get_settings() == {
            'output_folder': './converted_u1',
            'source_folder': '',
            'auto_detect': True,
            'delete_duplicates': True
        }
        assert hm.get_converted() == []
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest test_history.py::test_load_empty_history -v`
Expected: FAIL with "No module named 'history'"

**Step 3: Write minimal implementation**

```python
# history.py
import os
import json
import hashlib
from datetime import datetime

DEFAULT_SETTINGS = {
    'output_folder': './converted_u1',
    'source_folder': '',
    'auto_detect': True,
    'delete_duplicates': True
}

class HistoryManager:
    def __init__(self, filepath='conversion_history.json'):
        self.filepath = filepath
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                self.settings = data.get('settings', DEFAULT_SETTINGS.copy())
                self.converted = data.get('converted', [])
        else:
            self.settings = DEFAULT_SETTINGS.copy()
            self.converted = []

    def _save(self):
        with open(self.filepath, 'w') as f:
            json.dump({
                'settings': self.settings,
                'converted': self.converted
            }, f, indent=2)

    def get_settings(self):
        return self.settings.copy()

    def update_settings(self, new_settings):
        self.settings.update(new_settings)
        self._save()

    def get_converted(self):
        return self.converted.copy()

    def add_converted(self, source, source_hash, output, filaments):
        entry = {
            'source': source,
            'source_hash': source_hash,
            'output': output,
            'timestamp': datetime.now().isoformat(),
            'filaments': filaments
        }
        self.converted.append(entry)
        # Cap at 1000 entries
        if len(self.converted) > 1000:
            self.converted = self.converted[-1000:]
        self._save()

    def find_by_hash(self, source_hash):
        for entry in self.converted:
            if entry.get('source_hash') == source_hash:
                return entry
        return None

    def clear_history(self):
        self.converted = []
        self._save()

    @staticmethod
    def hash_file(filepath):
        hash_md5 = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest test_history.py::test_load_empty_history -v`
Expected: PASS

**Step 5: Commit**

```bash
git add history.py test_history.py
git commit -m "feat: add history storage module"
```

---

### Task 2: Add More History Tests

**Files:**
- Modify: `test_history.py`

**Step 1: Write additional tests**

```python
# Add to test_history.py

def test_save_and_load_settings():
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, 'history.json')
        hm = HistoryManager(filepath)
        hm.update_settings({'output_folder': '/mnt/e/3d/output'})

        # Reload and verify
        hm2 = HistoryManager(filepath)
        assert hm2.get_settings()['output_folder'] == '/mnt/e/3d/output'

def test_add_converted_entry():
    with tempfile.TemporaryDirectory() as tmpdir:
        hm = HistoryManager(os.path.join(tmpdir, 'history.json'))
        hm.add_converted('cat.3mf', 'abc123', 'cat_U1.3mf', 3)

        converted = hm.get_converted()
        assert len(converted) == 1
        assert converted[0]['source'] == 'cat.3mf'
        assert converted[0]['source_hash'] == 'abc123'

def test_find_by_hash():
    with tempfile.TemporaryDirectory() as tmpdir:
        hm = HistoryManager(os.path.join(tmpdir, 'history.json'))
        hm.add_converted('cat.3mf', 'abc123', 'cat_U1.3mf', 3)

        found = hm.find_by_hash('abc123')
        assert found is not None
        assert found['source'] == 'cat.3mf'

        not_found = hm.find_by_hash('xyz999')
        assert not_found is None

def test_clear_history():
    with tempfile.TemporaryDirectory() as tmpdir:
        hm = HistoryManager(os.path.join(tmpdir, 'history.json'))
        hm.add_converted('cat.3mf', 'abc123', 'cat_U1.3mf', 3)
        hm.clear_history()
        assert hm.get_converted() == []
```

**Step 2: Run tests**

Run: `python3 -m pytest test_history.py -v`
Expected: All PASS

**Step 3: Commit**

```bash
git add test_history.py
git commit -m "test: add comprehensive history manager tests"
```

---

### Task 3: Add Settings API Endpoints

**Files:**
- Modify: `app.py`

**Step 1: Import and initialize HistoryManager in app.py**

Add after existing imports:
```python
from history import HistoryManager

# Initialize history manager
history_manager = HistoryManager('conversion_history.json')
```

**Step 2: Add settings endpoints**

Add before `if __name__ == '__main__':`:
```python
@app.route('/settings', methods=['GET'])
def get_settings():
    """Get current settings."""
    return jsonify(history_manager.get_settings())

@app.route('/settings', methods=['POST'])
def update_settings():
    """Update settings."""
    data = request.json
    history_manager.update_settings(data)
    return jsonify({'success': True, 'settings': history_manager.get_settings()})

@app.route('/history', methods=['GET'])
def get_history():
    """Get conversion history."""
    return jsonify(history_manager.get_converted())

@app.route('/history/clear', methods=['POST'])
def clear_history():
    """Clear conversion history."""
    history_manager.clear_history()
    return jsonify({'success': True})
```

**Step 3: Test manually**

Run: `curl http://localhost:8085/settings`
Expected: JSON with default settings

**Step 4: Commit**

```bash
git add app.py
git commit -m "feat: add settings and history API endpoints"
```

---

### Task 4: Add Folder Browser Endpoint

**Files:**
- Modify: `app.py`

**Step 1: Add browse endpoint**

```python
@app.route('/browse', methods=['GET'])
def browse_directory():
    """List contents of a directory for folder browser."""
    path = request.args.get('path', '')

    # Default to common roots
    if not path:
        # Return drive letters on Windows, root dirs on Linux
        if os.name == 'nt':
            import string
            drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
            return jsonify({'path': '', 'dirs': drives, 'is_root': True})
        else:
            path = '/'

    # Normalize path
    path = os.path.normpath(path)

    if not os.path.isdir(path):
        return jsonify({'error': 'Path is not a directory'}), 400

    try:
        entries = []
        for name in sorted(os.listdir(path)):
            full_path = os.path.join(path, name)
            if os.path.isdir(full_path):
                entries.append({
                    'name': name,
                    'path': full_path,
                    'type': 'dir'
                })
        return jsonify({
            'path': path,
            'parent': os.path.dirname(path) if path != '/' else None,
            'dirs': entries
        })
    except PermissionError:
        return jsonify({'error': 'Permission denied'}), 403
```

**Step 2: Test manually**

Run: `curl "http://localhost:8085/browse?path=/mnt/e"`
Expected: JSON with directory listing

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add folder browser API endpoint"
```

---

### Task 5: Add Check-New Endpoint

**Files:**
- Modify: `app.py`

**Step 1: Add check-new endpoint**

```python
@app.route('/check-new', methods=['GET'])
def check_new_files():
    """Find unconverted files in source folder."""
    settings = history_manager.get_settings()
    source_folder = settings.get('source_folder', '')

    if not source_folder or not os.path.isdir(source_folder):
        return jsonify({'new_files': [], 'error': 'Source folder not configured'})

    new_files = []

    for filename in os.listdir(source_folder):
        if not filename.lower().endswith('.3mf'):
            continue

        filepath = os.path.join(source_folder, filename)
        if not os.path.isfile(filepath):
            continue

        # Check if it's a Bambu file
        if not is_bambu_file(filepath):
            continue

        # Hash the file
        file_hash = history_manager.hash_file(filepath)

        # Check if already converted
        existing = history_manager.find_by_hash(file_hash)
        if existing:
            continue

        # Parse filaments for preview
        filaments = parse_bambu_filaments(filepath)

        new_files.append({
            'filename': filename,
            'filepath': filepath,
            'hash': file_hash,
            'filaments': len(filaments)
        })

    return jsonify({'new_files': new_files, 'count': len(new_files)})
```

**Step 2: Test manually**

Run: `curl http://localhost:8085/check-new`
Expected: JSON with new files list

**Step 3: Commit**

```bash
git add app.py
git commit -m "feat: add check-new endpoint for detecting unconverted files"
```

---

### Task 6: Update Batch Convert to Use History

**Files:**
- Modify: `app.py`

**Step 1: Modify batch_convert to record history and use output folder**

Update the `batch_convert` function to:
1. Get output folder from settings
2. Record each conversion in history
3. Handle duplicates with versioning

```python
@app.route('/batch-convert', methods=['POST'])
def batch_convert():
    """Convert all files in a batch session."""
    data = request.json
    batch_session_id = data.get('batch_session_id')
    if not batch_session_id:
        return jsonify({'error': 'No batch session ID provided'}), 400

    batch_folder = os.path.join(app.config['UPLOAD_FOLDER'], f"batch_{batch_session_id}")
    if not os.path.exists(batch_folder):
        return jsonify({'error': 'Batch session expired or not found'}), 404

    # Get output folder from settings
    settings = history_manager.get_settings()
    output_folder = settings.get('output_folder', './converted_u1')
    os.makedirs(output_folder, exist_ok=True)

    files_to_convert = data.get('files', [])
    if not files_to_convert:
        files_to_convert = [f for f in os.listdir(batch_folder) if f.endswith('.3mf')]

    converted_files = []
    skipped_files = []
    errors = []

    for file_info in files_to_convert:
        if isinstance(file_info, dict):
            filename = file_info.get('filename')
            auto_colors = file_info.get('auto_colors', {})
        else:
            filename = file_info
            input_path = os.path.join(batch_folder, filename)
            filaments = parse_bambu_filaments(input_path)
            auto_colors = auto_map_filaments(filaments)

        input_path = os.path.join(batch_folder, filename)
        if not os.path.exists(input_path):
            errors.append({'filename': filename, 'error': 'File not found'})
            continue

        # Calculate hash
        file_hash = history_manager.hash_file(input_path)

        # Check if exact duplicate
        existing = history_manager.find_by_hash(file_hash)
        if existing and settings.get('delete_duplicates', True):
            skipped_files.append({'filename': filename, 'reason': 'Already converted'})
            continue

        # Generate output filename with versioning
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_U1.3mf"
        output_path = os.path.join(output_folder, output_filename)

        # Version if exists
        version = 2
        while os.path.exists(output_path):
            output_filename = f"{base_name}_U1_v{version}.3mf"
            output_path = os.path.join(output_folder, output_filename)
            version += 1

        filaments = parse_bambu_filaments(input_path)
        success, error = convert_single_file(input_path, output_path, auto_colors)

        if success:
            converted_files.append(output_filename)
            history_manager.add_converted(filename, file_hash, output_filename, len(filaments))
        else:
            errors.append({'filename': filename, 'error': error})

    # Clean up batch folder
    shutil.rmtree(batch_folder, ignore_errors=True)

    return jsonify({
        'converted_count': len(converted_files),
        'converted_files': converted_files,
        'skipped_count': len(skipped_files),
        'skipped_files': skipped_files,
        'error_count': len(errors),
        'errors': errors,
        'output_folder': output_folder
    })
```

**Step 2: Commit**

```bash
git add app.py
git commit -m "feat: integrate history tracking into batch convert"
```

---

### Task 7: Add Settings Panel to Frontend

**Files:**
- Modify: `templates/index.html`

**Step 1: Add settings button to header**

After the info button in the header paragraph:
```html
<button id="settings-btn" class="ml-2 text-cyan-400 hover:text-cyan-300 transition-colors">
    <i class="fa-solid fa-gear"></i>
</button>
```

**Step 2: Add settings panel HTML**

After the info-modal div:
```html
<!-- Settings Panel -->
<div id="settings-panel" class="hidden fixed inset-y-0 right-0 w-80 bg-slate-800 border-l border-slate-600 shadow-2xl z-50 transform transition-transform">
    <div class="p-6">
        <div class="flex justify-between items-center mb-6">
            <h3 class="text-lg font-bold text-cyan-400"><i class="fa-solid fa-gear mr-2"></i>Settings</h3>
            <button id="close-settings" class="text-slate-400 hover:text-white transition-colors">
                <i class="fa-solid fa-xmark text-xl"></i>
            </button>
        </div>

        <div class="space-y-4">
            <div>
                <label class="block text-sm text-slate-400 mb-1">Output Folder:</label>
                <div class="flex gap-2">
                    <input type="text" id="output-folder" class="flex-1 bg-slate-700 border border-slate-600 rounded px-3 py-2 text-sm text-white" placeholder="./converted_u1">
                    <button id="browse-output" class="bg-slate-600 hover:bg-slate-500 px-3 py-2 rounded">
                        <i class="fa-solid fa-folder-open"></i>
                    </button>
                </div>
            </div>

            <div>
                <label class="block text-sm text-slate-400 mb-1">Source Folder (for monitoring):</label>
                <div class="flex gap-2">
                    <input type="text" id="source-folder" class="flex-1 bg-slate-700 border border-slate-600 rounded px-3 py-2 text-sm text-white" placeholder="E:\Downloads">
                    <button id="browse-source" class="bg-slate-600 hover:bg-slate-500 px-3 py-2 rounded">
                        <i class="fa-solid fa-folder-open"></i>
                    </button>
                </div>
            </div>

            <div class="flex items-center gap-2">
                <input type="checkbox" id="auto-detect" class="w-4 h-4" checked>
                <label for="auto-detect" class="text-sm text-slate-300">Auto-detect new files</label>
            </div>

            <div class="flex items-center gap-2">
                <input type="checkbox" id="delete-duplicates" class="w-4 h-4" checked>
                <label for="delete-duplicates" class="text-sm text-slate-300">Skip exact duplicates</label>
            </div>

            <hr class="border-slate-600">

            <div>
                <p class="text-sm text-slate-400">History: <span id="history-count">0</span> files converted</p>
                <div class="flex gap-2 mt-2">
                    <button id="view-history" class="text-sm text-cyan-400 hover:text-cyan-300">View History</button>
                    <button id="clear-history" class="text-sm text-red-400 hover:text-red-300">Clear History</button>
                </div>
            </div>
        </div>
    </div>
</div>
```

**Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat: add settings panel HTML structure"
```

---

### Task 8: Add Folder Browser Modal

**Files:**
- Modify: `templates/index.html`

**Step 1: Add folder browser modal HTML**

After settings panel:
```html
<!-- Folder Browser Modal -->
<div id="folder-browser" class="hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-slate-800 border border-slate-600 rounded-xl p-6 w-96 max-h-96 shadow-2xl">
        <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-bold text-cyan-400"><i class="fa-solid fa-folder-tree mr-2"></i>Select Folder</h3>
            <button id="close-browser" class="text-slate-400 hover:text-white transition-colors">
                <i class="fa-solid fa-xmark text-xl"></i>
            </button>
        </div>

        <div id="current-path" class="text-sm text-slate-400 mb-2 truncate"></div>

        <div id="folder-list" class="bg-slate-700 rounded border border-slate-600 h-48 overflow-y-auto mb-4">
            <!-- Folders will be populated here -->
        </div>

        <div class="flex gap-2">
            <button id="browser-up" class="bg-slate-600 hover:bg-slate-500 px-3 py-2 rounded text-sm">
                <i class="fa-solid fa-arrow-up mr-1"></i>Up
            </button>
            <button id="browser-select" class="flex-1 bg-cyan-600 hover:bg-cyan-500 px-3 py-2 rounded text-sm font-medium">
                Select This Folder
            </button>
        </div>
    </div>
</div>
```

**Step 2: Commit**

```bash
git add templates/index.html
git commit -m "feat: add folder browser modal HTML"
```

---

### Task 9: Add Badge to Batch Tab

**Files:**
- Modify: `templates/index.html`

**Step 1: Update batch mode button to include badge**

Change:
```html
<button id="batch-mode-btn" class="px-4 py-2 rounded-md text-sm font-medium transition-all text-slate-400 hover:text-white">
    <i class="fa-solid fa-folder-open mr-2"></i>Batch Convert
</button>
```

To:
```html
<button id="batch-mode-btn" class="px-4 py-2 rounded-md text-sm font-medium transition-all text-slate-400 hover:text-white relative">
    <i class="fa-solid fa-folder-open mr-2"></i>Batch Convert
    <span id="new-files-badge" class="hidden absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">0</span>
</button>
```

**Step 2: Commit**

```bash
git add templates/index.html
git commit -m "feat: add new files badge to batch tab"
```

---

### Task 10: Add Settings JavaScript

**Files:**
- Modify: `templates/index.html`

**Step 1: Add settings JavaScript at end of script section**

```javascript
// ========== SETTINGS ==========
let currentSettings = {};
let browserTarget = null; // 'output' or 'source'
let currentBrowsePath = '';

// Load settings on page load
async function loadSettings() {
    try {
        const res = await fetch('/settings');
        currentSettings = await res.json();
        document.getElementById('output-folder').value = currentSettings.output_folder || '';
        document.getElementById('source-folder').value = currentSettings.source_folder || '';
        document.getElementById('auto-detect').checked = currentSettings.auto_detect !== false;
        document.getElementById('delete-duplicates').checked = currentSettings.delete_duplicates !== false;

        // Load history count
        const histRes = await fetch('/history');
        const history = await histRes.json();
        document.getElementById('history-count').textContent = history.length;

        // Check for new files
        if (currentSettings.auto_detect && currentSettings.source_folder) {
            checkNewFiles();
        }
    } catch (e) {
        console.error('Failed to load settings:', e);
    }
}

async function saveSettings() {
    const settings = {
        output_folder: document.getElementById('output-folder').value,
        source_folder: document.getElementById('source-folder').value,
        auto_detect: document.getElementById('auto-detect').checked,
        delete_duplicates: document.getElementById('delete-duplicates').checked
    };
    try {
        await fetch('/settings', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(settings)
        });
        currentSettings = settings;
        if (settings.auto_detect && settings.source_folder) {
            checkNewFiles();
        }
    } catch (e) {
        console.error('Failed to save settings:', e);
    }
}

async function checkNewFiles() {
    try {
        const res = await fetch('/check-new');
        const data = await res.json();
        const badge = document.getElementById('new-files-badge');
        if (data.count > 0) {
            badge.textContent = data.count > 99 ? '99+' : data.count;
            badge.classList.remove('hidden');
        } else {
            badge.classList.add('hidden');
        }
    } catch (e) {
        console.error('Failed to check new files:', e);
    }
}

// Settings panel toggle
document.getElementById('settings-btn').addEventListener('click', () => {
    document.getElementById('settings-panel').classList.remove('hidden');
});
document.getElementById('close-settings').addEventListener('click', () => {
    document.getElementById('settings-panel').classList.add('hidden');
    saveSettings();
});

// Auto-save on input change
['output-folder', 'source-folder', 'auto-detect', 'delete-duplicates'].forEach(id => {
    document.getElementById(id).addEventListener('change', saveSettings);
});

// Clear history
document.getElementById('clear-history').addEventListener('click', async () => {
    if (confirm('Clear all conversion history?')) {
        await fetch('/history/clear', { method: 'POST' });
        document.getElementById('history-count').textContent = '0';
    }
});

// Load settings on page load
loadSettings();
```

**Step 2: Commit**

```bash
git add templates/index.html
git commit -m "feat: add settings panel JavaScript functionality"
```

---

### Task 11: Add Folder Browser JavaScript

**Files:**
- Modify: `templates/index.html`

**Step 1: Add folder browser JavaScript**

```javascript
// ========== FOLDER BROWSER ==========
async function openBrowser(target) {
    browserTarget = target;
    currentBrowsePath = '';
    document.getElementById('folder-browser').classList.remove('hidden');
    await loadFolderContents('');
}

async function loadFolderContents(path) {
    try {
        const res = await fetch(`/browse?path=${encodeURIComponent(path)}`);
        const data = await res.json();

        if (data.error) {
            alert(data.error);
            return;
        }

        currentBrowsePath = data.path || '';
        document.getElementById('current-path').textContent = currentBrowsePath || 'Select a drive';

        const list = document.getElementById('folder-list');
        list.innerHTML = '';

        if (data.dirs) {
            data.dirs.forEach(dir => {
                const item = document.createElement('div');
                item.className = 'px-3 py-2 hover:bg-slate-600 cursor-pointer flex items-center gap-2';
                item.innerHTML = `<i class="fa-solid fa-folder text-yellow-400"></i><span class="truncate">${dir.name || dir}</span>`;
                item.addEventListener('click', () => {
                    loadFolderContents(dir.path || dir);
                });
                list.appendChild(item);
            });
        }

        // Show/hide up button
        document.getElementById('browser-up').style.display = data.parent ? 'block' : 'none';
    } catch (e) {
        console.error('Failed to browse:', e);
    }
}

document.getElementById('browse-output').addEventListener('click', () => openBrowser('output'));
document.getElementById('browse-source').addEventListener('click', () => openBrowser('source'));

document.getElementById('close-browser').addEventListener('click', () => {
    document.getElementById('folder-browser').classList.add('hidden');
});

document.getElementById('browser-up').addEventListener('click', async () => {
    const res = await fetch(`/browse?path=${encodeURIComponent(currentBrowsePath)}`);
    const data = await res.json();
    if (data.parent) {
        loadFolderContents(data.parent);
    }
});

document.getElementById('browser-select').addEventListener('click', () => {
    if (currentBrowsePath) {
        if (browserTarget === 'output') {
            document.getElementById('output-folder').value = currentBrowsePath;
        } else if (browserTarget === 'source') {
            document.getElementById('source-folder').value = currentBrowsePath;
        }
        saveSettings();
    }
    document.getElementById('folder-browser').classList.add('hidden');
});
```

**Step 2: Commit**

```bash
git add templates/index.html
git commit -m "feat: add folder browser JavaScript functionality"
```

---

### Task 12: Update Batch UI to Show New Files

**Files:**
- Modify: `templates/index.html`

**Step 1: Add new files section to batch mode**

Add before batch-step1 div in batch-mode section:
```html
<!-- New Files Alert -->
<div id="new-files-alert" class="hidden mb-4 bg-green-900 border border-green-700 rounded-lg p-4">
    <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
            <i class="fa-solid fa-bell text-green-400"></i>
            <span class="text-green-300"><span id="new-files-count">0</span> new files ready to convert</span>
        </div>
        <button id="convert-new-btn" class="bg-green-600 hover:bg-green-500 text-white px-4 py-1 rounded text-sm">
            Convert All New
        </button>
    </div>
</div>
```

**Step 2: Update checkNewFiles to show alert**

```javascript
async function checkNewFiles() {
    try {
        const res = await fetch('/check-new');
        const data = await res.json();
        const badge = document.getElementById('new-files-badge');
        const alert = document.getElementById('new-files-alert');
        const count = document.getElementById('new-files-count');

        if (data.count > 0) {
            badge.textContent = data.count > 99 ? '99+' : data.count;
            badge.classList.remove('hidden');
            count.textContent = data.count;
            alert.classList.remove('hidden');
            window.newFilesData = data.new_files;
        } else {
            badge.classList.add('hidden');
            alert.classList.add('hidden');
        }
    } catch (e) {
        console.error('Failed to check new files:', e);
    }
}
```

**Step 3: Commit**

```bash
git add templates/index.html
git commit -m "feat: add new files alert to batch mode"
```

---

### Task 13: Final Integration Test

**Step 1: Start the app**

Run: `python3 app.py`

**Step 2: Test settings**
1. Open http://localhost:8085
2. Click gear icon - settings panel should open
3. Click folder browse - should show directory tree
4. Select output folder
5. Select source folder
6. Close settings - should save

**Step 3: Test new file detection**
1. With source folder configured, should see badge if new files exist
2. Click Batch Convert tab - should show new files alert

**Step 4: Test batch convert with history**
1. Upload files via batch mode
2. Convert - should save to configured output folder
3. Check history count increased
4. Try same files again - should skip as duplicates

**Step 5: Commit final changes**

```bash
git add .
git commit -m "feat: complete GUI enhancements with settings, history, and folder browser"
git push fork main
```

---

Plan complete and saved to `docs/plans/2026-02-16-gui-enhancements.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?