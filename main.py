import streamlit as st
import pandas as pd
import base64

from auth import login, signup, init_user_db
from job_db import (
    init_job_db, add_job, get_user_jobs,
    delete_job, edit_job, save_resume,
    get_resumes_for_job
)
from helper import (
    extract_text_from_pdf, extract_text_from_txt,
    extract_email, extract_phone, rank_resumes
)
from email_service import send_email
from utils.email_templates import get_shortlisted_email, get_rejected_email

#-------------prebuild skill database--------------
skill_database = {
    "Programming Languages": ["Python", "Java", "C++", "JavaScript", "SQL", "R", "Go", "Ruby"],
    "Frameworks": ["Django", "Flask", "React", "Angular", "Vue", "Spring", "TensorFlow", "PyTorch"],
    "Tools": ["Docker", "Kubernetes", "AWS", "Azure", "Git", "Linux", "Terraform"],
    "Databases": ["MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle", "Cassandra"],
    "Others": ["Machine Learning", "Data Analysis", "Cloud Computing", "DevOps", "Agile"]
}

# ---------- INIT ----------
init_user_db()
init_job_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email" not in st.session_state:
    st.session_state.email = None

st.set_page_config(page_title="Resume Ranker", layout="wide")

# ---------- AUTH ----------

def show_auth():
    st.sidebar.title("🔐 Account")
    option = st.sidebar.radio("Login or Sign Up", ["Login", "Sign Up"])
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if option == "Login":
        if st.sidebar.button("🔓 Login"):
            if login(email, password):
                st.session_state.logged_in = True
                st.session_state.email = email
                st.rerun()
            else:
                st.error("Invalid credentials")
    else:
        confirm = st.sidebar.text_input("Confirm Password", type="password")
        if st.sidebar.button("📝 Sign Up"):
            if password != confirm:
                st.error("Passwords do not match")
            elif signup(email, password):
                st.session_state.logged_in = True
                st.session_state.email = email
                st.rerun()
            else:
                st.error("Email already registered")

