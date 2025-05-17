# auth.py

import sqlite3
import hashlib
import streamlit as st

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_user_db():
    conn = sqlite3.connect("app.db")
    conn.execute("CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT)")
    conn.commit()
    conn.close()

def signup(email, password):
    conn = sqlite3.connect("app.db")
    if conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone():
        return False
    conn.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hash_password(password)))
    conn.commit()
    conn.close()
    return True

def login(email, password):
    conn = sqlite3.connect("app.db")
    user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", 
                        (email, hash_password(password))).fetchone()
    conn.close()
    return user is not None

def user_session(email):
    """
    Stores the login session in Streamlit's session_state.
    """
    st.session_state["user"] = email

