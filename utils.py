import openpyxl
import PyPDF2
from extensions import db
from models import Task, PDFAnalysis, GeneratedEmail
from chat_request import send_openai_request

def process_excel(file, add_to_db=True):
    workbook = openpyxl.load_workbook(file)
    sheet = workbook.active
    tasks = []
    
    # Get all rows including the header
    rows = list(sheet.iter_rows(min_row=1, values_only=True))
    
    if not rows:
        return []
    
    # Find indices of 'Task' and 'E-mail' columns
    header = rows[0]
    task_index = None
    email_index = None
    
    for i, cell in enumerate(header):
        if cell == 'Task':
            task_index = i
        elif cell == 'E-mail':
            email_index = i
    
    # Check if required columns are found
    if task_index is None or email_index is None:
        raise ValueError("Required columns 'Task' and 'E-mail' not found in the Excel file.")
    
    # Process data rows
    for row in rows[1:]:
        if len(row) > max(task_index, email_index):
            task_description = row[task_index]
            email = row[email_index]
            if task_description and email:
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
