import sqlite3

def init_job_db():
    conn = sqlite3.connect("app.db")
    with open("schema.sql") as f:
        conn.executescript(f.read())
    conn.close()

def add_job(email, title, desc):
    conn = sqlite3.connect("app.db")
    conn.execute("INSERT INTO jobs (user_email, title, description) VALUES (?, ?, ?)", (email, title, desc))
    conn.commit()
    conn.close()

def get_user_jobs(email):
    conn = sqlite3.connect("app.db")
    jobs = conn.execute("SELECT id, title, description FROM jobs WHERE user_email=?", (email,)).fetchall()
    conn.close()
    return jobs

def delete_job(job_id):
    conn = sqlite3.connect("app.db")
    conn.execute("DELETE FROM resumes WHERE job_id=?", (job_id,))
    conn.execute("DELETE FROM jobs WHERE id=?", (job_id,))
    conn.commit()
    conn.close()

def edit_job(job_id, new_title, new_desc):
    conn = sqlite3.connect("app.db")
    conn.execute("UPDATE jobs SET title=?, description=? WHERE id=?", (new_title, new_desc, job_id))
    conn.commit()
    conn.close()

def save_resume(job_id, filename, email, phone, score, shortlisted, content):
    conn = sqlite3.connect("app.db")
    conn.execute("""
        INSERT INTO resumes (job_id, filename, email, phone, score, shortlisted, content)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (job_id, filename, email, phone, score, shortlisted, content)
    )
    conn.commit()
    conn.close()

def get_resumes_for_job(job_id):
    conn = sqlite3.connect("app.db")
    data = conn.execute("SELECT filename, email, phone, score, shortlisted FROM resumes WHERE job_id=?", (job_id,)).fetchall()
    conn.close()
    return data

