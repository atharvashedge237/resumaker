# app/main.py
import os
import sys
from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import FileResponse

# Ensure Python knows where to find our app modules relative to the runtime execution path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.engine import tailor_resume, compile_pdf

# Initialize our Web Framework
app = FastAPI(
    title="ResuMaker API Gateway",
    description="Automated DevOps Pipeline for LaTeX Resume Tailoring via Gemini 2.5",
    version="1.0.0"
)

# Establish strict system path anchors
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MASTER_RESUME_PATH = os.path.join(DATA_DIR, "resume.tex")

@app.post("/api/v1/tailor")
async def api_tailor_resume(job_description: str = Form(...)):
    """
    HTTP POST Endpoint:
    Accepts a form-data string payload of a job description, mutates your master resume,
    compiles it through the local TeX Live tools, and streams the finished PDF back.
    """
    output_tex = os.path.join(DATA_DIR, "tailored_resume.tex")
    output_pdf = os.path.join(DATA_DIR, "tailored_resume.pdf")
    
    # Pre-flight Check: Verify master layout file is in place on disk
    if not os.path.exists(MASTER_RESUME_PATH):
        raise HTTPException(
            status_code=404,
            detail="Master profile document database file 'resume.tex' is missing from data directory."
        )
        
    try:
        # Phase 1: Call Gemini Generation Engine
        mutated_latex_string = tailor_resume(MASTER_RESUME_PATH, job_description)
        
        # Phase 2: Save the optimized variant locally
        with open(output_tex, "w", encoding="utf-8") as f:
            f.write(mutated_latex_string)
            
        # Phase 3: Trigger local shell compilation gate
        compilation_success = compile_pdf(output_tex, DATA_DIR)
        
        if not compilation_success or not os.path.exists(output_pdf):
            raise HTTPException(
                status_code=500,
                detail="LaTeX code optimization completed successfully, but downstream binary compilation failed."
            )
            
        # Phase 4: Stream final binary file straight back over HTTP response channel
        return FileResponse(
            path=output_pdf,
            media_type="application/pdf",
            filename="tailored_Resume.pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Core microservice execution failure: {str(e)}")

@app.get("/health")
async def service_health_check():
    """Service availability node ping."""
    return {"status": "healthy", "engine": "active"}