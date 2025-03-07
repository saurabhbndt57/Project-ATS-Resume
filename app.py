from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
import PyPDF2
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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

st.title("🎨 ATS Resume Expert & MCQ Test Generator")
st.subheader("Your AI-powered Resume & Interview Preparation Tool")

# Job description input
input_text = st.text_area("📄 Job Description:")

# Resume upload
uploaded_file = st.file_uploader("📤 Upload your resume (PDF)...", type=['pdf'])

# Company and topic selection
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
    "company_prep": f"Generate a question bank for {company} including both Logical Reasoning and Aptitude questions. Provide 10 questions for each category."
}

# Buttons Grid Layout
buttons = list(input_prompts.keys())
cols = st.columns(4)
responses = {}

for idx, key in enumerate(buttons):
    with cols[idx % 4]:
        if st.button(f"{key.replace('_', ' ').title()}"):
            if key == "update_resume" and uploaded_file:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                resume_text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
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
            else:
                responses[key] = get_gemini_response(input_text, input_prompts[key])

# Display responses in a structured layout
for key, response in responses.items():
    st.markdown("---")
    st.subheader(f"📌 {key.replace('_', ' ').title()}")
    st.write(response)

st.markdown("---")
st.markdown("<h3 style='text-align: center;'>🛠 DSA for Data Science</h3>", unsafe_allow_html=True)

# DSA Questions Section
level = st.selectbox("📚 Select Difficulty Level:", ["Easy", "Intermediate", "Advanced"])
if st.button(f"📝 Generate {level} DSA Questions"):
    response = get_gemini_response("", f"Generate 10 DSA questions and answers for {level} level.")
    st.write(response)

topic = st.selectbox("🗂 Select DSA Topic:", ["Arrays", "Linked Lists", "Trees", "Graphs", "Dynamic Programming", "Recursion", "Big O notation", "Sorting", "Searching"])
if st.button(f"📖 Teach me {topic} with Case Studies"):
    explanation = get_gemini_response("", f"Explain {topic} with examples and Python code.")
    case_study = get_gemini_response("", f"Provide a real-world case study on {topic} for data science.")
    st.write(explanation)
    st.write(case_study)