# test_history.py
import os
import tempfile
import pytest
from history import HistoryManager

def test_load_empty_history():
    """Test that a new history manager has default settings and empty converted list."""
    with tempfile.TemporaryDirectory() as tmpdir:
        hm = HistoryManager(os.path.join(tmpdir, 'history.json'))
        assert hm.get_settings() == {
            'output_folder': './converted_u1',
            'source_folder': '',
            'auto_detect': True,
            'delete_duplicates': True
        }
        assert hm.get_converted() == []


def test_update_settings():
    """Test that settings can be updated and persisted."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, 'history.json')
        hm = HistoryManager(filepath)

        # Update settings
        hm.update_settings({'output_folder': '/custom/path', 'auto_detect': False})

        # Verify update
        settings = hm.get_settings()
        assert settings['output_folder'] == '/custom/path'
        assert settings['auto_detect'] == False
        assert settings['source_folder'] == ''  # unchanged

        # Verify persistence by loading fresh
        hm2 = HistoryManager(filepath)
        settings2 = hm2.get_settings()
        assert settings2['output_folder'] == '/custom/path'
        assert settings2['auto_detect'] == False


def test_add_converted():
    """Test adding converted file entries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, 'history.json')
        hm = HistoryManager(filepath)

        # Add a converted entry
        hm.add_converted(
            source='test.3mf',
            source_hash='abc123',
            output='test_U1.3mf',
            filaments=[{'color': '#FF0000', 'type': 'PLA'}]
        )

        converted = hm.get_converted()
        assert len(converted) == 1
        assert converted[0]['source'] == 'test.3mf'
        assert converted[0]['source_hash'] == 'abc123'
        assert converted[0]['output'] == 'test_U1.3mf'
        assert 'timestamp' in converted[0]
        assert converted[0]['filaments'] == [{'color': '#FF0000', 'type': 'PLA'}]


def test_find_by_hash():
    """Test finding a converted entry by source hash."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, 'history.json')
        hm = HistoryManager(filepath)

        # Add entries
        hm.add_converted('file1.3mf', 'hash1', 'file1_U1.3mf', [])
        hm.add_converted('file2.3mf', 'hash2', 'file2_U1.3mf', [])

        # Find by hash
        result = hm.find_by_hash('hash1')
        assert result is not None
        assert result['source'] == 'file1.3mf'

        # Not found
        result = hm.find_by_hash('nonexistent')
        assert result is None


def test_clear_history():
    """Test clearing the conversion history."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, 'history.json')
        hm = HistoryManager(filepath)

        # Add entries
        hm.add_converted('file1.3mf', 'hash1', 'file1_U1.3mf', [])
        hm.add_converted('file2.3mf', 'hash2', 'file2_U1.3mf', [])
        assert len(hm.get_converted()) == 2

        # Clear
        hm.clear_history()
        assert hm.get_converted() == []

        # Verify persistence
        hm2 = HistoryManager(filepath)
        assert hm2.get_converted() == []


def test_history_cap_at_1000():
    """Test that history is capped at 1000 entries."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, 'history.json')
        hm = HistoryManager(filepath)

        # Add 1005 entries
        for i in range(1005):
            hm.add_converted(f'file{i}.3mf', f'hash{i}', f'file{i}_U1.3mf', [])

        converted = hm.get_converted()
        assert len(converted) == 1000
        # Should keep the most recent entries (last 1000)
        assert converted[0]['source'] == 'file5.3mf'
        assert converted[-1]['source'] == 'file1004.3mf'


def test_hash_file():
    """Test file hashing functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file
        test_file = os.path.join(tmpdir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('Hello, World!')

        hash1 = HistoryManager.hash_file(test_file)
        assert isinstance(hash1, str)
        assert len(hash1) == 32  # MD5 produces 32 hex characters

        # Same content should produce same hash
        hash2 = HistoryManager.hash_file(test_file)
        assert hash1 == hash2

        # Different content should produce different hash
        test_file2 = os.path.join(tmpdir, 'test2.txt')
        with open(test_file2, 'w') as f:
            f.write('Different content')
        hash3 = HistoryManager.hash_file(test_file2)
        assert hash1 != hash3


def test_persistence_across_sessions():
    """Test that data persists correctly across multiple sessions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, 'history.json')

        # Session 1: Add data
        hm1 = HistoryManager(filepath)
        hm1.update_settings({'source_folder': '/my/source'})
        hm1.add_converted('test.3mf', 'testhash', 'test_U1.3mf', [{'color': '#00FF00', 'type': 'PETG'}])

        # Session 2: Verify data
        hm2 = HistoryManager(filepath)
        assert hm2.get_settings()['source_folder'] == '/my/source'
        converted = hm2.get_converted()
        assert len(converted) == 1
        assert converted[0]['source_hash'] == 'testhash'
