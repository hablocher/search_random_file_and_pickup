"""Unit tests for file picker core functionality."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

from random_file_picker.core.file_picker import (
    is_file_accessible,
    collect_files,
    pick_random_file,
    list_files_in_zip,
)


class TestIsFileAccessible:
    """Tests for is_file_accessible function."""
    
    def test_accessible_file(self, tmp_path):
        """Test that accessible files return True."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        assert is_file_accessible(test_file) is True
    
    def test_nonexistent_file(self, tmp_path):
        """Test that nonexistent files return False."""
        test_file = tmp_path / "nonexistent.txt"
        
        assert is_file_accessible(test_file) is False
    
    def test_empty_file(self, tmp_path):
        """Test that empty files are considered accessible."""
        test_file = tmp_path / "empty.txt"
        test_file.touch()
        
        assert is_file_accessible(test_file) is True


class TestCollectFiles:
    """Tests for collect_files function."""
    
    def test_collect_files_from_folder(self, tmp_path):
        """Test collecting files from a folder."""
        # Create test files
        (tmp_path / "file1.txt").write_text("content")
        (tmp_path / "file2.txt").write_text("content")
        (tmp_path / "_L_file3.txt").write_text("content")  # Should be excluded
        
        files = collect_files([str(tmp_path)])
        
        assert len(files) == 2
        assert any("file1.txt" in f for f in files)
        assert any("file2.txt" in f for f in files)
        assert not any("_L_file3.txt" in f for f in files)
    
    def test_collect_files_with_keywords(self, tmp_path):
        """Test collecting files with keyword filtering."""
        (tmp_path / "important_doc.txt").write_text("content")
        (tmp_path / "random_file.txt").write_text("content")
        (tmp_path / "document.txt").write_text("content")
        
        files = collect_files([str(tmp_path)], keywords=["important", "document"])
        
        assert len(files) == 2
        assert any("important_doc.txt" in f for f in files)
        assert any("document.txt" in f for f in files)
        assert not any("random_file.txt" in f for f in files)
    
    def test_collect_files_ignores_hidden_folders(self, tmp_path):
        """Test that hidden folders (starting with .) are ignored."""
        # Create hidden folder
        hidden_folder = tmp_path / ".hidden"
        hidden_folder.mkdir()
        (hidden_folder / "file.txt").write_text("content")
        
        # Create normal folder
        (tmp_path / "normal.txt").write_text("content")
        
        files = collect_files([str(tmp_path)])
        
        assert len(files) == 1
        assert not any(".hidden" in f for f in files)
    
    def test_collect_files_recursive(self, tmp_path):
        """Test recursive file collection."""
        # Create nested structure
        sub_folder = tmp_path / "subfolder"
        sub_folder.mkdir()
        (tmp_path / "root_file.txt").write_text("content")
        (sub_folder / "sub_file.txt").write_text("content")
        
        files = collect_files([str(tmp_path)])
        
        assert len(files) == 2
        assert any("root_file.txt" in f for f in files)
        assert any("sub_file.txt" in f for f in files)


class TestPickRandomFile:
    """Tests for pick_random_file function."""
    
    def test_pick_random_file_success(self, tmp_path):
        """Test successful random file selection."""
        # Create test files
        for i in range(5):
            (tmp_path / f"file{i}.txt").write_text("content")
        
        selected = pick_random_file([str(tmp_path)])
        
        assert selected is not None
        assert Path(selected).exists()
        assert Path(selected).parent == tmp_path
    
    def test_pick_random_file_no_files(self, tmp_path):
        """Test ValueError when no valid files found."""
        with pytest.raises(ValueError, match="Nenhum arquivo válido encontrado"):
            pick_random_file([str(tmp_path)])
    
    def test_pick_random_file_with_keywords(self, tmp_path):
        """Test random file selection with keywords."""
        (tmp_path / "important.txt").write_text("content")
        (tmp_path / "other.txt").write_text("content")
        
        selected = pick_random_file([str(tmp_path)], keywords=["important"])
        
        assert "important.txt" in selected


class TestListFilesInZip:
    """Tests for ZIP file handling."""
    
    @pytest.fixture
    def sample_zip(self, tmp_path):
        """Create a sample ZIP file for testing."""
        import zipfile
        
        zip_path = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_path, 'w') as zf:
            zf.writestr("file1.txt", "content1")
            zf.writestr("file2.txt", "content2")
            zf.writestr("_L_file3.txt", "content3")  # Should be excluded
            zf.writestr("subfolder/file4.txt", "content4")
        
        return zip_path
    
    def test_list_files_in_zip(self, sample_zip):
        """Test listing files in a ZIP."""
        files = list_files_in_zip(str(sample_zip))
        
        assert len(files) >= 2
        assert not any("_L_" in f for f in files)
    
    def test_list_files_in_zip_with_keywords(self, sample_zip):
        """Test listing files in ZIP with keywords."""
        # Add a specific file
        import zipfile
        with zipfile.ZipFile(sample_zip, 'a') as zf:
            zf.writestr("important_doc.txt", "content")
        
        files = list_files_in_zip(str(sample_zip), keywords=["important"])
        
        assert len(files) == 1
        assert "important_doc.txt" in files[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
