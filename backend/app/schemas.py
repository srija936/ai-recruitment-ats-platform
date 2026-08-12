from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "candidate"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    role: str
    skills: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class JobCreate(BaseModel):
    title: str
    company: str
    location: str
    description: str
    required_skills: str

class JobOut(JobCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    recruiter_id: int

class ApplicationOut(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    status: str
    match_score: float
    matched_skills: str
    missing_skills: str
    job_title: Optional[str] = None
    candidate_name: Optional[str] = None

class StatusUpdate(BaseModel):
    status: str
