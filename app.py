import streamlit as st

from analyzer import (
    extract_text,
    resume_preview,
    calculate_ats_score,
    analyze_resume,
    rewrite_resume,
    generate_pdf_report,
    job_description_match,
    generate_resume_docx
)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# =====================================================
# CSS
# =====================================================

st.markdown("""
<style>

.main-title{
text-align:center;
font-size:42px;
font-weight:bold;
color:#2563EB;
}

.subtitle{
text-align:center;
color:#6B7280;
font-size:18px;
margin-bottom:25px;
}

.top-card{
background:linear-gradient(135deg,#111827,#1E3A8A);
padding:20px;
border-radius:18px;
text-align:center;
color:white;
margin-bottom:25px;
}

.score-wrapper{
display:flex;
justify-content:center;
margin:20px 0;
}

.score-circle{
width:220px;
height:220px;
border-radius:50%;
background:conic-gradient(#2563EB var(--score),#E5E7EB 0deg);
display:flex;
justify-content:center;
align-items:center;
}

.score-inner{
width:165px;
height:165px;
background:white;
border-radius:50%;
display:flex;
flex-direction:column;
justify-content:center;
align-items:center;
}

.score-number{
font-size:48px;
font-weight:bold;
color:#111827;
}

.score-label{
font-size:14px;
color:#6B7280;
}

.skill-found{
display:inline-block;
background:#DCFCE7;
color:#166534;
padding:8px 14px;
border-radius:999px;
margin:5px;
font-weight:600;
}

.skill-missing{
display:inline-block;
background:#FEE2E2;
color:#991B1B;
padding:8px 14px;
border-radius:999px;
margin:5px;
font-weight:600;
}

.tip-card{
background:#EFF6FF;
padding:15px;
border-left:5px solid #2563EB;
border-radius:10px;
margin:15px 0;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.markdown(
    "<div class='main-title'>📄 AI Resume Analyzer</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='subtitle'>Upload any resume and get ATS + AI-powered feedback.</div>",
    unsafe_allow_html=True
)

st.markdown("""
<div class="top-card">
<h2>🤖 AI Resume Analysis</h2>
<p>Powered by Gemini + Python ATS Engine</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# TARGET ROLE
# =====================================================

target_role = st.selectbox(
    "🎯 Select Target Role",
    [
        "AI Engineer",
        "Python Developer",
        "Full Stack Developer",
        "Data Analyst",
        "Software Engineer",
        "Accountant",
        "HR / Recruiter",
        "Customer Support"
    ]
)

# =====================================================
# FILE UPLOAD
# =====================================================

uploaded_file = st.file_uploader(
    "📤 Upload Resume (PDF)",
    type=["pdf"]
)

# =====================================================
# JOB DESCRIPTION
# =====================================================

job_description = st.text_area(
    "📋 Paste Job Description (Optional)",
    height=150,
    placeholder="Example: We need a Python Developer with FastAPI, SQL and Git..."
)

# =====================================================
# MAIN
# =====================================================

if uploaded_file:

    st.success("✅ Resume uploaded successfully!")

    # ---------------- Resume Preview ----------------

    st.subheader("👀 Resume Preview")

    preview = resume_preview(uploaded_file)

    st.image(
        preview,
        caption="First page of uploaded resume",
        use_container_width=True
    )

    # ---------------- Resume Text ----------------

    with st.spinner("Reading resume..."):

        resume_text = extract_text(uploaded_file)

    # ---------------- ATS ----------------

    score, found_skills, missing_skills, improvement_skills, breakdown = calculate_ats_score(
        resume_text,
        target_role,
        job_description
    )

    st.divider()

    st.subheader("📊 ATS Score")

    angle = score * 3.6

    st.markdown(f"""
<div class="score-wrapper">
<div class="score-circle" style="--score:{angle}deg;">
<div class="score-inner">
<div class="score-number">{score}</div>
<div class="score-label">ATS Score /100</div>
</div>
</div>
</div>
""", unsafe_allow_html=True)

    if score >= 80:
        st.success("🎉 Excellent ATS Score!")
    elif score >= 60:
        st.warning("👍 Good score.")
    else:
        st.error("⚠️ Improve your resume.")

    st.info(f"ATS evaluated for: **{target_role}**")

    # ---------------- Breakdown ----------------

    st.subheader("📈 Score Breakdown")

    c1,c2,c3,c4 = st.columns(4)

    c1.metric("Skills", breakdown["skills"])
    c2.metric("JD Match", breakdown["job_description"])
    c3.metric("Education", breakdown["education"])
    c4.metric("Projects", breakdown["projects"])

    # ---------------- Skills ----------------

    st.divider()

    st.subheader("✅ Skills Found")

    if found_skills:

        html=""

        for s in found_skills:
            html += f"<span class='skill-found'>✓ {s.title()}</span>"

        st.markdown(html, unsafe_allow_html=True)

    st.subheader("❌ Missing Skills")

    if missing_skills:

        html=""

        for s in missing_skills:
            html += f"<span class='skill-missing'>✗ {s.title()}</span>"

        st.markdown(html, unsafe_allow_html=True)

    # ---------------- Improvement ----------------

    st.divider()

    st.subheader("💡 Improvement Suggestions")

    st.markdown("""
<div class="tip-card">
Add only the skills you genuinely know.
</div>
""", unsafe_allow_html=True)

    for s in improvement_skills:
        st.write(f"👉 **{s.title()}**")

    # ---------------- Gemini ----------------

    st.divider()

    st.subheader("🤖 AI Resume Analysis")

    ai_result=""

    if st.button("Analyze with Gemini"):

        with st.spinner("Gemini is analyzing..."):

            ai_result = analyze_resume(
                resume_text,
                target_role,
                job_description
            )

        st.markdown(ai_result)

    # ---------------- Rewrite ----------------

    st.divider()

    st.subheader("✍️ AI Resume Rewrite")

    if st.button("Rewrite Resume"):

        with st.spinner("Rewriting..."):

            rewritten = rewrite_resume(
                resume_text,
                target_role,
                job_description
            )

        st.markdown(rewritten)

        st.download_button(
            "📥 Download Rewritten Resume",
            rewritten,
            file_name="rewritten_resume.md"
        )

    # ---------------- PDF Report ----------------

    st.divider()

    st.subheader("📄 ATS Report")

    if st.button("Generate PDF Report"):

        pdf_file = generate_pdf_report(
            filename="ATS_Report.pdf",
            role=target_role,
            score=score,
            found_skills=found_skills,
            missing_skills=missing_skills,
            breakdown=breakdown,
            ai_summary=ai_result
        )

        with open(pdf_file,"rb") as f:

            st.download_button(
                "⬇️ Download ATS Report",
                f,
                file_name="ATS_Report.pdf",
                mime="application/pdf"
            )

    # ---------------- Extracted Text ----------------

    with st.expander("🔍 View Extracted Resume Text"):

        st.text(resume_text)