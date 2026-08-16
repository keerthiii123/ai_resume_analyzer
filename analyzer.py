import fitz
import os
import re
import io
import time

from PIL import Image
from dotenv import load_dotenv
from google import genai

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
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

    "AI Engineer":[
        "python","langchain","langgraph","crewai",
        "rag","chromadb","fastapi","huggingface",
        "embeddings","vector database","llm",
        "generative ai","groq","git","github",
        "streamlit"
    ],

    "Python Developer":[
        "python","django","flask","fastapi",
        "sql","mysql","postgresql",
        "rest api","git","oop"
    ],

    "Full Stack Developer":[
        "html","css","javascript","react",
        "django","python","mysql","node"
    ],

    "Data Analyst":[
        "python","sql","excel","power bi",
        "tableau","pandas","numpy",
        "matplotlib","seaborn"
    ],

    "Software Engineer":[
        "python","java","sql",
        "data structures","algorithms",
        "git","oop"
    ],

    "Accountant":[
        "tally","gst","sap","excel",
        "accounting","bookkeeping",
        "accounts payable","accounts receivable"
    ],

    "HR / Recruiter":[
        "recruitment","sourcing",
        "linkedin","naukri",
        "screening","excel"
    ],

    "Customer Support":[
        "customer support","crm",
        "communication","email support",
        "chat support"
    ]
}

# =====================================================
# ALIASES
# =====================================================

ALIASES = {
    "vector database":["chromadb","pinecone","faiss","weaviate"],
    "huggingface":["hugging face","sentence-transformers"],
    "rag":["retrieval augmented generation"],
    "llm":["large language model"],
    "github":["github.com"]
}

# =====================================================
# PDF TEXT EXTRACTION
# =====================================================

def extract_text(uploaded_file):

    uploaded_file.seek(0)

    doc = fitz.open(
        stream=uploaded_file.read(),
        filetype="pdf"
    )

    text = ""

    for page in doc:
        text += page.get_text()

    uploaded_file.seek(0)

    return text

# =====================================================
# RESUME PREVIEW
# =====================================================

def resume_preview(uploaded_file):

    uploaded_file.seek(0)

    doc = fitz.open(
        stream=uploaded_file.read(),
        filetype="pdf"
    )

    page = doc.load_page(0)

    pix = page.get_pixmap(matrix=fitz.Matrix(2,2))

    image = Image.open(io.BytesIO(pix.tobytes("png")))

    uploaded_file.seek(0)

    return image

# =====================================================
# JOB DESCRIPTION MATCH
# =====================================================

def job_description_match(resume_text, job_description):

    if not job_description.strip():
        return 0, [], []

    resume_words = set(
        re.findall(
            r"[a-zA-Z][a-zA-Z0-9+.#-]{2,}",
            resume_text.lower()
        )
    )

    jd_words = set(
        re.findall(
            r"[a-zA-Z][a-zA-Z0-9+.#-]{2,}",
            job_description.lower()
        )
    )

    stop_words = {
        "the","and","for","with","you","your",
        "developer","engineer","experience",
        "looking","our"
    }

    jd_words -= stop_words

    matched = sorted(jd_words & resume_words)
    missing = sorted(jd_words - resume_words)

    percentage = round(
        len(matched)/max(1,len(jd_words))*100
    )

    return percentage, matched, missing

# =====================================================
# ATS SCORE
# =====================================================

def calculate_ats_score(resume_text, role, job_description=""):

    text = re.sub(r"\s+"," ",resume_text.lower())

    role_skills = ROLE_SKILLS.get(role,[])

    found_skills=[]
    missing_skills=[]

    for skill in role_skills:

        keywords=[skill]+ALIASES.get(skill,[])

        found=False

        for keyword in keywords:

            if keyword.lower() in text:
                found=True
                break

        if found:
            found_skills.append(skill)
        else:
            missing_skills.append(skill)

    skills_score=round(
        len(found_skills)/max(1,len(role_skills))*60
    )

    jd_percentage,_,_=job_description_match(
        resume_text,
        job_description
    )

    jd_score=round(jd_percentage*20/100)

    education_score=5 if any(
        x in text for x in [
            "b.e","btech","engineering","education"
        ]
    ) else 0

    experience_score=5 if "experience" in text else 0
    project_score=5 if "project" in text else 0

    total=min(
        100,
        skills_score+
        jd_score+
        education_score+
        experience_score+
        project_score
    )

    breakdown={
        "skills":skills_score,
        "job_description":jd_score,
        "education":education_score,
        "projects":project_score
    }

    return (
        total,
        found_skills,
        missing_skills,
        missing_skills[:10],
        breakdown
    )

