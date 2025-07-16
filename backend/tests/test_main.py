import pytest
import tempfile
import os
from io import BytesIO
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from main import app

client = TestClient(app)


def create_test_pdf(num_pages: int = 5) -> BytesIO:
    """Create a test PDF with specified number of pages."""
    writer = PdfWriter()
    
    # Add empty pages
    for i in range(num_pages):
        writer.add_blank_page(width=612, height=792)  # Standard letter size
    
    pdf_buffer = BytesIO()
    writer.write(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer


class TestAPIEndpoints:
    """Test API endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "PDF Splitter API"
        assert "version" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "pdf-splitter"


class TestSplitEndpoint:
    """Test PDF splitting endpoint."""
    
    def test_successful_split(self):
        """Test successful PDF splitting."""
        # Create test PDF
        pdf_content = create_test_pdf(5)
        
        # Prepare form data
        files = {"file": ("test.pdf", pdf_content, "application/pdf")}
        data = {"page_ranges": "1-3,5"}
        
        response = client.post("/split", files=files, data=data)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
        assert "Content-Disposition" in response.headers
        assert "test_split.zip" in response.headers["Content-Disposition"]
    
    def test_invalid_page_ranges(self):
        """Test invalid page ranges."""
        pdf_content = create_test_pdf(5)
        
        files = {"file": ("test.pdf", pdf_content, "application/pdf")}
        data = {"page_ranges": "1-10"}  # Out of bounds
        
        response = client.post("/split", files=files, data=data)
        assert response.status_code == 400
        assert "out of bounds" in response.json()["detail"]
    
    def test_invalid_range_format(self):
        """Test invalid range format."""
        pdf_content = create_test_pdf(5)
        
        files = {"file": ("test.pdf", pdf_content, "application/pdf")}
        data = {"page_ranges": "abc"}
        
        response = client.post("/split", files=files, data=data)
        assert response.status_code == 400
        assert "Invalid page ranges" in response.json()["detail"]
    
    def test_no_file_provided(self):
        """Test no file provided."""
        data = {"page_ranges": "1-3"}
        
        response = client.post("/split", data=data)
        assert response.status_code == 422  # Validation error
    
    def test_non_pdf_file(self):
        """Test non-PDF file upload."""
        # Create fake text file
        text_content = BytesIO(b"This is not a PDF")
        
        files = {"file": ("test.txt", text_content, "text/plain")}
        data = {"page_ranges": "1"}
        
        response = client.post("/split", files=files, data=data)
        assert response.status_code == 400
        assert "Only PDF files are allowed" in response.json()["detail"]
    
    def test_empty_filename(self):
        """Test empty filename."""
        pdf_content = create_test_pdf(5)
        
        files = {"file": ("", pdf_content, "application/pdf")}
        data = {"page_ranges": "1"}
        
        response = client.post("/split", files=files, data=data)
        assert response.status_code == 400
        assert "No file provided" in response.json()["detail"]
    
    def test_filename_too_long(self):
        """Test filename that's too long."""
        pdf_content = create_test_pdf(5)
        long_filename = "a" * 300 + ".pdf"
        
        files = {"file": (long_filename, pdf_content, "application/pdf")}
        data = {"page_ranges": "1"}
        
        response = client.post("/split", files=files, data=data)
        assert response.status_code == 400
        assert "Filename too long" in response.json()["detail"]
    
    def test_wrong_file_extension(self):
        """Test file with wrong extension but PDF content type."""
        pdf_content = create_test_pdf(5)
        
        files = {"file": ("test.txt", pdf_content, "application/pdf")}
        data = {"page_ranges": "1"}
        
        response = client.post("/split", files=files, data=data)
        assert response.status_code == 400
        assert "Only PDF files are allowed" in response.json()["detail"]
    
    def test_empty_page_ranges(self):
        """Test empty page ranges."""
        pdf_content = create_test_pdf(5)
        
        files = {"file": ("test.pdf", pdf_content, "application/pdf")}
        data = {"page_ranges": ""}
        
        response = client.post("/split", files=files, data=data)
        assert response.status_code == 400
        assert "Invalid page ranges" in response.json()["detail"]
    
    def test_single_page_extraction(self):
        """Test extracting a single page."""
        pdf_content = create_test_pdf(5)
        
        files = {"file": ("test.pdf", pdf_content, "application/pdf")}
        data = {"page_ranges": "3"}
        
        response = client.post("/split", files=files, data=data)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
    
    def test_all_pages_extraction(self):
        """Test extracting all pages."""
        pdf_content = create_test_pdf(5)
        
        files = {"file": ("test.pdf", pdf_content, "application/pdf")}
        data = {"page_ranges": "1-5"}
        
        response = client.post("/split", files=files, data=data)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"