from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
import PyPDF2
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import logging

# Load environment variables
load_dotenv()

# Configure Google Gemini API
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("GOOGLE_API_KEY not found. Please set it in your environment variables.")
    st.stop()

genai.configure(api_key=API_KEY)

@st.cache_data
def get_gemini_response(input_text, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    try:
        response = model.generate_content([input_text, prompt])
        return response.text
    except Exception as e:
        return f"Error fetching response: {e}"

# App layout
st.set_page_config(page_title="ATS Resume Expert & MCQ Generator", layout="wide")
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stTextArea, .stFileUploader, .stSelectbox, .stSlider, .stButton {
        margin-bottom: 1rem;
    }
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }
    .stDownloadButton > button {
        background-color: #2196F3;
        color: white;
        font-weight: bold;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1 style='text-align: center; color: #333;'>🎨 ATS Resume Expert & MCQ Test Generator</h1>
    <p style='text-align: center; font-size: 18px;'>Your AI-powered Resume & Interview Preparation Tool</p>
""", unsafe_allow_html=True)

# Layout for inputs
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        input_text = st.text_area("📄 Job Description:")
        uploaded_file = st.file_uploader("📤 Upload your resume (PDF)...", type=['pdf'])

    with col2:
        company = st.selectbox("🏢 Select a company:", ["TCS", "Infosys", "Accenture", "Celebal"])
        topic = st.selectbox("📌 Select a topic:", ["Core Python", "Machine Learning", "Deep Learning", "Statistics", "SQL", "Data Visualization"])
        difficulty = st.selectbox("⚡ Select difficulty level:", ["Easy", "Intermediate", "Hard"])
        study_duration = st.slider("📅 Duration (Months):", 1, 10, 6)

# Prompt templates
input_prompts = {
    "resume_review": "Review the resume against the job description, highlighting strengths and weaknesses.",
    "match_percentage": "Evaluate the resume against the job description with percentage match and missing keywords.",
    "learning_path": f"Create a {study_duration}-month personalized study plan for {company} Data Science role.",
    "update_resume": "Optimize the resume for ATS with relevant skills and keywords. Return the updated resume text.",
    "interview_qs": f"Generate 10 {difficulty} interview questions for {topic} for {company}.",
    "data_science_qs": f"Generate 30 Data Science interview questions for {company}.",
    "mcq_test": f"Generate a multiple-choice test with 10 {difficulty} level questions on {topic}, with 5 answer options each and the correct answer marked.",
    "company_prep": f"Generate a question bank for {company} including both Logical Reasoning and Aptitude questions. Provide 10 questions for each category.",
    "group_discussion": f"Generate an AI-guided structured group discussion on {topic}, including key discussion points, challenges, and role-based perspectives."
}

# Extract resume text early if uploaded
resume_text = ""
if uploaded_file:
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        resume_text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
    except Exception as e:
        st.error(f"Error reading PDF: {e}")

# Buttons Grid Layout
st.markdown("<h3 style='margin-top: 30px;'>🚀 Choose Your Action</h3>", unsafe_allow_html=True)
buttons = list(input_prompts.keys())
cols = st.columns(4)
responses = {}

for idx, key in enumerate(buttons):
    with cols[idx % 4]:
        if st.button(f"{key.replace('_', ' ').title()}"):
            if key in ["resume_review", "match_percentage"]:
                if not resume_text or not input_text:
                    responses[key] = "Please upload a resume and provide the job description."
                else:
                    combined_text = f"Job Description:\n{input_text}\n\nResume:\n{resume_text}"
                    responses[key] = get_gemini_response(combined_text, input_prompts[key])

            elif key == "update_resume" and uploaded_file:
                response = get_gemini_response(resume_text, input_prompts[key])
                pdf_buffer = BytesIO()
                pdf_canvas = canvas.Canvas(pdf_buffer, pagesize=letter)
                pdf_canvas.setFont("Helvetica", 12)
                y_position = 750
                for line in response.split("\n"):
                    pdf_canvas.drawString(50, y_position, line)
                    y_position -= 20
                    if y_position < 50:
                        pdf_canvas.showPage()
                        y_position = 750
                pdf_canvas.save()
                pdf_buffer.seek(0)
                st.subheader("📂 Updated Resume Recommendations")
                st.write(response)
                st.download_button("📥 Download Updated Resume", pdf_buffer, "Updated_Resume.pdf", "application/pdf")

            elif key not in ["update_resume", "resume_review", "match_percentage"]:
                responses[key] = get_gemini_response(input_text, input_prompts[key])

# Display responses in a structured layout
for key, response in responses.items():
    st.markdown("---")
    st.subheader(f"📌 {key.replace('_', ' ').title()}")
    st.write(response)

# DSA Section
st.markdown("---")
st.markdown("<h3 style='text-align: center;'>🛠 DSA for Data Science</h3>", unsafe_allow_html=True)

col_dsa1, col_dsa2 = st.columns(2)

with col_dsa1:
    level = st.selectbox("📚 Select Difficulty Level:", ["Easy", "Intermediate", "Advanced"])
    if st.button(f"📝 Generate {level} DSA Questions"):
        response = get_gemini_response("", f"Generate 10 DSA questions and answers for {level} level.")
        st.write(response)

with col_dsa2:
    topic = st.selectbox("🗂 Select DSA Topic:", ["Arrays", "Linked Lists", "Trees", "Graphs", "Dynamic Programming", "Recursion", "Big O notation", "Sorting", "Searching"])
    if st.button(f"📖 Teach me {topic} with Case Studies"):
        explanation = get_gemini_response("", f"Explain {topic} with examples and Python code.")
        case_study = get_gemini_response("", f"Provide a real-world case study on {topic} for data science.")
        st.write(explanation)
        st.write(case_study)

# Python Code Debugger Section
# --- Python Code Debugger Section ---
st.markdown("---")
st.markdown("<h3 style='text-align: center;'>🐞 Python Code Debugger</h3>", unsafe_allow_html=True)

# Text area for code input
user_code = st.text_area("🧾 Enter or paste your Python code here:", height=200)

# Optional filename input
filename = st.text_input("📄 Give your code a name (optional):", value="my_script.py")

# Button to check and fix code
if st.button("🔍 Check & Fix Code"):
    if not user_code.strip():
        st.warning("⚠️ Please enter some Python code to check.")
    else:
        with st.spinner("Analyzing and fixing code..."):
            prompt = f"""
            Analyze the following Python code for bugs, syntax errors, and logic errors.
            If it has issues, correct them. Return the fixed code and briefly explain the changes made.

            Code:
            ```python
            {user_code}
            ```
            """
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content([prompt])
                if response:
                    response_text = response.text
                    st.subheader("✅ Corrected Code")
                    st.code(response_text, language="python")
                else:
                    st.error("❌ No response from Gemini.")
            except Exception as e:
                st.error(f"Error: {e}")
