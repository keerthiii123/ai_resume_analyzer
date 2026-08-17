
import os
import re
import io
import fitz

from PIL import Image
from dotenv import load_dotenv
from google import genai

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor

from docx import Document
from docx.shared import Pt


# =====================================================
# GEMINI CONFIG
# =====================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key) if api_key else None


# =====================================================
# ROLE BASED SKILLS
# =====================================================

ROLE_SKILLS = {

    "AI Engineer": [
        "python", "langchain", "langgraph", "crewai",
        "rag", "chromadb", "fastapi", "huggingface",
        "embeddings", "vector database", "llm",
        "generative ai", "groq", "git", "github",
        "streamlit"
    ],

    "Python Developer": [
        "python", "django", "flask", "fastapi",
        "sql", "mysql", "postgresql",
        "rest api", "git", "oop"
    ],

    "Full Stack Developer": [
        "html", "css", "javascript", "react",
        "django", "python", "mysql", "node"
    ],

    "Data Analyst": [
        "python", "sql", "excel", "power bi",
        "tableau", "pandas", "numpy",
        "matplotlib", "seaborn"
    ],

    "Software Engineer": [
        "python", "java", "sql",
        "data structures", "algorithms",
        "git", "oop"
    ],

    "Accountant": [
        "tally", "gst", "sap", "excel",
        "accounting", "bookkeeping",
        "accounts payable", "accounts receivable"
    ],

    "HR / Recruiter": [
        "recruitment", "sourcing",
        "linkedin", "naukri",
        "screening", "excel"
    ],

    "Customer Support": [
        "customer support", "crm",
        "communication", "email support",
        "chat support"
    ]
}


# =====================================================
# ALIASES
# =====================================================

ALIASES = {

    "vector database": [
        "chromadb",
        "pinecone",
        "faiss",
        "weaviate",
        "vector db"
    ],

    "huggingface": [
        "hugging face",
        "sentence-transformers"
    ],

    "rag": [
        "retrieval augmented generation"
    ],

    "llm": [
        "large language model"
    ],

    "github": [
        "github.com"
    ],

    "generative ai": [
        "gen ai",
        "genai"
    ],

    "fastapi": [
        "fast api"
    ]
}


# =====================================================
# NORMALIZE
# =====================================================

def normalize_text(text):

    text = text.lower()

    text = text.replace("–", "-")
    text = text.replace("—", "-")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# =====================================================
# PDF TEXT EXTRACTION
# =====================================================

def extract_text(uploaded_file):

    uploaded_file.seek(0)

    pdf = fitz.open(
        stream=uploaded_file.read(),
        filetype="pdf"
    )

    text = ""

    for page in pdf:
        text += page.get_text("text") + "\n"

    pdf.close()

    uploaded_file.seek(0)

    return text.strip()


# =====================================================
# RESUME PREVIEW
# =====================================================

def resume_preview(uploaded_file):

    uploaded_file.seek(0)

    pdf = fitz.open(
        stream=uploaded_file.read(),
        filetype="pdf"
    )

    page = pdf.load_page(0)

    pix = page.get_pixmap(
        matrix=fitz.Matrix(2, 2)
    )

    image = Image.open(
        io.BytesIO(
            pix.tobytes("png")
        )
    )

    pdf.close()

    uploaded_file.seek(0)

    return image


# =====================================================
# SKILL DETECTION
# =====================================================

def skill_exists(text, skill):

    text = normalize_text(text)

    keywords = [skill] + ALIASES.get(skill, [])

    for keyword in keywords:

        keyword = normalize_text(keyword)

        if len(keyword) <= 3:

            pattern = rf"\b{re.escape(keyword)}\b"

            if re.search(pattern, text):
                return True

        else:

            if keyword in text:
                return True

    return False


# =====================================================
# JOB DESCRIPTION MATCH
# =====================================================

def job_description_match(resume_text, job_description):

    if not job_description.strip():
        return 0, [], []

    resume_text = normalize_text(resume_text)
    jd_text = normalize_text(job_description)

    technical_keywords = []

    for skills in ROLE_SKILLS.values():
        technical_keywords.extend(skills)

    technical_keywords = sorted(set(technical_keywords))

    matched = []
    missing = []

    for keyword in technical_keywords:

        if skill_exists(jd_text, keyword):

            if skill_exists(resume_text, keyword):
                matched.append(keyword)
            else:
                missing.append(keyword)

    percentage = round(
        len(matched)
        / max(1, len(matched) + len(missing))
        * 100
    )

    return percentage, matched, missing


# =====================================================
# ATS SCORE
# =====================================================

