import pytest
import tempfile
import os
from pypdf import PdfWriter
from split_pdf import parse_page_ranges, validate_page_ranges, group_consecutive_pages


class TestParsePageRanges:
    """Test page range parsing functionality."""
    
    def test_single_page(self):
        """Test parsing single page number."""
        result = parse_page_ranges("5")
        assert result == [4]  # 0-indexed
    
    def test_simple_range(self):
        """Test parsing simple range."""
        result = parse_page_ranges("1-3")
        assert result == [0, 1, 2]  # 0-indexed
    
    def test_complex_ranges(self):
        """Test parsing complex ranges with mixed formats."""
        result = parse_page_ranges("1-3,5,7-9,12")
        assert result == [0, 1, 2, 4, 6, 7, 8, 11]  # 0-indexed
    
    def test_unordered_ranges(self):
        """Test that result is sorted even with unordered input."""
        result = parse_page_ranges("9,1-3,5")
        assert result == [0, 1, 2, 4, 8]  # 0-indexed and sorted
    
    def test_overlapping_ranges(self):
        """Test overlapping ranges are handled correctly."""
        result = parse_page_ranges("1-5,3-7,6")
        assert result == [0, 1, 2, 3, 4, 5, 6]  # No duplicates
    
    def test_spaces_in_input(self):
        """Test handling of spaces in input."""
        result = parse_page_ranges(" 1 - 3 , 5 , 7 - 9 ")
        assert result == [0, 1, 2, 4, 6, 7, 8]
    
    def test_empty_string(self):
        """Test empty string raises error."""
        with pytest.raises(ValueError, match="Page ranges cannot be empty"):
            parse_page_ranges("")
    
    def test_empty_whitespace(self):
        """Test whitespace-only string raises error."""
        with pytest.raises(ValueError, match="Page ranges cannot be empty"):
            parse_page_ranges("   ")
    
    def test_invalid_range_format(self):
        """Test invalid range format."""
        with pytest.raises(ValueError, match="Invalid page number"):
            parse_page_ranges("1-2-3")
    
    def test_non_numeric_input(self):
        """Test non-numeric input."""
        with pytest.raises(ValueError, match="Invalid page number"):
            parse_page_ranges("1,abc,3")
    
    def test_zero_page_number(self):
        """Test zero page number."""
        with pytest.raises(ValueError, match="Page numbers must be positive"):
            parse_page_ranges("0,1,2")
    
    def test_negative_page_number(self):
        """Test negative page number."""
        with pytest.raises(ValueError, match="Page numbers must be positive"):
            parse_page_ranges("1,-2,3")
    
    def test_invalid_range_order(self):
        """Test invalid range where start > end."""
        with pytest.raises(ValueError, match="Invalid range"):
            parse_page_ranges("5-2")
    
    def test_empty_range_parts(self):
        """Test handling of empty range parts."""
        result = parse_page_ranges("1,,3")
        assert result == [0, 2]


class TestValidatePageRanges:
    """Test page range validation."""
    
    def test_valid_ranges(self):
        """Test valid page ranges."""
        # Should not raise any exception
        validate_page_ranges([0, 1, 4], 5)
    
    def test_out_of_bounds_page(self):
        """Test out of bounds page number."""
        with pytest.raises(ValueError, match="Page 6 is out of bounds"):
            validate_page_ranges([0, 1, 5], 5)  # Page 6 (1-indexed) out of bounds for 5-page PDF
    
    def test_boundary_pages(self):
        """Test boundary page numbers."""
        # Last page should be valid
        validate_page_ranges([4], 5)  # Page 5 (1-indexed) for 5-page PDF


class TestGroupConsecutivePages:
    """Test grouping of consecutive pages."""
    
    def test_all_consecutive(self):
        """Test all pages are consecutive."""
        result = group_consecutive_pages([0, 1, 2, 3, 4])
        assert result == [[0, 1, 2, 3, 4]]
    
    def test_no_consecutive(self):
        """Test no consecutive pages."""
        result = group_consecutive_pages([0, 2, 4, 6])
        assert result == [[0], [2], [4], [6]]
    
    def test_mixed_groups(self):
        """Test mixed consecutive and non-consecutive."""
        result = group_consecutive_pages([0, 1, 2, 5, 6, 9])
        assert result == [[0, 1, 2], [5, 6], [9]]
    
    def test_single_page(self):
        """Test single page."""
        result = group_consecutive_pages([3])
        assert result == [[3]]
    
    def test_empty_list(self):
        """Test empty list."""
        result = group_consecutive_pages([])
        assert result == []
    
    def test_two_consecutive(self):
        """Test two consecutive pages."""
        result = group_consecutive_pages([1, 2])
        assert result == [[1, 2]]
    
    def test_two_non_consecutive(self):
        """Test two non-consecutive pages."""
        result = group_consecutive_pages([1, 3])
        assert result == [[1], [3]]


class TestIntegration:
    """Integration tests for the full pipeline."""
    
    def test_parse_and_validate_integration(self):
        """Test parsing and validation together."""
        page_ranges = "1-3,5,7-9"
        parsed = parse_page_ranges(page_ranges)
        
        # Should work with a 10-page PDF
        validate_page_ranges(parsed, 10)
        
        # Should fail with a 5-page PDF
        with pytest.raises(ValueError):
            validate_page_ranges(parsed, 5)
    
    def test_realistic_scenarios(self):
        """Test realistic usage scenarios."""
        # Extracting first few pages
        result = parse_page_ranges("1-5")
        assert result == [0, 1, 2, 3, 4]
        
        # Extracting specific chapters
        result = parse_page_ranges("1,5-10,15-20,25")
        expected = [0] + list(range(4, 10)) + list(range(14, 20)) + [24]
        assert result == expected
        
        # Single page extraction
        result = parse_page_ranges("42")
        assert result == [41]