# AI-Powered Recruitment & ATS Platform

A college/portfolio-ready full-stack Applicant Tracking System (ATS) with AI-assisted resume parsing and job matching.

## Stack
- Frontend: React + Vite
- Backend: FastAPI + SQLAlchemy
- Database: SQLite by default (easy local setup), PostgreSQL-ready configuration
- Authentication: JWT
- Resume parsing: PDF/DOCX/TXT
- Matching: NLP-style skill extraction and weighted keyword matching

## Features
- Recruiter and candidate accounts
- JWT authentication
- Recruiter dashboard
- Create and manage jobs
- Candidate dashboard
- Browse and apply to jobs
- Resume upload and parsing
- Skill extraction
- Resume/job match score
- Candidate ranking
- Application status updates

## Demo accounts
- Recruiter: recruiter@demo.com / demo123
- Candidate: candidate@demo.com / demo123

## Run backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
# source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend: http://127.0.0.1:8000
Swagger: http://127.0.0.1:8000/docs

## Run frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## PostgreSQL
The project works out of the box with SQLite. To use PostgreSQL, set `DATABASE_URL` in `backend/.env`, for example:

`postgresql+psycopg://postgres:password@localhost:5432/ats_db`

The included PostgreSQL driver is already in `requirements.txt`.

## Project structure

```text
ai-recruitment-ats-platform/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── auth.py
│   │   ├── seed.py
│   │   └── services/
│   │       └── resume_parser.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── styles.css
│   ├── index.html
│   └── package.json
├── .gitignore
└── README.md
```
