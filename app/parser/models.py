from pydantic import BaseModel, Field
from typing import List

class WorkExperience(BaseModel):
    company: str = Field(description="Name of the company or organization")
    role: str = Field(description="Your job title")
    duration: str = Field(description="Dates employed, e.g., 'Mar 2024 - Present'")
    bullet_points: List[str] = Field(description="The list of bullet points detailing achievements")

class ResumeSchema(BaseModel):
    name: str
    contact_info: List[str]
    skills: List[str] = Field(description="List of technical skills, languages, or tools")
    experience: List[WorkExperience] = Field(description="List of your professional work history blocks")