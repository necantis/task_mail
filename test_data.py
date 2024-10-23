import os
import pandas as pd
from reportlab.pdfgen import canvas

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Create test Excel file
def create_test_excel():
    df = pd.DataFrame({
        'Task': [
            'Review Q3 financial report',
            'Schedule team planning meeting',
            'Update project documentation'
        ],
        'E-mail': [
            'finance@example.com',
            'team@example.com',
            'docs@example.com'
        ],
        'Recipient': [
            'Finance Team',
            'Project Team',
            'Documentation Team'
        ]
    })
    excel_path = os.path.join(UPLOAD_FOLDER, 'test_tasks.xlsx')
    df.to_excel(excel_path, index=False)
    return excel_path

# Create test PDF file
def create_test_pdf():
    pdf_path = os.path.join(UPLOAD_FOLDER, 'test_document.pdf')
    c = canvas.Canvas(pdf_path)
    
    # Add some test content with potential inconsistencies
    text_content = [
        "Project Analysis Report",
        "The project will definitely succeed because everyone likes it.",
        "Our competitors are all terrible at what they do.",
        "Studies show that 60% of the time, it works every time.",
        "We should proceed with the plan because that's what we've always done.",
    ]
    
    y_position = 800
    for line in text_content:
        c.drawString(50, y_position, line)
        y_position -= 50
        
    c.save()
    return pdf_path

if __name__ == "__main__":
    # Create test files
    excel_file = create_test_excel()
    pdf_file = create_test_pdf()
    print(f"Created test Excel file: {excel_file}")
    print(f"Created test PDF file: {pdf_file}")
