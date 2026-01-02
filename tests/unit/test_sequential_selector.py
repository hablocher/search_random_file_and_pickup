"""Unit tests for sequential selector functionality."""

import pytest
from pathlib import Path
from random_file_picker.core.sequential_selector import (
    extract_number_from_filename,
    extract_collection_name,
    SequentialFileTracker,
    analyze_folder_sequence,
)


class TestExtractNumberFromFilename:
    """Tests for extract_number_from_filename function."""
    
    def test_simple_numbers(self):
        """Test extraction of simple numbers."""
        assert extract_number_from_filename("file001.txt") == (1.0, 'decimal')
        assert extract_number_from_filename("file01.txt") == (1.0, 'decimal')
        assert extract_number_from_filename("001.txt") == (1.0, 'decimal')
    
    def test_hash_numbers(self):
        """Test extraction of #-prefixed numbers."""
        assert extract_number_from_filename("file #001.txt") == (1.0, 'hash_decimal')
        assert extract_number_from_filename("#42.txt") == (42.0, 'hash_decimal')
    
    def test_x_of_y_format(self):
        """Test 'X de Y' format."""
        assert extract_number_from_filename("01 de 10.txt") == (1.0, 'x_of_y')
        assert extract_number_from_filename("05 of 20.txt") == (5.0, 'x_of_y')
    
    def test_chapter_format(self):
        """Test chapter/cap format."""
        assert extract_number_from_filename("Chapter 01.txt") == (1.0, 'chapter')
        assert extract_number_from_filename("Cap 05.txt") == (5.0, 'chapter')
        assert extract_number_from_filename("Capitulo 10.txt") == (10.0, 'chapter')
    
    def test_volume_format(self):
        """Test volume format."""
        assert extract_number_from_filename("Volume 01.txt") == (1.0, 'volume')
        assert extract_number_from_filename("Vol 03.txt") == (3.0, 'volume')
    
    def test_episode_format(self):
        """Test episode format."""
        assert extract_number_from_filename("Episode 01.txt") == (1.0, 'episode')
        assert extract_number_from_filename("Ep 05.txt") == (5.0, 'episode')
    
    def test_roman_numerals(self):
        """Test roman numeral extraction."""
        result = extract_number_from_filename("Part II.txt")
        assert result is not None
        assert result[0] == 2
        assert result[1] == 'roman'
    
    def test_no_number(self):
        """Test files without numbers."""
        assert extract_number_from_filename("random_file.txt") is None


class TestExtractCollectionName:
    """Tests for extract_collection_name function."""
    
    def test_simple_numbered_file(self):
        """Test extraction from simple numbered files."""
        assert extract_collection_name("Series Name 001.txt") == "Series Name"
        assert extract_collection_name("Book #05.txt") == "Book"
    
    def test_chapter_format(self):
        """Test extraction from chapter format."""
        assert extract_collection_name("My Story Chapter 01.txt") == "My Story"
        assert extract_collection_name("Adventure Cap 10.txt") == "Adventure"
    
    def test_x_of_y_format(self):
        """Test extraction from X of Y format."""
        assert extract_collection_name("Collection 01 de 10.txt") == "Collection"


class TestSequentialFileTracker:
    """Tests for SequentialFileTracker class."""
    
    @pytest.fixture
    def tracker(self, tmp_path):
        """Create a tracker with temporary file."""
        tracker_file = tmp_path / "test_tracker.json"
        return SequentialFileTracker(str(tracker_file))
    
    def test_mark_and_check_read(self, tracker, tmp_path):
        """Test marking files as read and checking status."""
        test_file = tmp_path / "test.txt"
        test_file.touch()
        
        assert not tracker.is_read(str(test_file))
        
        tracker.mark_as_read(str(test_file))
        
        assert tracker.is_read(str(test_file))
    
    def test_get_read_files(self, tracker, tmp_path):
        """Test getting list of read files."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.touch()
        file2.touch()
        
        tracker.mark_as_read(str(file1))
        tracker.mark_as_read(str(file2))
        
        read_files = tracker.get_read_files(str(tmp_path))
        
        assert len(read_files) == 2
        assert "file1.txt" in read_files
        assert "file2.txt" in read_files
    
    def test_reset_folder(self, tracker, tmp_path):
        """Test resetting a folder's tracking."""
        test_file = tmp_path / "test.txt"
        test_file.touch()
        
        tracker.mark_as_read(str(test_file))
        assert tracker.is_read(str(test_file))
        
        tracker.reset_folder(str(tmp_path))
        assert not tracker.is_read(str(test_file))


class TestAnalyzeFolderSequence:
    """Tests for analyze_folder_sequence function."""
    
    def test_detect_simple_sequence(self, tmp_path):
        """Test detection of simple numbered sequence."""
        for i in range(1, 6):
            (tmp_path / f"file{i:03d}.txt").touch()
        
        sequences = analyze_folder_sequence(tmp_path)
        
        assert sequences is not None
        assert len(sequences) > 0
        assert sequences[0]['count'] >= 5
    
    def test_detect_multiple_collections(self, tmp_path):
        """Test detection of multiple collections in same folder."""
        # Collection A
        for i in range(1, 4):
            (tmp_path / f"Series A - {i:02d}.txt").touch()
        
        # Collection B
        for i in range(1, 4):
            (tmp_path / f"Series B - {i:02d}.txt").touch()
        
        sequences = analyze_folder_sequence(tmp_path)
        
        assert sequences is not None
        assert len(sequences) == 2
    
    def test_no_sequence(self, tmp_path):
        """Test folder without sequences."""
        (tmp_path / "random1.txt").touch()
        (tmp_path / "other.txt").touch()
        
        sequences = analyze_folder_sequence(tmp_path)
        
        # Should return None or empty list if no sequence detected
        assert sequences is None or len(sequences) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
