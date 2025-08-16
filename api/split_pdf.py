import os
import re
import tempfile
import zipfile
from typing import List, Tuple, Set
from pypdf import PdfReader, PdfWriter
from pathlib import Path


def parse_page_ranges(ranges_str: str) -> List[int]:
    """
    Parse page ranges string like '1-3,5,7-9' into list of page numbers.
    Returns 0-indexed page numbers for internal use.
    """
    if not ranges_str.strip():
        raise ValueError("Page ranges cannot be empty")
    
    pages = set()
    ranges = ranges_str.split(',')
    
    for range_part in ranges:
        range_part = range_part.strip()
        if not range_part:
            continue
            
        if '-' in range_part:
            # Range like "1-5"
            try:
                start, end = range_part.split('-', 1)
                start_num = int(start.strip())
                end_num = int(end.strip())
                
                if start_num < 1 or end_num < 1:
                    raise ValueError("Page numbers must be positive")
                if start_num > end_num:
                    raise ValueError(f"Invalid range: {range_part}")
                
                for page in range(start_num, end_num + 1):
                    pages.add(page - 1)  # Convert to 0-indexed
                    
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"Invalid page number in range: {range_part}")
                raise
        else:
            # Single page like "5"
            try:
                page_num = int(range_part)
                if page_num < 1:
                    raise ValueError("Page numbers must be positive")
                pages.add(page_num - 1)  # Convert to 0-indexed
            except ValueError:
                raise ValueError(f"Invalid page number: {range_part}")
    
    if not pages:
        raise ValueError("No valid pages specified")
    
    return sorted(list(pages))


def validate_page_ranges(page_numbers: List[int], total_pages: int) -> None:
    """Validate that all page numbers are within bounds."""
    for page_num in page_numbers:
        if page_num >= total_pages:
            raise ValueError(f"Page {page_num + 1} is out of bounds (PDF has {total_pages} pages)")


def split_pdf_to_zip(pdf_file_path: str, page_ranges: str, original_filename: str) -> str:
    """
    Split PDF according to page ranges and return path to ZIP file.
    """
    try:
        # Parse ranges
        page_numbers = parse_page_ranges(page_ranges)
        
        # Read PDF
        reader = PdfReader(pdf_file_path)
        total_pages = len(reader.pages)
        
        # Validate ranges
        validate_page_ranges(page_numbers, total_pages)
        
        # Create temporary directory for output files
        temp_dir = tempfile.mkdtemp()
        output_files = []
        
        # Get base filename without extension
        base_name = Path(original_filename).stem
        
        # Group consecutive pages for efficient splitting
        page_groups = group_consecutive_pages(page_numbers)
        
        for i, group in enumerate(page_groups, 1):
            writer = PdfWriter()
            
            # Add pages to writer
            for page_num in group:
                writer.add_page(reader.pages[page_num])
            
            # Generate output filename
            if len(group) == 1:
                output_filename = f"{base_name}_page{group[0] + 1}.pdf"
            else:
                output_filename = f"{base_name}_pages{group[0] + 1}-{group[-1] + 1}.pdf"
            
            output_path = os.path.join(temp_dir, output_filename)
            
            # Write PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            output_files.append(output_path)
        
        # Create ZIP file
        zip_filename = f"{base_name}_split.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in output_files:
                # Use only basename to avoid directory structure in ZIP
                arcname = os.path.basename(file_path)
                zipf.write(file_path, arcname)
        
        return zip_path
        
    except Exception as e:
        raise ValueError(f"Error processing PDF: {str(e)}")


def group_consecutive_pages(page_numbers: List[int]) -> List[List[int]]:
    """Group consecutive page numbers together."""
    if not page_numbers:
        return []
    
    groups = []
    current_group = [page_numbers[0]]
    
    for i in range(1, len(page_numbers)):
        if page_numbers[i] == page_numbers[i-1] + 1:
            current_group.append(page_numbers[i])
        else:
            groups.append(current_group)
            current_group = [page_numbers[i]]
    
    groups.append(current_group)
    return groups