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
# SESSION STATE
# =====================================================

if "analysis" not in st.session_state:
    st.session_state.analysis = ""

if "rewrite" not in st.session_state:
    st.session_state.rewrite = ""

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 20px;
    }

    .score-circle {
        width: 180px;
        height: 180px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: auto;
        background:
            conic-gradient(#2563eb var(--score), #e5e7eb 0);
        padding: 12px;
    }

    .score-inner {
        width: 100%;
        height: 100%;
        background: white;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    .score-number {
        font-size: 42px;
        font-weight: bold;
        color: #111827;
    }

    .score-label {
        font-size: 14px;
        color: #6b7280;
    }

    .skill-found {
        display: inline-block;
        background: #dcfce7;
        color: #166534;
        padding: 8px 12px;
        border-radius: 20px;
        margin: 4px;
        font-weight: 600;
    }

    .skill-missing {
        display: inline-block;
        background: #fee2e2;
        color: #991b1b;
        padding: 8px 12px;
        border-radius: 20px;
        margin: 4px;
        font-weight: 600;
    }

    .block-container {
        padding-top: 2rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# HEADER
# =====================================================

st.title("📄 AI Resume Analyzer")

st.write(
    "Upload any resume and get **ATS + AI-powered feedback.**"
)

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
    placeholder="Paste job description here..."
)

# =====================================================
# MAIN APP
# =====================================================

if uploaded_file:

    st.success("✅ Resume uploaded successfully!")

    # =================================================
    # EXTRACT TEXT
    # =================================================

    resume_text = extract_text(uploaded_file)

    # =================================================
    # RESUME PREVIEW
    # =================================================

    st.subheader("👀 Resume Preview")

    preview = resume_preview(uploaded_file)

    st.image(
        preview,
        caption="First page of uploaded resume"
    )

    # =================================================
    # ATS SCORE
    # =================================================

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

    # =================================================
    # SCORE MESSAGE
    # =================================================

    if score >= 80:
        st.success("🎉 Excellent ATS Score!")

    elif score >= 60:
        st.success(
            "👍 Good score. A few improvements can make it stronger."
        )

    elif score >= 40:
        st.warning(
            "⚠️ Average score. Improve your resume."
        )

    else:
        st.error(
            "❌ Resume needs improvement."
        )

    st.info(
        f"ATS evaluated for: **{target_role}**"
    )

    # =================================================
    # SCORE BREAKDOWN
    # =================================================

    st.subheader("📈 Score Breakdown")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Skills",
        breakdown["skills"]
    )

    c2.metric(
        "JD Match",
        breakdown["job_description"]
    )

    c3.metric(
        "Education",
        breakdown["education"]
    )

    c4.metric(
        "Projects",
        breakdown["projects"]
    )

    # =================================================
    # JOB DESCRIPTION MATCH
    # =================================================

    if job_description.strip():

        st.divider()

        st.subheader(
            "🎯 Resume vs Job Description Match"
        )

        percentage, matched, missing = job_description_match(
            resume_text,
            job_description
        )

        st.metric(
            "Match",
            f"{percentage}%"
        )

        st.progress(
            percentage / 100
        )

        if percentage >= 80:

            st.success(
                "Excellent Job Description Match."
            )

        elif percentage >= 60:

            st.warning(
                "Good match. Add missing keywords."
            )

        else:

            st.error(
                "Low match. Resume needs optimization."
            )

        left, right = st.columns(2)

        # =============================================
        # MATCHED KEYWORDS
        # =============================================

        with left:

            st.markdown(
                "### 🟢 Matched Keywords"
            )

            if matched:

                html = ""

                for word in matched:

                    html += (
                        f"<span class='skill-found'>"
                        f"✓ {word.title()}"
                        f"</span>"
                    )

                st.markdown(
                    html,
                    unsafe_allow_html=True
                )

            else:

                st.info(
                    "No matched keywords found."
                )

        # =============================================
        # MISSING KEYWORDS
        # =============================================

        with right:

            st.markdown(
                "### 🔴 Missing Keywords"
            )

            if missing:

                html = ""

                for word in missing[:20]:

                    html += (
                        f"<span class='skill-missing'>"
                        f"✗ {word.title()}"
                        f"</span>"
                    )

                st.markdown(
                    html,
                    unsafe_allow_html=True
                )

            else:

                st.success(
                    "No important keywords missing."
                )

    # =================================================
    # SKILLS FOUND
    # =================================================

    st.divider()

    st.subheader("✅ Skills Found")

    if found_skills:

        html = ""

        for skill in found_skills:

            html += (
                f"<span class='skill-found'>"
                f"✓ {skill.title()}"
                f"</span>"
            )

        st.markdown(
            html,
            unsafe_allow_html=True
        )

    else:

        st.info(
            "No skills detected."
        )

    # =================================================
    # MISSING SKILLS
    # =================================================

    st.subheader("❌ Missing Skills")

    if missing_skills:

        html = ""

        for skill in missing_skills:

            html += (
                f"<span class='skill-missing'>"
                f"✗ {skill.title()}"
                f"</span>"
            )

        st.markdown(
            html,
            unsafe_allow_html=True
        )

    else:

        st.success(
            "🎉 No important skills missing."
        )

    # =================================================
    # IMPROVEMENT SUGGESTIONS
    # =================================================

    st.subheader(
        "💡 Improvement Suggestions"
    )

    if improvement_skills:

        st.write(
            "Add only the skills you genuinely know."
        )

        for skill in improvement_skills:

            st.write(
                f"👉 **{skill.title()}**"
            )

    else:

        st.success(
            "Your resume already contains the important skills."
        )

    # =================================================
    # AI RESUME ANALYSIS
    # =================================================

    st.divider()

    st.subheader(
        "🤖 AI Resume Analysis"
    )

    if st.button(
        "Analyze Resume",
        key="analyze_resume_button"
    ):

        with st.spinner(
            "Gemini is analyzing your resume..."
        ):

            st.session_state.analysis = analyze_resume(
                resume_text,
                target_role,
                job_description
            )

    if st.session_state.analysis:

        st.markdown(
            st.session_state.analysis
        )

    # =================================================
    # AI RESUME REWRITE
    # =================================================

    st.divider()

    st.subheader(
        "✍️ AI Resume Rewrite"
    )

    if st.button(
        "Rewrite Resume",
        key="rewrite_resume_button"
    ):

        with st.spinner(
            "Generating ATS-friendly rewritten resume..."
        ):

            st.session_state.rewrite = rewrite_resume(
                resume_text,
                target_role,
                job_description
            )

    if st.session_state.rewrite:

        st.markdown(
            st.session_state.rewrite
        )

        # =============================================
        # MARKDOWN DOWNLOAD
        # =============================================

        st.download_button(
            "📥 Download Markdown",
            data=st.session_state.rewrite,
            file_name="rewritten_resume.md",
            mime="text/markdown",
            key="download_markdown"
        )

        # =============================================
        # DOCX GENERATION
        # =============================================

        docx_file = generate_resume_docx(
            "Rewritten_Resume.docx",
            st.session_state.rewrite,
            target_role
        )

        with open(
            docx_file,
            "rb"
        ) as f:

            st.download_button(
                "📄 Download DOCX Resume",
                data=f,
                file_name="Rewritten_Resume.docx",
                mime=(
                    "application/vnd.openxmlformats-"
                    "officedocument.wordprocessingml.document"
                ),
                key="download_docx"
            )

    # =================================================
    # PDF REPORT
    # =================================================

    st.divider()

    st.subheader(
        "📄 ATS Report"
    )

    if st.button(
        "Generate PDF Report",
        key="generate_pdf_button"
    ):

        pdf = generate_pdf_report(
            "ATS_Report.pdf",
            target_role,
            score,
            found_skills,
            missing_skills,
            breakdown,
            st.session_state.analysis
        )

        with open(
            pdf,
            "rb"
        ) as f:

            st.download_button(
                "📥 Download ATS Report",
                data=f,
                file_name="ATS_Report.pdf",
                mime="application/pdf",
                key="download_pdf"
            )

    # =================================================
    # EXTRACTED TEXT
    # =================================================

    st.divider()

    with st.expander(
        "🔍 View Extracted Resume Text"
    ):

        st.text_area(
            "Extracted Resume Text",
            resume_text,
            height=300
        )

# =====================================================
# NO RESUME MESSAGE
# =====================================================

else:

    st.info(
        "📤 Please upload a PDF resume to start the analysis."
    )