def calculate_ats_score(
    resume_text,
    role,
    job_description=""
):

    text = normalize_text(resume_text)

    role_skills = ROLE_SKILLS.get(role, [])

    found = []
    missing = []

    for skill in role_skills:

        if skill_exists(text, skill):
            found.append(skill)
        else:
            missing.append(skill)

    skills_score = round(
        len(found)
        / max(1, len(role_skills))
        * 60
    )

    jd_percent, _, _ = job_description_match(
        resume_text,
        job_description
    )

    jd_score = round(jd_percent * 20 / 100)

    education_score = 5 if any(
        x in text for x in [
            "b.e",
            "btech",
            "engineering",
            "bachelor"
        ]
    ) else 0

    experience_score = 5 if any(
        x in text for x in [
            "experience",
            "work experience"
        ]
    ) else 0

    project_score = 5 if any(
        x in text for x in [
            "project",
            "projects"
        ]
    ) else 0

    total = min(
        100,
        skills_score
        + jd_score
        + education_score
        + experience_score
        + project_score
    )

    breakdown = {
        "skills": skills_score,
        "job_description": jd_score,
        "education": education_score,
        "projects": project_score
    }

    return (
        total,
        found,
        missing,
        missing[:10],
        breakdown
    )


# =====================================================
# GEMINI GENERATOR
# =====================================================

def gemini_generate(prompt):

    if client is None:
        return "⚠️ GEMINI_API_KEY not configured."

    # Try newer models first
    models = [
        "gemini-3.6-flash",
        "gemini-2.5-pro"
    ]

    last_error = ""

    for model in models:

        try:

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            if getattr(response, "text", None):
                return response.text

        except Exception as e:

            last_error = str(e)

            if (
                "API_KEY_INVALID" in last_error
                or "API key not valid" in last_error
            ):
                return "⚠️ Invalid Gemini API Key."

            if (
                "429" in last_error
                or "RESOURCE_EXHAUSTED" in last_error
            ):
                return "⚠️ Gemini quota exceeded."

    return f"⚠️ Gemini Error: {last_error}"


# =====================================================
# AI ANALYSIS
# =====================================================

def analyze_resume(
    resume_text,
    role,
    job_description=""
):

    prompt = f"""
You are an ATS Resume Reviewer.

Target Role:
{role}

Job Description:
{job_description if job_description else "Not provided"}

Return ONLY:

# Professional Summary

# Strengths

# Weaknesses

# Suggested Improvements

# Five Interview Questions

Use only information available in the resume.

Resume:
{resume_text}
"""

    return gemini_generate(prompt)


# =====================================================
# AI REWRITE
# =====================================================

def rewrite_resume(
    resume_text,
    role,
    job_description=""
):

    prompt = f"""
You are a professional ATS Resume Writer.

Rewrite this resume professionally.

Target Role:
{role}

Rules:
- Use ONLY genuine information.
- Do not invent companies, projects or experience.
- Improve formatting.
- Make it ATS-friendly.

Use sections:
1. Professional Summary
2. Technical Skills
3. Experience
4. Projects
5. Education

Resume:
{resume_text}
"""

    return gemini_generate(prompt)


# =====================================================
# PDF REPORT
# =====================================================

def generate_pdf_report(
    filename,
    role,
    score,
    found_skills,
    missing_skills,
    breakdown,
    ai_summary=""
):

    styles = getSampleStyleSheet()

    title = styles["Heading1"]
    title.alignment = TA_CENTER
    title.textColor = HexColor("#2563EB")

    doc = SimpleDocTemplate(filename)

    elements = []

    elements.append(
        Paragraph("AI Resume ATS Report", title)
    )

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(f"<b>Target Role:</b> {role}", styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>ATS Score:</b> {score}/100", styles["BodyText"])
    )

    elements.append(Spacer(1, 15))

    elements.append(
        Paragraph("Score Breakdown", styles["Heading2"])
    )

    for key, value in breakdown.items():

        elements.append(
            Paragraph(f"{key.title()}: {value}", styles["BodyText"])
        )

    elements.append(Spacer(1, 15))

    elements.append(
        Paragraph("Skills Found", styles["Heading2"])
    )

    elements.append(
        Paragraph(
            ", ".join(found_skills) if found_skills else "None",
            styles["BodyText"]
        )
    )

    elements.append(Spacer(1, 15))

    elements.append(
        Paragraph("Missing Skills", styles["Heading2"])
    )

    elements.append(
        Paragraph(
            ", ".join(missing_skills) if missing_skills else "None",
            styles["BodyText"]
        )
    )

    if ai_summary:

        elements.append(Spacer(1, 15))

        elements.append(
            Paragraph("AI Summary", styles["Heading2"])
        )

        elements.append(
            Paragraph(
                ai_summary.replace("\n", "<br/>"),
                styles["BodyText"]
            )
        )

    doc.build(elements)

    return filename


# =====================================================
# DOCX GENERATOR
# =====================================================

def generate_resume_docx(
    filename,
    rewritten_resume,
    role
):

    doc = Document()

    heading = doc.add_heading(
        "AI Rewritten Resume",
        1
    )

    heading.runs[0].font.size = Pt(22)

    doc.add_paragraph(f"Target Role: {role}")
    doc.add_paragraph()

    for line in rewritten_resume.split("\n"):

        line = line.strip()

        if not line:
            continue

        if line.startswith("# "):
            doc.add_heading(line[2:], 1)

        elif line.startswith("## "):
            doc.add_heading(line[3:], 2)

        elif line.startswith("- "):
            doc.add_paragraph(
                line[2:],
                style="List Bullet"
            )

        else:
            doc.add_paragraph(line)

    doc.save(filename)

    return filename