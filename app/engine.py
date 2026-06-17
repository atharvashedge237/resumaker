# app/engine.py
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def tailor_resume(resume_path: str, job_description: str) -> str:
    """
    Reads a local .tex resume file and updates its contents 
    using Gemini to align perfectly with a target Job Description.
    """
    # 1. Read the raw LaTeX file
    if not os.path.exists(resume_path):
        raise FileNotFoundError(f"Could not find resume at {resume_path}")
        
    with open(resume_path, 'r', encoding='utf-8') as f:
        raw_tex_resume = f.read()
        
    # 2. Initialize the Gemini API client
    client = genai.Client()
    
    # 3. Formulate a highly protective system instruction prompt
    system_instruction = """
    You are an expert technical resume writer and LaTeX engineer specializing in DevOps and MLOps engineering roles.
    Your task is to tailor a candidate's LaTeX resume to align perfectly with a provided target Job Description (JD).
    
    CRITICAL RULES:
    1. DO NOT alter the structural LaTeX layout commands, custom packages, or document configurations.
    2. Maintain exact custom syntax definitions:
       - Keep `\\resumeSubheading{Company}{Dates}{Role}{Location}` intact.
       - Keep `\\resumeProjectHeading{\\textbf{Title} $|$ \\textit{Tech}}{Year}` intact.
       - Keep `\\resumeItem{Text}` intact.
    3. Modify only the descriptive text inside the brackets to highlight key skills, metrics, or frameworks requested in the JD.
    4. Focus updates heavily on the 'Summary', 'Experience' bullet points, and the order of items listed under 'Skills'.
    5. Maintain realistic professional limits—do not fabricate achievements or invent entirely brand new experiences that lack structural backing in the original copy.
    6. Ensure all special text characters like % or & are correctly escaped (e.g., use \\% or \\&), or the document compilation will fail.
    7. Output ONLY the raw modified LaTeX content. Do not enclose the code in Markdown blocks like ```latex or ```.
    """
    
    user_prompt = f"""
    Target Job Description:
    {job_description}
    
    -------------------------------------------
    Original LaTeX Resume Content:
    {raw_tex_resume}
    """
    
    print("Analyzing Job Description and mutating LaTeX bullet points...")
    
    # Execute text transformation with Gemini
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2, # Low temperature forces structural consistency
        ),
    )
    
    return response.text

if __name__ == "__main__":
    # Quick execution test
    sample_jd = """
    We are looking for a Senior DevOps / Cloud Engineer with extensive experience in 
    GitLab CI/CD workflows, Terraform infrastructure as code, and running production 
    workloads inside Azure AKS. Experience tracking application performance metrics 
    via Prometheus and Grafana dashboards is highly valued. Familiarity with 
    managing secure enterprise data infrastructure in regulated banking environments is a major plus.
    """
    
    # Ensure you save your resume text into `data/resume.tex` first!
    test_resume_path = "data/resume.tex"
    
    try:
        updated_tex = tailor_resume(test_resume_path, sample_jd)
        output_path = "data/tailored_resume.tex"
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(updated_tex)
            
        print(f"Success! Tailored resume saved directly to {output_path}")
    except Exception as e:
        print(f"Execution Error: {e}")