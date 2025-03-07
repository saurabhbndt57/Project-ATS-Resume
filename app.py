from dotenv import load_dotenv
import streamlit as st
import os
import io
import base64
from PIL import Image
import pdf2image
import google.generativeai as genai
from fpdf import FPDF
import random
import matplotlib.pyplot as plt
import numpy as np

# Load environment variables
load_dotenv()

# Configure Google Gemini API
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("GOOGLE_API_KEY not found. Please set it in your environment variables.")
    st.stop()

genai.configure(api_key=API_KEY)

# Streamlit UI
st.title("🎨 ATS Resume Expert & MCQ Test Generator")
st.subheader("Your AI-powered Resume & Interview Preparation Tool")

input_text = st.text_area("📄 Job Description:")
uploaded_file = st.file_uploader("📤 Upload your resume (PDF)...", type=['pdf'])
if uploaded_file:
    st.success("✅ PDF Uploaded Successfully!")

# Company Selection Dropdown
company = st.selectbox("🏢 Select a company for job preparation:", ["TCS", "Infosys", "Accenture", "Celebal"])

topic = st.selectbox("📌 Select a topic:", ["Core Python", "Machine Learning", "Deep Learning", "Statistics", "SQL", "Data Visualization"])
difficulty = st.selectbox("⚡ Select difficulty level:", ["Easy", "Intermediate", "Hard"])

# Buttons Layout
col1, col2, col3 = st.columns([1, 1, 1])
col4, col5, col6 = st.columns([1, 1, 1])
col7, col8 = st.columns([1, 1])

with col1:
    submit1 = st.button("🔍 Resume Review")
with col2:
    submit3 = st.button("📊 Match Percentage")
with col3:
    submit4 = st.button("🎯 Learning Path")
    study_duration = st.slider("📅 Duration (Months):", 1, 10, 6)
with col4:
    submit5 = st.button("📂 Update Resume")
with col5:
    submit6 = st.button("💬 Interview Qs")
with col6:
    submit7 = st.button("🧠 30 Data Science Qs")
with col7:
    submit8 = st.button("📝 Generate MCQ Test")
with col8:
    submit9 = st.button("📖 Company-Specific Prep")

# Prompts
input_prompt1 = "Review the resume against the job description, highlighting strengths and weaknesses."
input_prompt3 = "Evaluate the resume against the job description with percentage match and missing keywords."
input_prompt4 = f"Create a {study_duration}-month personalized study plan for {company} Data Science role."
input_prompt5 = "Optimize the resume for ATS with relevant skills and keywords."
input_prompt6 = f"Generate 10 {difficulty} interview questions for {topic} for {company}."
input_prompt7 = f"Generate 30 Data Science interview questions for {company}."
input_prompt8 = f"Generate a multiple-choice test with 10 {difficulty} level questions on {topic}, with 5 answer options each and the correct answer marked."
input_prompt9 = f"Generate a question bank for {company} including both Logical Reasoning and Aptitude questions. Provide 10 questions for each category."

def get_gemini_response(input_text, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, prompt])
    return response.text

if submit4:
    response = get_gemini_response(input_text, input_prompt4)
    st.subheader(f"🎯 Learning Path for {company}")
    st.write(response)

if submit6:
    response = get_gemini_response(input_text, input_prompt6)
    st.subheader(f"💬 Interview Questions for {company}")
    st.write(response)

if submit8:
    response = get_gemini_response(input_text, input_prompt8)
    st.subheader("📝 MCQ Test")
    
    questions = response.split("\n\n")
    user_answers = []
    correct_answers = {}
    
    for i, q in enumerate(questions):
        parts = q.split("\n")
        if len(parts) >= 6:
            question_text = parts[0]
            options = parts[1:6]
            correct_option = [opt for opt in options if "(Correct)" in opt]
            
            if correct_option:
                correct_answers[i] = correct_option[0].replace("(Correct)", "").strip()
            
            user_choice = st.radio(question_text, options)
            user_answers.append(user_choice)
    
    if st.button("Submit Test"):
        score = sum(1 for i, ans in enumerate(user_answers) if ans.strip() == correct_answers.get(i, "").strip())
        total_questions = len(correct_answers)
        st.write(f"Your Score: {score}/{total_questions}")
        
        # Simulate performance analysis
        st.subheader("📊 Performance Analysis")
        categories = ["Python", "ML", "DL", "SQL", "Stats", "Viz"]
        scores = np.random.randint(40, 100, size=6)
        avg_score = np.mean(scores)
        rankings = sorted(scores, reverse=True)
        
        fig, ax = plt.subplots()
        ax.barh(categories, scores, color=['blue', 'red', 'green', 'purple', 'orange', 'cyan'])
        ax.set_xlabel("Score (%)")
        ax.set_title("Performance Analysis")
        
        for index, value in enumerate(scores):
            ax.text(value + 2, index, str(value) + "%", va='center')
        
        st.pyplot(fig)
        
        st.write(f"**Your Average Score:** {avg_score:.2f}%")
        if avg_score >= 75:
            st.success("🎯 Excellent! You're well-prepared!")
        elif avg_score >= 50:
            st.warning("⚡ Decent, but work on weaker areas.")
        else:
            st.error("❌ Needs Improvement! Focus on weak areas.")
        
        # Rank Analysis
        st.subheader("🏆 Rank Analysis")
        rank = rankings.index(scores[0]) + 1
        st.write(f"Your rank: {rank} out of {len(rankings)} participants.")

if submit9:
    response = get_gemini_response(input_text, input_prompt9)
    st.subheader(f"📖 Logical & Aptitude Questions for {company}")
    st.write(response)
