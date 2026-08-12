import os, json, shutil, uuid
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import Base, engine, get_db
from .models import User, Job, Application
from .schemas import *
from .auth import hash_password, verify_password, create_token, get_current_user, require_role
from .services.resume_parser import parse_resume, match_resume

Base.metadata.create_all(bind=engine)
Path("uploads").mkdir(exist_ok=True)

app = FastAPI(title="AI Recruitment ATS API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173","http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"message": "AI Recruitment ATS API is running"}

@app.post("/api/auth/register", response_model=UserOut)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if data.role not in ("candidate", "recruiter"):
        raise HTTPException(400, "Invalid role")
    if db.query(User).filter_by(email=data.email).first():
        raise HTTPException(400, "Email already registered")
    user = User(name=data.name, email=data.email, password_hash=hash_password(data.password), role=data.role)
    db.add(user); db.commit(); db.refresh(user)
    return user

@app.post("/api/auth/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return {"access_token": create_token(user.id), "token_type": "bearer"}

@app.get("/api/auth/me", response_model=UserOut)
def me(user=Depends(get_current_user)):
    return user

@app.get("/api/jobs", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(Job).order_by(Job.created_at.desc()).all()

@app.post("/api/jobs", response_model=JobOut)
def create_job(data: JobCreate, recruiter=Depends(require_role("recruiter")), db: Session = Depends(get_db)):
    job = Job(**data.model_dump(), recruiter_id=recruiter.id)
    db.add(job); db.commit(); db.refresh(job)
    return job

@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: int, recruiter=Depends(require_role("recruiter")), db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job or job.recruiter_id != recruiter.id:
        raise HTTPException(404, "Job not found")
    db.query(Application).filter_by(job_id=job_id).delete()
    db.delete(job); db.commit()
    return {"message": "Job deleted"}

@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...), candidate=Depends(require_role("candidate")), db: Session = Depends(get_db)):
    ext = Path(file.filename).suffix.lower()
    if ext not in (".pdf", ".docx", ".txt"):
        raise HTTPException(400, "Upload PDF, DOCX, or TXT")
    safe_name = f"{candidate.id}_{uuid.uuid4().hex}{ext}"
    path = Path("uploads") / safe_name
    with path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        text, skills = parse_resume(str(path))
    except Exception as e:
        path.unlink(missing_ok=True)
        raise HTTPException(400, f"Could not parse resume: {e}")
    candidate.resume_path = str(path)
    candidate.resume_text = text
    candidate.skills = json.dumps(skills)
    db.commit()
    return {"message": "Resume uploaded", "skills": skills, "text_preview": text[:500]}

@app.post("/api/applications/{job_id}", response_model=ApplicationOut)
def apply(job_id: int, candidate=Depends(require_role("candidate")), db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job: raise HTTPException(404, "Job not found")
    if db.query(Application).filter_by(job_id=job_id, candidate_id=candidate.id).first():
        raise HTTPException(400, "Already applied")
    if not candidate.resume_text:
        raise HTTPException(400, "Upload your resume before applying")
    resume_skills = json.loads(candidate.skills or "[]")
    score, matched, missing = match_resume(resume_skills, job.required_skills, job.description)
    appx = Application(job_id=job_id, candidate_id=candidate.id, match_score=score,
                        matched_skills=json.dumps(matched), missing_skills=json.dumps(missing))
    db.add(appx); db.commit(); db.refresh(appx)
    return application_out(appx)

@app.get("/api/applications/mine", response_model=list[ApplicationOut])
def my_applications(candidate=Depends(require_role("candidate")), db: Session = Depends(get_db)):
    return [application_out(a) for a in db.query(Application).filter_by(candidate_id=candidate.id).order_by(Application.created_at.desc()).all()]

@app.get("/api/recruiter/applications", response_model=list[ApplicationOut])
def recruiter_applications(recruiter=Depends(require_role("recruiter")), db: Session = Depends(get_db)):
    jobs = db.query(Job).filter_by(recruiter_id=recruiter.id).all()
    ids = {j.id for j in jobs}
    apps = [a for a in db.query(Application).order_by(Application.match_score.desc()).all() if a.job_id in ids]
    return [application_out(a) for a in apps]

@app.patch("/api/applications/{application_id}", response_model=ApplicationOut)
def update_status(application_id: int, data: StatusUpdate, recruiter=Depends(require_role("recruiter")), db: Session = Depends(get_db)):
    appx = db.get(Application, application_id)
    if not appx or appx.job.recruiter_id != recruiter.id:
        raise HTTPException(404, "Application not found")
    if data.status not in ("Applied","Shortlisted","Interview","Rejected","Hired"):
        raise HTTPException(400, "Invalid status")
    appx.status = data.status
    db.commit(); db.refresh(appx)
    return application_out(appx)

def application_out(a):
    return {
        "id": a.id, "job_id": a.job_id, "candidate_id": a.candidate_id,
        "status": a.status, "match_score": a.match_score or 0,
        "matched_skills": a.matched_skills or "[]",
        "missing_skills": a.missing_skills or "[]",
        "job_title": a.job.title if a.job else None,
        "candidate_name": a.candidate.name if a.candidate else None
    }

@app.on_event("startup")
def startup_seed():
    from .seed import seed
    seed()
