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
    
    # Find indices of 'Task', 'E-mail', and 'Recipient' columns
    header = rows[0]
    task_index = None
    email_index = None
    recipient_index = None
    
    for i, cell in enumerate(header):
        if cell == 'Task':
            task_index = i
        elif cell == 'E-mail':
            email_index = i
        elif cell == 'Recipient':
            recipient_index = i
    
    # Check if required columns are found
    if task_index is None or email_index is None or recipient_index is None:
        raise ValueError("Required columns 'Task', 'E-mail', and 'Recipient' not found in the Excel file.")
    
    # Process data rows
    for row in rows[1:]:
        if len(row) > max(task_index, email_index, recipient_index):
            task_description = row[task_index]
            email = row[email_index]
            recipient = row[recipient_index]
            if task_description and email and recipient:
                tasks.append({'description': task_description, 'email': email, 'recipient': recipient})
    
    if add_to_db:
        try:
            for task in tasks:
                db_task = Task(description=task['description'], email=task['email'], recipient=task['recipient'])
                db.session.add(db_task)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error saving tasks to database: {str(e)}")
            return []
    
    return tasks

def analyze_pdf(files):
    if len(files) != 2:
        raise ValueError("Exactly two PDF files are required for comparison.")
    
    texts = []
    for file in files:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        texts.append(text)
    
    prompt = f"""Analyze and compare the following two PDF documents for inconsistencies, logical fallacies, and unsupported statements. Highlight any discrepancies between them:

Document 1:
{texts[0][:4000]}

Document 2:
{texts[1][:4000]}

Provide a detailed analysis of the differences, inconsistencies, and potential issues found between these two documents."""

    analysis = send_openai_request(prompt)
    
    pdf_analysis = PDFAnalysis(filename=f"{files[0].filename}, {files[1].filename}", analysis=analysis)
    db.session.add(pdf_analysis)
    db.session.commit()
    
    return analysis

def generate_email(task, email, recipient):
    prompt = f"""Generate a professional email with the following details:
Task: {task}
Recipient: {recipient}
Recipient's Email: {email}

The email should be formal, clear, and concise. Include a brief introduction, details about the task, and a polite closing."""

    generated_email = send_openai_request(prompt)
    
    task_obj = Task.query.filter_by(description=task, email=email, recipient=recipient).first()
    if task_obj:
        email_obj = GeneratedEmail(task_id=task_obj.id, content=generated_email)
        db.session.add(email_obj)
        db.session.commit()
    else:
        print(f"Task not found for description: {task}, email: {email}, and recipient: {recipient}")
    
    return generated_email
