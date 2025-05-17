def get_shortlisted_email(name, score):
    return f"""Hi {name},

Congratulations! 🎉

You have been shortlisted for the role!

Your score: {score}%

We will contact you with further steps.

Regards,  
Resume Screening And Ranking System Team
"""

def get_rejected_email(name, score):
    return f"""Hi {name},

Thank you for applying. Unfortunately, your resume was not shortlisted.

Your score: {score}%

We wish you the best!

Regards,  
Resume Screening And Ranking System Team
"""

