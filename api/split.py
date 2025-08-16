import os
import tempfile
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from split_pdf import split_pdf_to_zip, parse_page_ranges

# Configuration
MAX_FILE_SIZE = 130 * 1024 * 1024  # 130MB
ALLOWED_CONTENT_TYPES = ["application/pdf"]

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

@app.post("/api/split")
async def split_pdf(
    file: UploadFile = File(...),
    page_ranges: str = Form(...)
):
    # Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only PDF files are allowed."
        )
    
    # Validate file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Reset file position
    await file.seek(0)
    
    # Validate page ranges
    try:
        parsed_ranges = parse_page_ranges(page_ranges)
        if not parsed_ranges:
            raise ValueError("No valid page ranges provided")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Save uploaded file
        input_path = temp_path / file.filename
        with open(input_path, "wb") as f:
            f.write(file_content)
        
        # Split PDF
        try:
            output_filename = file.filename.replace('.pdf', '_split.zip')
            output_path = temp_path / output_filename
            
            split_pdf_to_zip(str(input_path), parsed_ranges, str(output_path))
            
            # Return zip file
            return FileResponse(
                path=str(output_path),
                media_type="application/zip",
                filename=output_filename,
                headers={
                    "Content-Disposition": f"attachment; filename={output_filename}"
                }
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

# Handler for Vercel
handler = app