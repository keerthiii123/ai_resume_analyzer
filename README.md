# 📄 AI Resume Analyzer

An AI-powered Resume Analyzer built using **Python, Streamlit, Gemini AI, and ATS-based resume analysis**.

The application analyzes a resume against a selected target role and optional job description. It provides an ATS score, skill analysis, missing keywords, AI-powered feedback, resume rewriting, and downloadable reports.

---

## 🚀 Features

### 📊 ATS Resume Scoring

* Calculates an ATS score out of 100
* Role-based skill evaluation
* Education detection
* Experience detection
* Project detection
* Job description matching

### 🎯 Job Description Matching

Users can paste a job description and compare it with their resume.

The application identifies:

* 🟢 Matched keywords
* 🔴 Missing keywords
* 📈 Job description match percentage

### 🧠 AI Resume Analysis

Gemini AI analyzes the uploaded resume and provides:

* Professional Summary
* Strengths
* Weaknesses
* Suggested Improvements
* Interview Questions

### ✍️ AI Resume Rewrite

The application generates an ATS-friendly version of the resume using Gemini AI.

The rewrite follows important rules:

* Uses only genuine information
* Does not invent companies
* Does not invent projects
* Does not invent experience
* Improves grammar and professional wording
* Optimizes the resume for the selected target role

### 📥 Resume Downloads

Users can download the rewritten resume as:

* Markdown
* DOCX

### 📄 ATS Report

The application generates a downloadable PDF report containing:

* Target role
* ATS score
* Score breakdown
* Skills found
* Missing skills
* AI analysis

### 👀 Resume Preview

The first page of the uploaded PDF resume is displayed inside the application.

---

## 🛠️ Technologies Used

| Technology    | Purpose                          |
| ------------- | -------------------------------- |
| Python        | Backend and application logic    |
| Streamlit     | Web application UI               |
| Gemini API    | AI resume analysis and rewriting |
| PyMuPDF       | PDF text extraction and preview  |
| Pillow        | Image processing                 |
| ReportLab     | PDF report generation            |
| python-docx   | DOCX resume generation           |
| python-dotenv | Environment variable management  |
| Regex         | Text and skill detection         |

---

## 🏗️ Project Architecture

```text
AI Resume Analyzer
│
├── app.py
│   └── Streamlit user interface
│
├── analyzer.py
│   ├── PDF text extraction
│   ├── Resume preview
│   ├── Skill detection
│   ├── ATS score calculation
│   ├── Job description matching
│   ├── Gemini AI analysis
│   ├── AI resume rewriting
│   ├── PDF report generation
│   └── DOCX generation
│
├── requirements.txt
│
├── .env
│
└── README.md
```

---

## 📂 Project Structure

```text
ai_resume_analyzer/
│
├── app.py
├── analyzer.py
├── requirements.txt
├── README.md
├── .gitignore
└── .env
```

> ⚠️ Never upload your `.env` file or Gemini API key to GitHub.

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/ai-resume-analyzer.git
```

Move into the project directory:

```bash
cd ai-resume-analyzer
```

---

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Gemini API Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

The application uses the Gemini API for:

* AI Resume Analysis
* Resume Rewriting
* Resume Recommendations
* Interview Question Generation

### 🔐 Security

Never commit your API key to GitHub.

Add this to `.gitignore`:

```text
.env
venv/
__pycache__/
*.pyc
```

---

## ▶️ Run the Application

Start Streamlit:

```bash
streamlit run app.py
```

The application will open in your browser.

Usually:

```text
http://localhost:8501
```

---

## 🔄 Application Workflow

```text
Upload Resume
      ↓
Extract PDF Text
      ↓
Select Target Role
      ↓
Calculate ATS Score
      ↓
Detect Skills
      ↓
Check Missing Skills
      ↓
Paste Job Description
      ↓
Calculate JD Match
      ↓
Gemini AI Analysis
      ↓
AI Resume Rewrite
      ↓
Download Resume / ATS Report
```

---

## 📊 ATS Score Calculation

The ATS score is calculated using multiple factors.

| Category              | Maximum Score |
| --------------------- | ------------: |
| Role-based Skills     |            60 |
| Job Description Match |            20 |
| Education             |             5 |
| Experience            |             5 |
| Projects              |             5 |
| **Total**             |        **95** |

The application limits the final score to a maximum of **100**.

---

## 🎯 Supported Target Roles

Currently supported roles include:

* AI Engineer
* Python Developer
* Full Stack Developer
* Data Analyst
* Software Engineer
* Accountant
* HR / Recruiter
* Customer Support

Each role has its own set of relevant technical or professional skills.

---

## 🧠 Gemini AI Prompt Safety

The AI resume rewriting system is designed to avoid creating false information.

It follows rules such as:

```text
Use ONLY genuine information from the original resume.

Do NOT invent:
- Companies
- Projects
- Experience
- Skills
- Dates
- Achievements
```

This helps keep the rewritten resume truthful and professional.

---

## 📸 Application Screenshots

Add your screenshots here after taking them from the Streamlit application.

```text
screenshots/
│
├── home.png
├── ats-score.png
├── jd-match.png
├── ai-analysis.png
└── resume-rewrite.png
```

Example:

```markdown
![Home](screenshots/home.png)
```

---

## 💡 Future Improvements

Possible future enhancements:

* [ ] Support DOCX resumes
* [ ] Support multiple resume formats
* [ ] Improve ATS scoring algorithm
* [ ] Add semantic similarity using embeddings
* [ ] Add resume section detection
* [ ] Add LinkedIn profile analysis
* [ ] Add multiple job description comparison
* [ ] Add resume templates
* [ ] Add user authentication
* [ ] Add resume version history
* [ ] Deploy the application online
* [ ] Add database support
* [ ] Add interview preparation chatbot

---

## 🎓 What I Learned

Through this project, I worked with:

* Python application development
* Streamlit
* Gemini Generative AI API
* Prompt engineering
* PDF processing
* Resume parsing
* ATS scoring
* Keyword matching
* Regular expressions
* DOCX generation
* PDF generation
* Environment variables
* AI-powered text generation

---

## 👩‍💻 Author

**Keerthana P**

AI Engineer | Python | GenAI | LangChain | Streamlit

---

## ⭐ Project Goal

The goal of this project is to help job seekers understand how well their resume matches a target role and improve their resume using AI-powered recommendations while keeping the information truthful.

If you find this project useful, consider giving it a ⭐ on GitHub.
