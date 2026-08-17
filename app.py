import streamlit as st

from analyzer import (
    extract_text,
    resume_preview,
    calculate_ats_score,
    job_description_match,
    analyze_resume,
    rewrite_resume,
    generate_pdf_report,
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
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.score-circle{
width:180px;
height:180px;
border-radius:50%;
display:flex;
align-items:center;
justify-content:center;
margin:auto;
background:
conic-gradient(#2563eb var(--score),#e5e7eb 0);
padding:12px;
}

.score-inner{
width:100%;
height:100%;
background:white;
border-radius:50%;
display:flex;
flex-direction:column;
align-items:center;
justify-content:center;
}

.score-number{
font-size:42px;
font-weight:bold;
color:#111827;
}

.score-label{
font-size:14px;
color:#6b7280;
text-align:center;
}

.skill-found{
display:inline-block;
background:#dcfce7;
color:#166534;
padding:8px 12px;
border-radius:20px;
margin:5px;
font-weight:600;
}

.skill-missing{
display:inline-block;
background:#fee2e2;
color:#991b1b;
padding:8px 12px;
border-radius:20px;
margin:5px;
font-weight:600;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.title("📄 AI Resume Analyzer")
st.write("Upload any resume and get **ATS + AI-powered feedback.**")

st.markdown("## 🤖 AI Resume Analysis")
st.caption("Powered by Gemini + Python ATS Engine")

# =====================================================
# TARGET ROLE
# =====================================================

st.subheader("🎯 Select Target Role")

target_role = st.selectbox(
    "Target Role",
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

st.subheader("📤 Upload Resume (PDF)")

uploaded_file = st.file_uploader(
    "Choose your resume",
    type=["pdf"]
)

# =====================================================
# JOB DESCRIPTION
# =====================================================

st.subheader("📋 Paste Job Description (Optional)")

job_description = st.text_area(
    "Job Description",
    placeholder="Example: Looking for a Python Developer with FastAPI, SQL, Git and REST APIs...",
    height=150
)

# =====================================================
# MAIN APP
# =====================================================

if uploaded_file:

    st.success("✅ Resume uploaded successfully!")

    try:
        resume_text = extract_text(uploaded_file)

        if not resume_text.strip():
            st.error("No readable text found in this PDF.")
            st.stop()

    except Exception as e:
        st.error(f"Text extraction failed: {e}")
        st.stop()

    # Resume Preview

    st.subheader("👀 Resume Preview")

    try:
        preview = resume_preview(uploaded_file)
        st.image(preview, caption="First page of uploaded resume")
    except:
        st.warning("Preview unavailable.")

    # ATS

    (
        score,
        found_skills,
        missing_skills,
        improvement_skills,
        breakdown
    ) = calculate_ats_score(
        resume_text,
        target_role,
        job_description
    )

    st.divider()

    st.subheader("📊 ATS Score")

    angle = score * 3.6

    st.markdown(
        f"""
        <div class="score-circle" style="--score:{angle}deg;">
            <div class="score-inner">
                <div class="score-number">{score}</div>
                <div class="score-label">ATS Score /100</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if score >= 80:
        st.success("🎉 Excellent ATS Score!")

    elif score >= 60:
        st.success("👍 Good score. A few improvements can make it stronger.")

    elif score >= 40:
        st.warning("⚠️ Average score.")

    else:
        st.error("Resume needs improvement.")

    st.info(f"ATS evaluated for: **{target_role}**")

    # Breakdown

    st.subheader("📈 Score Breakdown")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Skills", breakdown["skills"])
    c2.metric("JD Match", breakdown["job_description"])
    c3.metric("Education", breakdown["education"])
    c4.metric("Projects", breakdown["projects"])

    # JD Match

    if job_description.strip():

        st.divider()

        st.subheader("🎯 Resume vs Job Description Match")

        percentage, matched, missing = job_description_match(
            resume_text,
            job_description
        )

        st.metric("Match", f"{percentage}%")
        st.progress(percentage / 100)

        col1, col2 = st.columns(2)

        with col1:

            st.markdown("### 🟢 Matched Keywords")

            if matched:

                html = ""

                for word in matched:
                    html += f"<span class='skill-found'>✓ {word.title()}</span>"

                st.markdown(html, unsafe_allow_html=True)

            else:
                st.info("No matched keywords.")

        with col2:

            st.markdown("### 🔴 Missing Keywords")

            if missing:

                html = ""

                for word in missing[:20]:
                    html += f"<span class='skill-missing'>✗ {word.title()}</span>"

                st.markdown(html, unsafe_allow_html=True)

            else:
                st.success("No important keywords missing.")

    # Skills

    st.divider()

    st.subheader("✅ Skills Found")

    if found_skills:

        html = ""

        for skill in found_skills:
            html += f"<span class='skill-found'>✓ {skill.title()}</span>"

        st.markdown(html, unsafe_allow_html=True)

    else:
        st.info("No skills detected.")

    st.subheader("❌ Missing Skills")

    if missing_skills:

        html = ""

        for skill in missing_skills:
            html += f"<span class='skill-missing'>✗ {skill.title()}</span>"

        st.markdown(html, unsafe_allow_html=True)

    else:
        st.success("🎉 No important skills missing.")

    # Suggestions

    st.subheader("💡 Improvement Suggestions")

    if improvement_skills:

        for skill in improvement_skills:
            st.write(f"👉 **{skill.title()}**")

    else:
        st.success("Your resume already contains the important skills.")

    # =====================================================
    # AI ANALYSIS
    # =====================================================

    st.divider()

    st.subheader("🤖 AI Resume Analysis")

    if st.button("Analyze Resume", use_container_width=True):

        with st.spinner("Gemini is analyzing..."):

            result = analyze_resume(
                resume_text,
                target_role,
                job_description
            )

        st.markdown(result)

    # =====================================================
    # AI REWRITE
    # =====================================================

    st.divider()

    st.subheader("✍️ AI Resume Rewrite")

    if st.button("Rewrite Resume", use_container_width=True):

        with st.spinner("Rewriting..."):

            rewritten = rewrite_resume(
                resume_text,
                target_role,
                job_description
            )

        if rewritten and not rewritten.startswith("⚠️"):

            st.markdown(rewritten)

            st.download_button(
                "📥 Download Markdown",
                rewritten,
                file_name="rewritten_resume.md"
            )

            docx = generate_resume_docx(
                "Rewritten_Resume.docx",
                rewritten,
                target_role
            )

            with open(docx, "rb") as f:

                st.download_button(
                    "📄 Download DOCX Resume",
                    f,
                    file_name="Rewritten_Resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        else:
            st.error(rewritten)

    # =====================================================
    # PDF REPORT
    # =====================================================

    st.divider()

    st.subheader("📄 ATS Report")

    if st.button("Generate PDF Report", use_container_width=True):

        pdf = generate_pdf_report(
            "ATS_Report.pdf",
            target_role,
            score,
            found_skills,
            missing_skills,
            breakdown
        )

        with open(pdf, "rb") as f:

            st.download_button(
                "📥 Download ATS Report",
                f,
                file_name="ATS_Report.pdf",
                mime="application/pdf"
            )

    # =====================================================
    # EXTRACTED TEXT
    # =====================================================

    st.divider()

    with st.expander("🔍 View Extracted Resume Text"):

        st.text_area(
            "Extracted Resume Text",
            resume_text,
            height=350
        )

        c1, c2 = st.columns(2)

        c1.metric("Words", len(resume_text.split()))
        c2.metric("Characters", len(resume_text))