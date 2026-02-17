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
