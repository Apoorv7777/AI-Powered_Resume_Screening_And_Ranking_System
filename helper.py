from PyPDF2 import PdfReader
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_text_from_pdf(file):
    return "".join([p.extract_text() or "" for p in PdfReader(file).pages])

def extract_text_from_txt(file):
    return file.read().decode('utf-8')

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group(0) if match else "Not Found"

def extract_phone(text):
    match = re.search(r'(\+?\d{1,3})?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}', text)
    return match.group(0) if match else "Not Found"

def extract_skills_from_text(text, skill_database):
    found_skills = []
    for category, skills in skill_database.items():
        for skill in skills:
            if re.search(r"\b" + re.escape(skill) + r"\b", text, re.IGNORECASE):
                found_skills.append(skill)
    return found_skills


def extract_experience_from_text(text):
    # Extracting the number of years of experience
    experience = re.findall(r"\b\d+ ?(?:years?|yrs?)\b", text, re.IGNORECASE)
    return experience



def rank_resumes(job_description, resumes, skill_database):
    # Extract relevant skills and experience from the job description and resumes
    job_skills = " ".join(extract_skills_from_text(job_description, skill_database)) + " " + " ".join(extract_experience_from_text(job_description))
    resumes_skills = [extract_skills_from_text(resume, skill_database) + extract_experience_from_text(resume) for resume in resumes]

    # Convert lists into string format to apply TF-IDF Vectorizer
    documents = [job_skills] + [" ".join(resume) for resume in resumes_skills]
    
    # Vectorize and calculate cosine similarity
    vectors = TfidfVectorizer().fit_transform(documents).toarray()
    return cosine_similarity([vectors[0]], vectors[1:]).flatten()

