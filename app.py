from dotenv import load_dotenv
import streamlit as st
import os
import io
import base64
from PIL import Image
import pdf2image
import google.generativeai as genai
from fpdf import FPDF
import requests

# Load environment variables
load_dotenv()

# Configure Google Gemini API
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("GOOGLE_API_KEY not found. Please set it in your environment variables.")
    st.stop()

genai.configure(api_key=API_KEY)

def get_gemini_response(input_text, pdf_content, prompt):
    """Generate a response using Google Gemini API."""
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Handle empty pdf_content
    if isinstance(pdf_content, list) and len(pdf_content) > 0:
        response = model.generate_content([input_text, pdf_content[0], prompt])
    else:
        response = model.generate_content([input_text, prompt])  # Avoid index error
    
    return response.text

def input_pdf_setup(uploaded_file):
    """Convert first page of uploaded PDF to an image and encode as base64."""
    if uploaded_file is not None:
        uploaded_file.seek(0)
        images = pdf2image.convert_from_bytes(uploaded_file.read())
        first_page = images[0]

        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [{
            "mime_type": "image/jpeg",
            "data": base64.b64encode(img_byte_arr).decode()
        }]
        return pdf_parts
    else:
        raise FileNotFoundError("No File Uploaded")

def generate_pdf(updated_resume_text):
    """Generate a downloadable PDF file."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(190, 10, updated_resume_text, align="L")
    pdf_output_path = "updated_resume.pdf"
    pdf.output(pdf_output_path, "F")
    return pdf_output_path

# Streamlit App
st.set_page_config(page_title="A5 ATS Resume Expert")
st.header("MY A5 PERSONAL ATS")

input_text = st.text_area("Job Description:")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=['pdf'])
if uploaded_file:
    st.success("PDF Uploaded Successfully.")

# Dropdowns for topic and difficulty selection
topic = st.selectbox("Select a topic:", ["Core Python", "Machine Learning", "Deep Learning"])
difficulty = st.selectbox("Select difficulty level:", ["Easy", "Intermediate", "Hard"])

# Buttons for different features
submit1 = st.button("Tell Me About the Resume")
submit3 = st.button("Percentage Match")
submit4 = st.button("Personalized Learning Path")
submit5 = st.button("Update Resume & Download")
submit6 = st.button("Generate Interview Questions")
submit7 = st.button("Generate 30 Questions (10 Easy, 10 Intermediate, 10 Hard)")

# Prompts
input_prompt1 = "Review the resume against the job description, highlighting strengths and weaknesses."
input_prompt3 = "Evaluate the resume against the job description with percentage match and missing keywords."
input_prompt4 = "Create a 6-month personalized study plan based on the job description."
input_prompt5 = "Optimize the resume for ATS with relevant skills and keywords."
input_prompt6 = f"Generate 10 {difficulty} interview questions for {topic} based on the job description."
input_prompt7 = "Generate 30 interview questions (10 Easy, 10 Intermediate, 10 Hard)."

if submit1 and uploaded_file:
    pdf_content = input_pdf_setup(uploaded_file)
    response = get_gemini_response(input_text, pdf_content, input_prompt1)
    st.subheader("Response:")
    st.write(response)
elif submit3 and uploaded_file:
    pdf_content = input_pdf_setup(uploaded_file)
    response = get_gemini_response(input_text, pdf_content, input_prompt3)
    st.subheader("Response:")
    st.write(response)
elif submit4 and uploaded_file:
    pdf_content = input_pdf_setup(uploaded_file)
    response = get_gemini_response(input_text, pdf_content, input_prompt4)
    st.subheader("Response:")
    st.write(response)
elif submit5 and uploaded_file:
    pdf_content = input_pdf_setup(uploaded_file)
    response = get_gemini_response(input_text, pdf_content, input_prompt5)
    pdf_path = generate_pdf(response)
    with open(pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()
        b64_pdf = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="Updated_Resume.pdf">Download Updated Resume</a>'
        st.markdown(href, unsafe_allow_html=True)
elif submit6:
    response = get_gemini_response(input_text, [], input_prompt6)
    st.subheader("Generated Interview Questions:")
    st.write(response)
elif submit7:
    response = get_gemini_response(input_text, [], input_prompt7)
    st.subheader("Generated 30 Interview Questions (10 Easy, 10 Intermediate, 10 Hard):")
    st.write(response)