# =====================================================
# GEMINI GENERATOR
# =====================================================

def gemini_generate(prompt):

    if client is None:
        return "⚠️ GEMINI_API_KEY not configured."

    models=[
        "gemini-flash-latest",
        "gemini-3.7-flash",
        "gemini-3.6-flash"
    ]

    last_error=""

    for model in models:

        try:

            response=client.models.generate_content(
                model=model,
                contents=prompt
            )

            if getattr(response,"text",""):
                return response.text

        except Exception as e:

            last_error=str(e)

            if "429" in last_error:
                return "⚠️ Gemini free-tier quota exceeded."

            if "503" in last_error:
                time.sleep(2)

    return f"⚠️ Gemini Error: {last_error}"

# =====================================================
# AI ANALYSIS
# =====================================================

def analyze_resume(resume_text,role,job_description=""):

    prompt=f"""
You are an expert ATS Resume Reviewer.

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

Resume:

{resume_text}
"""

    return gemini_generate(prompt)

# =====================================================
# AI REWRITE
# =====================================================

def rewrite_resume(resume_text,role,job_description=""):

    prompt=f"""
Rewrite this resume professionally.

Rules:

- Use ONLY genuine information.
- ATS friendly.
- One-page format.
- Target Role: {role}

Job Description:
{job_description if job_description else "Not provided"}

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

    styles=getSampleStyleSheet()

    title=styles["Heading1"]
    title.alignment=TA_CENTER
    title.textColor=HexColor("#2563EB")

    doc=SimpleDocTemplate(filename)

    elements=[]

    elements.append(Paragraph("AI Resume ATS Report",title))
    elements.append(Spacer(1,20))

    elements.append(
        Paragraph(f"<b>Target Role:</b> {role}",styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>ATS Score:</b> {score}/100",styles["BodyText"])
    )

    elements.append(Spacer(1,15))

    elements.append(Paragraph("Score Breakdown",styles["Heading2"]))

    for k,v in breakdown.items():
        elements.append(
            Paragraph(f"{k.title()}: {v}",styles["BodyText"])
        )

    elements.append(Spacer(1,15))

    elements.append(Paragraph("Skills Found",styles["Heading2"]))
    elements.append(
        Paragraph(", ".join(found_skills) if found_skills else "None",
                  styles["BodyText"])
    )

    elements.append(Spacer(1,15))

    elements.append(Paragraph("Missing Skills",styles["Heading2"]))
    elements.append(
        Paragraph(", ".join(missing_skills) if missing_skills else "None",
                  styles["BodyText"])
    )

    if ai_summary:

        elements.append(Spacer(1,15))
        elements.append(Paragraph("AI Summary",styles["Heading2"]))
        elements.append(
            Paragraph(ai_summary.replace("\n","<br/>"),
                      styles["BodyText"])
        )

    doc.build(elements)

    return filename

# =====================================================
# DOCX RESUME DOWNLOAD
# =====================================================

def generate_resume_docx(filename,rewritten_resume,role):

    doc=Document()

    heading=doc.add_heading("AI Rewritten Resume",1)
    heading.runs[0].font.size=Pt(22)

    doc.add_paragraph(f"Target Role: {role}")
    doc.add_paragraph()

    for line in rewritten_resume.split("\n"):

        line=line.strip()

        if not line:
            continue

        if line.startswith("# "):
            doc.add_heading(line[2:],1)

        elif line.startswith("## "):
            doc.add_heading(line[3:],2)

        elif line.startswith("- "):
            doc.add_paragraph(line[2:],style="List Bullet")

        else:
            doc.add_paragraph(line)

    doc.save(filename)

    return filename