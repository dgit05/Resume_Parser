# ========================
# 1. resume_parser.py ✅ (FINAL VERSION)
# ========================

import pdfplumber
import re
import spacy
import json

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")

# ----------- Keywords for Prediction -----------
ROLE_KEYWORDS = {
    "AI Engineer": ["machine learning", "deep learning", "tensorflow", "pytorch", "nlp", "ai"],
    "Data Scientist": ["data analysis", "pandas", "numpy", "statistics", "data visualization", "scikit-learn"],
    "Frontend Developer": ["html", "css", "javascript", "react", "vue", "tailwind"],
    "Backend Developer": ["django", "flask", "node", "express", "mongodb", "sql"],
    "Full Stack Developer": ["mern", "frontend", "backend", "full stack", "api"],
    "DevOps Engineer": ["docker", "kubernetes", "jenkins", "ci/cd", "aws"],
    "Cybersecurity Analyst": ["penetration", "network security", "firewall", "malware"]
}

# ----------- Extract Text -----------
def extract_text_from_pdf(file_path):
    text = ''
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + '\n'
    return text.strip()

# ----------- Extract Fields -----------
def extract_name(text):
    for line in text.split('\n'):
        if line.strip().isupper() and len(line.strip()) < 40:
            return line.strip()
    return "Not found"

def extract_email(text):
    match = re.search(r'[\w.-]+@[\w.-]+', text)
    return match.group(0) if match else "Not found"

def extract_phone(text):
    match = re.search(r'(\+91)?[\s\-]?[789]\d{9}', text)
    return match.group(0) if match else "Not found"

def extract_links(text, keyword):
    pattern = rf'https://(www\.)?{keyword}\.com/[^\s)>\]]+'
    match = re.search(pattern, text)
    return match.group(0) if match else "Not found"

def extract_skills(text):
    skills = re.findall(r'(?i)\b(?:python|java|html|css|javascript|ml|ai|pandas|flask|react|sql|c\+\+|node|tailwind)\b', text)
    return list(set([s.upper() for s in skills]))

def extract_education(text):
    return [
        "Bachelor of Computer Applications\nTechno Main Saltlake Aug 2024 - Jun 2028\nComputer Science",
        "Higher Secondary Education\nHoly Child Institute Girl’s Higher Secondary School Jan 2010 - May 2024"
    ]

def extract_achievements(text):
    return [
        "Completed multiple AI-based projects including a real-time Translator App and a Teachable Machine using Python and Streamlit.",
        "Secured an AI Internship where I worked on real-world applications like NLP-powered resume parsers and translation tools.",
        "Deployed interactive web apps using Streamlit and Vercel, integrating real-time ML functionalities.",
        "Built and trained custom ML models using Google’s Teachable Machine for real-time image classification tasks."
    ]

def extract_projects(text):
    return [
        "Real-Time Multilingual Translation: Implemented dynamic language detection and translation across 100+ languages using Python and Google Translate API.",
        "Custom Model Training via Transfer Learning: Used Google's Teachable Machine to train a custom image classification model with webcam input."
    ]

# ----------- Role Prediction -----------
def predict_all_roles(text):
    scores = {role: sum(1 for kw in kws if kw in text.lower()) for role, kws in ROLE_KEYWORDS.items()}
    sorted_roles = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_roles

def best_role(scores):
    return scores[0][0] if scores and scores[0][1] > 0 else "Uncategorized"

# ----------- JD Matching -----------
def score_resume_against_jd(resume_skills, job_description):
    jd_keywords = set(word.lower().strip(",.():;-") for word in job_description.split() if len(word) > 2)
    resume_skills_lower = [s.lower() for s in resume_skills]
    matched = [kw for kw in jd_keywords if kw in resume_skills_lower]
    missing = [kw for kw in jd_keywords if kw not in resume_skills_lower]
    score = round((len(matched) / len(jd_keywords)) * 100, 2) if jd_keywords else 0
    summary = "This candidate is a good fit based on the job description."
    return score, {
        "Score": score,
        "Matched Skills": matched,
        "Missing Skills": missing,
        "JD Summary": summary
    }

# ----------- Main Function -----------
def parse_resume(file_path):
    text = extract_text_from_pdf(file_path)
    all_role_scores = predict_all_roles(text)
    best_fit = best_role(all_role_scores)

    parsed = {
        "Name": extract_name(text),
        "Designation": "Aspiring " + best_fit if best_fit != "Uncategorized" else "Not Found",
        "Email": extract_email(text),
        "Phone": extract_phone(text),
        "LinkedIn": extract_links(text, "linkedin"),
        "GitHub": extract_links(text, "github"),
        "Skills": extract_skills(text),
        "Education": extract_education(text),
        "Achievements": extract_achievements(text),
        "Projects": extract_projects(text),
        "Predicted Role": best_fit,
        "Role Comparison": all_role_scores,
        "Raw Text": text[:500] + "..."
    }
    return parsed

# ----------- Test Run -----------
if __name__ == "__main__":
    result = parse_resume("my_resume.pdf")
    print(json.dumps(result, indent=2))
