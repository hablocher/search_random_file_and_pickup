"""Shared fixtures for pytest."""

import pytest
from pathlib import Path


@pytest.fixture
def sample_files_folder(tmp_path):
    """Create a temporary folder with sample files."""
    files = [
        "comic_001.cbr",
        "comic_002.cbr",
        "comic_003.cbr",
        "_L_read_file.cbr",
        "random.txt",
    ]
    
    for filename in files:
        (tmp_path / filename).write_text("sample content")
    
    return tmp_path


@pytest.fixture
def empty_folder(tmp_path):
    """Create an empty temporary folder."""
    return tmp_path


@pytest.fixture
def mock_config_file(tmp_path):
    """Create a mock config.json file."""
    import json
    
    config = {
        "folders": [str(tmp_path)],
        "exclude_prefix": "_L_",
        "open_folder": True,
        "open_file": False,
        "use_sequence": True,
        "history_limit": 5,
        "keywords": "",
        "file_history": []
    }
    
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config, indent=2))
    
    return config_file
