import os
import tempfile
import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from split_pdf import split_pdf_to_zip, parse_page_ranges
from schemas import SplitResponse, ErrorResponse


# Configuration
MAX_FILE_SIZE = 130 * 1024 * 1024  # 130MB
ALLOWED_CONTENT_TYPES = ["application/pdf"]

app = FastAPI(
    title="PDF Splitter API",
    description="Split PDF files by page ranges and download as ZIP",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:5173",  # Vite dev server
        "https://pdf-splitter-6vd6nl7dv-abecos-projects.vercel.app",  # Vercel deployment
        "https://pdf-splitter-dno84nfzy-abecos-projects.vercel.app",  # Vercel deployment
        "https://pdf-splitter-6b6mvn87v-abecos-projects.vercel.app",  # Latest Vercel deployment
        "https://*.vercel.app",  # All Vercel deployments
        "https://pdf-splitter.vercel.app",  # Custom domain if set
        "https://abecoko.github.io"  # GitHub Pages
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


# File size middleware
@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    if request.method == "POST" and "multipart/form-data" in request.headers.get("content-type", ""):
        content_length = request.headers.get("content-length")
        if content_length:
            content_length = int(content_length)
            if content_length > MAX_FILE_SIZE:
                return JSONResponse(
                    status_code=413,
                    content={"success": False, "message": f"File size exceeds {MAX_FILE_SIZE // (1024*1024)}MB limit"}
                )
    
    response = await call_next(request)
    return response


@app.get("/")
async def root():
    return {"message": "PDF Splitter API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "pdf-splitter"}


@app.options("/split")
async def split_options():
    """Handle preflight OPTIONS request for CORS"""
    return {"message": "OK"}


@app.post("/split", response_model=SplitResponse)
async def split_pdf(
    file: UploadFile = File(...),
    page_ranges: str = Form(...)
):
    """
    Split PDF file by page ranges and return as ZIP download.
    
    Args:
        file: PDF file to split (max 130MB)
        page_ranges: Comma-separated page ranges (e.g., "1-3,5,7-9")
    
    Returns:
        ZIP file containing split PDF pages
    """
    
    print(f"[INFO] Received split request - File: {file.filename}, Size: {file.size}, Content-Type: {file.content_type}")
    print(f"[INFO] Page ranges: {page_ranges}")
    
    # Validate file
    if not file.filename:
        print("[ERROR] No filename provided")
        raise HTTPException(status_code=400, detail="No file provided")
    
    if not file.filename.lower().endswith('.pdf'):
        print(f"[ERROR] Invalid file extension: {file.filename}")
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        print(f"[ERROR] Invalid content type: {file.content_type}")
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF files are allowed")
    
    # Validate filename length
    if len(file.filename) > 255:
        print(f"[ERROR] Filename too long: {len(file.filename)} characters")
        raise HTTPException(status_code=400, detail="Filename too long")
    
    # Validate page ranges format
    try:
        page_numbers = parse_page_ranges(page_ranges)
        print(f"[INFO] Parsed page numbers: {page_numbers}")
    except ValueError as e:
        print(f"[ERROR] Invalid page ranges: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid page ranges: {str(e)}")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            print(f"[INFO] Created temp directory: {temp_dir}")
            
            # Save uploaded file
            temp_pdf_path = os.path.join(temp_dir, "input.pdf")
            
            with open(temp_pdf_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            print(f"[INFO] Saved uploaded file to: {temp_pdf_path}")
            
            # Split PDF and create ZIP
            zip_path = split_pdf_to_zip(temp_pdf_path, page_ranges, file.filename)
            
            # Get ZIP filename for response
            zip_filename = os.path.basename(zip_path)
            
            print(f"[INFO] Created ZIP file: {zip_filename}")
            
            # Return file response
            return FileResponse(
                path=zip_path,
                filename=zip_filename,
                media_type="application/zip",
                headers={
                    "Content-Disposition": f"attachment; filename={zip_filename}",
                    "Access-Control-Expose-Headers": "Content-Disposition"
                }
            )
            
        except ValueError as e:
            print(f"[ERROR] ValueError: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            print(f"[ERROR] Exception: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.exception_handler(413)
async def file_too_large_handler(request: Request, exc):
    return JSONResponse(
        status_code=413,
        content={"success": False, "message": "File too large. Maximum size is 130MB."}
    )


@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": "Validation error", "details": str(exc)}
    )


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        timeout_keep_alive=180
    )