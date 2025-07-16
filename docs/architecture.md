# Architecture Overview

## System Architecture

```mermaid
graph TB
    subgraph "Frontend (React + TypeScript)"
        A[User Interface]
        B[Drag & Drop Zone]
        C[Range Input Component]
        D[File Validation]
    end
    
    subgraph "Backend (FastAPI + Python)"
        E[API Endpoints]
        F[File Upload Handler]
        G[PDF Processing Engine]
        H[Range Parser]
        I[ZIP Generator]
    end
    
    subgraph "Processing Pipeline"
        J[Temporary File Storage]
        K[pypdf Library]
        L[Page Extraction]
        M[ZIP Packaging]
    end
    
    A --> B
    B --> D
    C --> H
    D --> F
    F --> G
    G --> K
    K --> L
    L --> M
    M --> I
    
    E <--> F
    G --> J
    J --> K
```

## Component Breakdown

### Frontend Components
- **DropZone.tsx**: Drag-and-drop file upload interface
- **RangeInput.tsx**: Page range input with live validation
- **App.tsx**: Main application orchestrator
- **parseRange.ts**: Client-side range validation utilities

### Backend Components
- **main.py**: FastAPI application with middleware
- **split_pdf.py**: Core PDF processing logic
- **schemas.py**: Pydantic data models

## Data Flow

1. **File Upload**: User drags PDF into DropZone component
2. **Validation**: Client validates file type/size, server re-validates
3. **Range Input**: User specifies pages using flexible syntax
4. **Processing**: Backend streams PDF, extracts pages using pypdf
5. **Packaging**: Extracted pages bundled into ZIP file
6. **Download**: Client automatically downloads ZIP file

## Security Considerations

- File type validation (MIME type checking)
- Size limitations (130MB max)
- Path sanitization in ZIP files
- Temporary file cleanup
- Input validation and sanitization

## Performance Optimizations

- Streaming file upload/download
- Memory-efficient PDF processing
- Temporary file cleanup
- Client-side validation to reduce server load
- Docker container optimization