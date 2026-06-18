# app/engine.py
import os
import sys
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def compile_pdf(tex_path: str, output_dir: str) -> bool:
    """Attempts to compile the generated .tex file into a PDF locally."""
    try:
        print("Compiling tailored LaTeX file into PDF...")
        result = subprocess.run(
            ["pdflatex", f"-output-directory={output_dir}", "-interaction=batchmode", tex_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            print("PDF compiled successfully!")
            return True
        else:
            print("LaTeX Compilation Failed.")
            return False
    except FileNotFoundError:
        print("Warning: 'pdflatex' command not found. Please check your system MacTeX installation.")
        return False

def extract_latex_errors(log_path: str) -> str:
    """Parses a LaTeX log file to extract relevant error context lines."""
    if not os.path.exists(log_path):
        return "No log file found."
        
    error_lines = []
    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if line.startswith('! '):
            context = lines[i:i+4]
            error_lines.append("".join(context))
            
    return "\n".join(error_lines) if error_lines else "Unknown compilation anomaly detected."

def tailor_resume_pipeline(resume_path: str, job_description: str, data_dir: str) -> bool:
    """Executes the self-correcting agentic loop across max 3 retries."""
    output_tex_path = os.path.join(data_dir, "tailored_resume.tex")
    log_path = os.path.join(data_dir, "tailored_resume.log")
    
    with open(resume_path, 'r', encoding='utf-8') as f:
        raw_tex_resume = f.read()
        
    client = genai.Client()
    
    system_instruction = """
    You are an expert technical resume writer and LaTeX engineer.
    Your task is to tailor a candidate's LaTeX resume to align perfectly with a provided target Job Description (JD).
    
    CRITICAL RULES:
    1. DO NOT alter structural LaTeX layout commands or custom macros.
    2. Modify only descriptive text inside brackets to emphasize key skills requested in the JD.
    3. Ensure special characters like % or & are correctly escaped (e.g., use \\% or \\&).
    4. Output ONLY raw text. Do not enclose code in Markdown blocks like ```latex.
    5. STYLISTIC RULE: Avoid using bold lettering (the \\textbf command) for the tailored keywords unless absolutely necessary. Keep the text flowing naturally without adding extra formatting weights.
    """
    
    user_prompt = f"Target Job Description:\n{job_description}\n\nOriginal LaTeX Resume:\n{raw_tex_resume}"
    
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        print(f"Compilation Pipeline Attempt {attempt}/{max_retries}...")
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
            ),
        )
        
        with open(output_tex_path, "w", encoding="utf-8") as f:
            f.write(response.text)
            
        if compile_pdf(output_tex_path, data_dir):
            print(f"Success! PDF generated cleanly on attempt {attempt}.")
            return True
            
        print(f"Attempt {attempt} failed compilation syntax gates. Extracting logs...")
        error_context = extract_latex_errors(log_path)
        
        user_prompt = f"""
        Your previous LaTeX output failed compilation with the following error context:
        ---
        {error_context}
        ---
        
        Please completely resolve this syntax fault. Ensure all special characters (especially %, &, _, $, #) are perfectly escaped using standard backslashes. Output the complete corrected LaTeX code document.
        """
        
    return False

if __name__ == "__main__":
    sample_jd = """
    We are looking for a Senior DevOps / Cloud Engineer with extensive experience in 
    GitLab CI/CD workflows, Terraform infrastructure as code, and running production 
    workloads inside Azure AKS. Experience tracking application performance metrics 
    via Prometheus and Grafana dashboards is highly valued.
    """
    
    test_resume_path = "data/resume.tex"
    data_directory = "data"
    
    try:
        # Fixed to call the accurate pipeline method name
        success = tailor_resume_pipeline(test_resume_path, sample_jd, data_directory)
        print(f"Local pipeline run finished. Status: {'Success' if success else 'Failed'}")
    except Exception as e:
        print(f"Execution Error: {e}")