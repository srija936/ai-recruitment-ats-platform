import re
from pathlib import Path

SKILL_VOCAB = [
    "python","java","javascript","typescript","react","node.js","fastapi","django",
    "flask","sql","postgresql","mysql","mongodb","html","css","tailwind","git",
    "github","docker","aws","azure","machine learning","deep learning","nlp",
    "pandas","numpy","scikit-learn","tensorflow","pytorch","rest api","api",
    "data structures","algorithms","tableau","power bi","excel"
]

def extract_text(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        from pypdf import PdfReader
        return "\n".join((page.extract_text() or "") for page in PdfReader(path).pages)
    if suffix == ".docx":
        from docx import Document
        return "\n".join(p.text for p in Document(path).paragraphs)
    return Path(path).read_text(errors="ignore")

def extract_skills(text: str):
    lower = text.lower()
    found = []
    for skill in SKILL_VOCAB:
        pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
        if re.search(pattern, lower):
            found.append(skill)
    return sorted(set(found))

def parse_resume(path: str):
    text = extract_text(path)
    skills = extract_skills(text)
    return text, skills

def match_resume(resume_skills, required_skills_text, description=""):
    required = extract_skills(required_skills_text + " " + description)
    rset = set(x.lower() for x in resume_skills)
    qset = set(x.lower() for x in required)
    if not qset:
        return 0.0, [], []
    matched = sorted(rset & qset)
    missing = sorted(qset - rset)
    score = round((len(matched) / len(qset)) * 100, 2)
    return score, matched, missing
