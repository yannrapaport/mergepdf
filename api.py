from fastapi import FastAPI, File, UploadFile, HTTPException, Form, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
import tempfile
import os
import uuid
import shutil
from typing import Optional
from pydantic import BaseModel
import uvicorn
from mergepdf import merge_pdfs

app = FastAPI(
    title="MergePDF API",
    description="API for merging odd and even PDF files",
    version="1.0.0"
)

# Storage for temporary files
TEMP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

class MergeResponse(BaseModel):
    job_id: str
    message: str

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None

def cleanup_temp_files(file_paths):
    """Remove temporary files after a delay"""
    for path in file_paths:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Error removing temp file {path}: {e}")

@app.post("/api/merge", response_model=MergeResponse)
async def merge_pdf_files(
    background_tasks: BackgroundTasks,
    odd_file: UploadFile = File(..., description="PDF file with odd pages"),
    even_file: UploadFile = File(..., description="PDF file with even pages (reversed)"),
    output_filename: str = Form("merged.pdf", description="Name for the output PDF file")
):
    """
    Merge two PDF files containing odd and even pages.
    
    - The first file should contain odd pages in normal order.
    - The second file should contain even pages in reverse order.
    """
    # Validate file types
    if not odd_file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Odd pages file must be a PDF")
    if not even_file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Even pages file must be a PDF")
    
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    
    # Create temporary directory for this job
    job_dir = os.path.join(TEMP_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    # Define file paths
    odd_path = os.path.join(job_dir, "odd.pdf")
    even_path = os.path.join(job_dir, "even.pdf")
    output_path = os.path.join(job_dir, output_filename)
    
    try:
        # Save uploaded files
        with open(odd_path, "wb") as f:
            shutil.copyfileobj(odd_file.file, f)
        with open(even_path, "wb") as f:
            shutil.copyfileobj(even_file.file, f)
        
        # Merge PDFs
        merge_pdfs(odd_path, even_path, output_path)
        
        # Schedule cleanup after 5 minutes (files will be available for download)
        background_tasks.add_task(cleanup_temp_files, [odd_path, even_path])
        
        return MergeResponse(
            job_id=job_id,
            message="PDFs merged successfully"
        )
    
    except Exception as e:
        # Clean up on error
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=f"Error merging PDFs: {str(e)}")

@app.get("/api/download/{job_id}")
async def download_merged_pdf(
    job_id: str, 
    filename: Optional[str] = None,
    background_tasks: BackgroundTasks = None
):
    """
    Download a previously merged PDF file.
    
    - job_id: The unique identifier returned from the merge operation
    - filename: Optional custom filename for the downloaded file
    """
    # Validate job_id format to prevent directory traversal
    try:
        uuid_obj = uuid.UUID(job_id)
        if str(uuid_obj) != job_id:
            raise ValueError("Invalid UUID format")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    # Get job directory
    job_dir = os.path.join(TEMP_DIR, job_id)
    
    if not os.path.exists(job_dir):
        raise HTTPException(status_code=404, detail="Merged file not found or expired")
    
    # Find the output file
    output_files = [f for f in os.listdir(job_dir) if not f.startswith(("odd", "even"))]
    
    if not output_files:
        raise HTTPException(status_code=404, detail="Merged file not found in job directory")
    
    output_path = os.path.join(job_dir, output_files[0])
    download_filename = filename or output_files[0]
    
    # Schedule cleanup after download
    if background_tasks:
        background_tasks.add_task(cleanup_temp_files, [output_path])
        background_tasks.add_task(lambda: shutil.rmtree(job_dir, ignore_errors=True))
    
    return FileResponse(
        path=output_path,
        filename=download_filename,
        media_type="application/pdf",
        background=background_tasks
    )

@app.get("/api/health")
async def health_check():
    """API health check endpoint"""
    return {"status": "ok"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "Request failed", "detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# CLI entry point
if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)

