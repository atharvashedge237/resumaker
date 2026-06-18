# app/main.py
import os
import sys
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import FileResponse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fixed to import the accurate pipeline name from the engine
from app.engine import tailor_resume_pipeline, compile_pdf

app = FastAPI(
    title="ResuMaker API Gateway",
    description="Automated DevOps Pipeline for LaTeX Resume Tailoring via Gemini 2.5",
    version="1.0.0"
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MASTER_RESUME_PATH = os.path.join(DATA_DIR, "resume.tex")

@app.post("/api/v1/tailor")
async def api_tailor_resume(job_description: str = Form(...)):
    output_pdf = os.path.join(DATA_DIR, "tailored_resume.pdf")
    
    if not os.path.exists(MASTER_RESUME_PATH):
        raise HTTPException(status_code=404, detail="Master profile missing.")
        
    success = tailor_resume_pipeline(MASTER_RESUME_PATH, job_description, DATA_DIR)
    
    if not success or not os.path.exists(output_pdf):
        raise HTTPException(
            status_code=500, 
            detail="The agentic pipeline failed to compile a syntactically valid PDF after maximum self-correction retries."
        )
        
    return FileResponse(path=output_pdf, media_type="application/pdf", filename="Tailored_Resume.pdf")

@app.get("/health")
async def service_health_check():
    return {"status": "healthy", "engine": "active"}