# ---------- MAIN ----------
if st.session_state.logged_in:
    st.sidebar.title("🧭 Navigation")
    st.sidebar.write(f"👤 {st.session_state.email}")
    if st.sidebar.button("🚪 Log Out"):
        st.session_state.logged_in = False
        st.session_state.email = None
        st.rerun()
        
    if "active_job" in st.session_state:
        st.sidebar.markdown("[📄 Job Description](#job-desc)")
        st.sidebar.markdown("[📤 Upload Resumes](#upload-resumes)")
        st.sidebar.markdown("[📊 Resume Ranking](#ranking)")
        st.sidebar.markdown("[📎 Resume Preview](#preview)")
        st.sidebar.markdown("[📧 Email Notification](#notify)")
       # st.sidebar.markdown("[⚙️ Shortlisting Criteria (#criteria)")
        
    nav = st.sidebar.radio("Go To", ["🏠 Dashboard", "➕ New Job Posting"])

    if nav == "🏠 Dashboard":
        st.title("📄 My Job Postings")
        jobs = get_user_jobs(st.session_state.email)
        if jobs:
            for j_id, title, _ in jobs:
                with st.container():
                    st.markdown(f"#### 📌 {title}")
                    col1, col2, col3 = st.columns([5, 2, 2])
                    with col1:
                        st.markdown("**Manage this job:**")
                        st.button("➡️ Open", key=f"open_{j_id}", on_click=lambda j=j_id: st.session_state.update({"active_job": j}))
                    with col2:
                        st.markdown("**Edit job:**")
                        if st.button("✏️ Edit", key=f"edit_{j_id}"):
                            st.session_state.editing_job = j_id
                            st.rerun()
                    with col3:
                        st.markdown("**Delete job:**")
                        if st.button("🗑️ Delete", key=f"delete_{j_id}"):
                            delete_job(j_id)
                            st.success("Job deleted")
                            st.rerun()
        else:
            st.info("You haven't posted any jobs yet. Start with ➕ New Job Posting.")

    elif nav == "➕ New Job Posting":
        st.title("➕ Post a New Job")
        if "job_desc" not in st.session_state:
            st.session_state.job_desc = ""

        title = st.text_input("Enter Job Title")
        job_file = st.file_uploader("Upload Job Description File", type=["pdf", "txt"])
        if job_file:
            desc = extract_text_from_pdf(job_file) if job_file.type == "application/pdf" else extract_text_from_txt(job_file)
            st.session_state.job_desc = desc

        desc_box = st.text_area("Extracted Job Description", st.session_state.job_desc, height=200)

        if st.button("📤 Post Job"):
            if title and desc_box.strip():
                add_job(st.session_state.email, title, desc_box)
                st.success("✅ Job Posted Successfully")
                st.session_state.job_desc = ""
                st.rerun()
            else:
                st.warning("Please provide both title and description.")

    # ---------- Processing Job Details ----------
    if "active_job" in st.session_state:
        job_id = st.session_state.active_job
        jobs = get_user_jobs(st.session_state.email)
        job_data = next((j for j in jobs if j[0] == job_id), None)

        if job_data:
            st.markdown('<a name="job-desc"></a>', unsafe_allow_html=True)
            st.title(f"🔍 Manage Job: {job_data[1]}")
            with st.expander("📑 Show Job Description"):
                st.markdown(job_data[2])

            st.markdown('<a name="upload-resumes"></a>', unsafe_allow_html=True)
            st.subheader("📤 Upload Resumes")
            resumes = st.file_uploader("Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)

            st.markdown('<a name="shortlisting"></a>', unsafe_allow_html=True)
            st.header("⚙️ Shortlisting Criteria")
            threshold = st.slider("🎯 Score Threshold", 0, 100, 40)
            top_n = st.slider("🏆 Top Candidates", 1, 10, 5)
            
            st.markdown('<a name="ranking"></a>', unsafe_allow_html=True)
            st.subheader("📊 Resume Ranking")
            if resumes:
                st.info("Processing resumes...")
                data = []
                for r in resumes:
                    text = extract_text_from_pdf(r)
                    email = extract_email(text)
                    phone = extract_phone(text)
                    data.append({"File": r, "Name": r.name, "Email": email, "Phone": phone, "Text": text})

                scores = rank_resumes(job_data[2], [d["Text"] for d in data],skill_database)
                for i, d in enumerate(data):
                    d["Score"] = round(scores[i] * 100, 2)

                df = pd.DataFrame(data).sort_values(by="Score", ascending=False).reset_index(drop=True)
                df["Shortlisted"] = df.apply(lambda row: "✅" if row.name < top_n and row["Score"] >= threshold else "❌", axis=1)

                st.success("✅ Ranking complete!")
                st.dataframe(df[["Name", "Email", "Phone", "Score", "Shortlisted"]], use_container_width=True)
                st.download_button("📥 Download CSV", data=df[["Name", "Email", "Phone", "Score", "Shortlisted"]].to_csv(index=False), file_name="shortlisted_resumes.csv")

                st.markdown('<a name="preview"></a>', unsafe_allow_html=True)
                st.subheader("📎 Resume Preview")
                selected_file = st.selectbox("Select a Resume to Preview", df["Name"])
                selected_row = df[df["Name"] == selected_file].iloc[0]
                selected_row["File"].seek(0)
                b64 = base64.b64encode(selected_row["File"].read()).decode("utf-8")
                st.markdown(f"<iframe src='data:application/pdf;base64,{b64}' width='100%' height='600px'></iframe>", unsafe_allow_html=True)

            st.markdown('<a name="notify"></a>', unsafe_allow_html=True)
            st.markdown('<a name="notify"></a>', unsafe_allow_html=True)
            st.subheader("📧 Email Notification")
            st.markdown("Use this section to notify shortlisted and non-shortlisted candidates via email based on their resume scores.")
            if resumes and st.button("📨 Send Emails"):
                for _, row in df.iterrows():
                    recipient = row["Email"]
                    if recipient == "Not Found": continue
                    subject = "Resume Shortlisting Result"
                    body = get_shortlisted_email(row["Name"], row["Score"]) if row["Shortlisted"] == "✅" else get_rejected_email(row["Name"], row["Score"])
                    send_email(recipient, subject, body)
                st.success("✅ Emails sent!")
                st.info("📬 All candidates have been notified based on their resume scores. You can re-send emails anytime if needed.")


else:
    st.markdown("""
        <style>
        .main-auth-bg {
            background-image: url('https://images.unsplash.com/photo-1521790945508-bf2a36314e85');
            background-size: cover;
            background-position: center;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 30px;
            text-align: center;
            padding: 2rem;
            border-radius: 8px;
        }
        </style>
        <div class="main-auth-bg">
            <div>
                <h1 style="font-size: 2.5rem; margin-bottom: 1rem;">🔍 AI-Powered Resume Screening & Ranking System</h1>
                <p style="font-size: 1.2rem; line-height: 1.6; max-width: 800px;">
                    Welcome to an intelligent resume screening platform. Effortlessly upload job descriptions, rank applicant resumes, and notify them instantly. 
                    Enhance your hiring process with automation and precision. Built for recruiters. Powered by AI.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    show_auth()

