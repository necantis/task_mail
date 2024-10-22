import openpyxl
import PyPDF2
from extensions import db
from models import Task, PDFAnalysis, GeneratedEmail
from chat_request import send_openai_request

def process_excel(file):
    workbook = openpyxl.load_workbook(file)
    sheet = workbook.active
    tasks = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        task_description, email = row
        task = Task(description=task_description, email=email)
        db.session.add(task)
        tasks.append({'description': task_description, 'email': email})
    db.session.commit()
    return tasks

def analyze_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    prompt = f"Analyze the following text for inconsistencies, logical fallacies, and unsupported statements:\n\n{text[:4000]}"
    analysis = send_openai_request(prompt)
    
    pdf_analysis = PDFAnalysis(filename=file.filename, analysis=analysis)
    db.session.add(pdf_analysis)
    db.session.commit()
    
    return analysis

def generate_email(task, email):
    prompt = f"Generate a professional email about the following task: {task}. The email should be sent to: {email}"
    generated_email = send_openai_request(prompt)
    
    task_obj = Task.query.filter_by(description=task, email=email).first()
    email_obj = GeneratedEmail(task_id=task_obj.id, content=generated_email)
    db.session.add(email_obj)
    db.session.commit()
    
    return generated_email
