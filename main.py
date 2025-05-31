from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import spacy
import pandas as pd
import json
from typing import List, Dict
from models import db, Resume
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import re

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

app = FastAPI()
flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = os.urandom(24)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resumes.db'
flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(flask_app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(flask_app)
login_manager.login_view = 'admin.login'

# Create admin user
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin@123'

# Create a simple User class for admin
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Initialize database
with flask_app.app_context():
    db.create_all()
    # Check if admin user exists, if not create it
    admin = User.query.filter_by(username=ADMIN_USERNAME).first()
    if not admin:
        admin = User(id=1)
        admin.password_hash = generate_password_hash(ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()

# FastAPI routes remain the same
@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    try:
        # Read PDF content
        pdf_reader = PyPDF2.PdfReader(file.file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        if not text.strip():
            raise ValueError("PDF file appears to be empty or not readable")

        # Process text with spaCy
        doc = nlp(text)
        
        # Extract entities
        entities = {
            "name": "",
            "email": "",
            "phone": "",
            "skills": [],
            "experience": []
        }

        # Extract name (assuming it's usually at the top)
        entities["name"] = text.split("\n")[0].strip()

        # Extract email and phone using regex
        emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
        if emails:
            entities["email"] = emails[0]

        phones = re.findall(r'\+?[1-9]\d{1,14}', text)
        if phones:
            entities["phone"] = phones[0]

        # Enhanced skill and experience extraction
        extract_skills_and_experience(text, doc, entities)

        # Save to database
        resume = Resume(
            name=entities["name"],
            email=entities["email"],
            phone=entities["phone"],
            skills=entities["skills"],  
            education=entities["education"],
            projects=entities["projects"],
            certifications=entities["certifications"],
            uploaded_at=datetime.now(),  
            resume_path=file.filename
        )
        db.session.add(resume)
        db.session.commit()

        # Debug logging - print final entities
        print("\nFinal Entities:")
        print("Education:", entities["education"])
        print("Projects:", entities["projects"])
        print("Certifications:", entities["certifications"])

        # Debug logging
        print("\nExtracted Data:")
        print("Name:", entities["name"])
        print("Email:", entities["email"])
        print("Phone:", entities["phone"])
        print("Skills:", entities["skills"])
        print("Experience:", entities["experience"])
        print("\n")

        # Return response
        return {
            "status": "success",
            "data": {
                "name": entities["name"],
                "email": entities["email"],
                "phone": entities["phone"],
                "skills": entities["skills"],
                "education": entities["education"],
                "projects": entities["projects"],
                "certifications": entities["certifications"]
            }
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "status": "error",
            "message": str(e)
        }

def extract_skills_and_experience(text, doc, entities):
    # Extract skills using pattern matching, NER, and context analysis
    for token in doc:
        # Check for NER entities that might be skills
        if token.ent_type_ in ["PRODUCT", "ORG", "TECH"]:
            skill = token.text.lower()
            if skill not in entities["skills"]:
                entities["skills"].append(skill)
        
    # Post-processing to clean up skills
    cleaned_skills = []
    for skill in entities["skills"]:
        # Clean up common variations
        skill = skill.strip().lower()
        if skill not in cleaned_skills:
            # Add variations of the same skill
            if skill in ["c++", "cpp"]:
                if "c++" not in cleaned_skills:
                    cleaned_skills.append("c++")
            elif skill in ["c#", "csharp"]:
                if "c#" not in cleaned_skills:
                    cleaned_skills.append("c#")
            elif skill in ["node.js", "nodejs"]:
                if "node.js" not in cleaned_skills:
                    cleaned_skills.append("node.js")
            else:
                cleaned_skills.append(skill)

    entities["skills"] = cleaned_skills

    # Post-processing to clean up skills
    cleaned_skills = []
    for skill in entities["skills"]:
        # Clean up common variations
        skill = skill.strip().lower()
        if skill not in cleaned_skills:
            # Add variations of the same skill
            if skill in ["c++", "cpp"]:
                if "c++" not in cleaned_skills:
                    cleaned_skills.append("c++")
            elif skill in ["c#", "csharp"]:
                if "c#" not in cleaned_skills:
                    cleaned_skills.append("c#")
            elif skill in ["node.js", "nodejs"]:
                if "node.js" not in cleaned_skills:
                    cleaned_skills.append("node.js")
            else:
                cleaned_skills.append(skill)

    entities["skills"] = cleaned_skills

    # Post-processing to clean up skills
    cleaned_skills = []
    for skill in entities["skills"]:
        # Clean up common variations
        skill = skill.strip().lower()
        if skill not in cleaned_skills:
            # Add variations of the same skill
            if skill in ["c++", "cpp"]:
                if "c++" not in cleaned_skills:
                    cleaned_skills.append("c++")
            elif skill in ["c#", "csharp"]:
                if "c#" not in cleaned_skills:
                    cleaned_skills.append("c#")
            elif skill in ["node.js", "nodejs"]:
                if "node.js" not in cleaned_skills:
                    cleaned_skills.append("node.js")
            else:
                cleaned_skills.append(skill)

    entities["skills"] = cleaned_skills

    # Post-processing to clean up skills
    cleaned_skills = []
    for skill in entities["skills"]:
        # Clean up common variations
        skill = skill.strip().lower()
        if skill not in cleaned_skills:
            # Add variations of the same skill
            if skill in ["c++", "cpp"]:
                if "c++" not in cleaned_skills:
                    cleaned_skills.append("c++")
            elif skill in ["c#", "csharp"]:
                if "c#" not in cleaned_skills:
                    cleaned_skills.append("c#")
            elif skill in ["node.js", "nodejs"]:
                if "node.js" not in cleaned_skills:
                    cleaned_skills.append("node.js")
            else:
                cleaned_skills.append(skill)

    entities["skills"] = cleaned_skills

    # Post-processing to clean up skills
    cleaned_skills = []
    for skill in entities["skills"]:
        # Clean up common variations
        skill = skill.strip().lower()
        if skill not in cleaned_skills:
            # Add variations of the same skill
            if skill in ["c++", "cpp"]:
                if "c++" not in cleaned_skills:
                    cleaned_skills.append("c++")
            elif skill in ["c#", "csharp"]:
                if "c#" not in cleaned_skills:
                    cleaned_skills.append("c#")
            elif skill in ["node.js", "nodejs"]:
                if "node.js" not in cleaned_skills:
                    cleaned_skills.append("node.js")
            else:
                cleaned_skills.append(skill)

    entities["skills"] = cleaned_skills

    # Post-processing to clean up skills
    cleaned_skills = []
    for skill in entities["skills"]:
        # Clean up common variations
        skill = skill.strip().lower()
        if skill not in cleaned_skills:
            # Add variations of the same skill
            if skill in ["c++", "cpp"]:
                if "c++" not in cleaned_skills:
                    cleaned_skills.append("c++")
            elif skill in ["c#", "csharp"]:
                if "c#" not in cleaned_skills:
                    cleaned_skills.append("c#")
            elif skill in ["node.js", "nodejs"]:
                if "node.js" not in cleaned_skills:
                    cleaned_skills.append("node.js")
            else:
                cleaned_skills.append(skill)

    entities["skills"] = cleaned_skills

def extract_skills_from_text(text):
    """Extract skills from a given text using both pattern matching and NER"""
    skills = []
    doc = nlp(text)
    for token in doc:
        if token.text.lower() in skill_patterns or token.ent_type_ == "PRODUCT":
            skill = token.text.lower()
            if skill not in skills:
                skills.append(skill)
    return skills

# Flask routes for admin interface
@flask_app.route('/admin/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username == ADMIN_USERNAME and check_password_hash(User.query.get(1).password_hash, password):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

@flask_app.route('/admin/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({"success": True})

@flask_app.route('/admin/resumes', methods=['GET'])
def get_resumes():
    resumes = Resume.query.order_by(Resume.uploaded_at.desc()).all()
    return jsonify([{
        'id': resume.id,
        'name': resume.name,
        'email': resume.email,
        'phone': resume.phone,
        'skills': resume.skills,
        'experience': resume.experience,
        'uploaded_at': resume.uploaded_at.isoformat()
    } for resume in resumes])

@flask_app.route('/admin/dashboard')
@login_required
def dashboard():
    resumes = Resume.query.order_by(Resume.uploaded_at.desc()).all()
    return render_template('dashboard.html', resumes=resumes)

@flask_app.route('/admin/logout')
def logout():
    logout_user()
    return redirect(url_for('admin.login'))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
