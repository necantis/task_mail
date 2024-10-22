import openpyxl
import PyPDF2
from extensions import db
from models import Task, PDFAnalysis, GeneratedEmail
from chat_request import send_openai_request

def process_excel(file, add_to_db=True):
    workbook = openpyxl.load_workbook(file)
    sheet = workbook.active
    tasks = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if len(row) >= 2 and row[0] and row[1]:  # Ensure we have both task description and email
            task_description, email = row[0], row[1]
            tasks.append({'description': task_description, 'email': email})
    
    if add_to_db:
        try:
            for task in tasks:
                db_task = Task(description=task['description'], email=task['email'])
                db.session.add(db_task)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error saving tasks to database: {str(e)}")
            return []
    
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
    if task_obj:
        email_obj = GeneratedEmail(task_id=task_obj.id, content=generated_email)
        db.session.add(email_obj)
        db.session.commit()
    else:
        print(f"Task not found for description: {task} and email: {email}")
    
    return generated_email
