from .database import SessionLocal, Base, engine
from .models import User, Job
from .auth import hash_password

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if not db.query(User).filter_by(email="recruiter@demo.com").first():
        db.add(User(name="Demo Recruiter", email="recruiter@demo.com",
                    password_hash=hash_password("demo123"), role="recruiter"))
    if not db.query(User).filter_by(email="candidate@demo.com").first():
        db.add(User(name="Demo Candidate", email="candidate@demo.com",
                    password_hash=hash_password("demo123"), role="candidate",
                    skills="python, react, fastapi, postgresql, git"))
    db.commit()
    recruiter = db.query(User).filter_by(email="recruiter@demo.com").first()
    if recruiter and not db.query(Job).first():
        db.add(Job(
            title="Full Stack Python Developer",
            company="TechNova",
            location="Hyderabad / Remote",
            description="Build web applications and REST APIs with a modern frontend.",
            required_skills="Python, FastAPI, React, PostgreSQL, Git, REST API",
            recruiter_id=recruiter.id
        ))
        db.commit()
    db.close()

if __name__ == "__main__":
    seed()
