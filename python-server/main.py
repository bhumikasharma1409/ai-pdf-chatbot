from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path
import shutil
from pypdf import PdfReader
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Setup CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup uploads directory
UPLOADS_DIR = Path(__file__).parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

# Helper function to extract text from PDF
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from PDF file"""
    try:
        with open(file_path, 'rb') as pdf_file:
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        logger.error(f"Error extracting PDF text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"PDF parsing failed: {str(e)}")

@app.get("/api/test")
async def test_connection():
    """Test endpoint to verify server is running"""
    return {"message": "Python server running"}

@app.post("/api/upload")
async def upload_pdf(pdf: UploadFile = File(...)):
    """Handle PDF file upload and text extraction"""
    try:
        # Validate PDF file
        if pdf.content_type not in ["application/pdf"]:
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        if not pdf.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Save file with unique name
        import time
        import random
        unique_suffix = f"{int(time.time())}-{random.randint(0, 999999999)}"
        file_extension = ".pdf"
        unique_filename = f"{pdf.filename.replace('.pdf', '')}-{unique_suffix}{file_extension}"
        file_path = UPLOADS_DIR / unique_filename
        
        # Write file
        with open(file_path, "wb") as buffer:
            content = await pdf.read()
            buffer.write(content)
        
        logger.info(f"File uploaded successfully: {unique_filename}")
        
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(str(file_path))
        preview = extracted_text.strip()[:300]
        
        logger.info(f"Extracted text preview: {preview}")
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "PDF uploaded and parsed successfully",
                "filename": unique_filename,
                "size": len(content),
                "preview": preview,
                "textLength": len(extracted_text)
            }
        )
    
    except HTTPException as e:
        logger.error(f"Upload error: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during upload")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"status": "Python server is running", "port": 8000}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
