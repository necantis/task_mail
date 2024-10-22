import io
from app import create_app
from utils import process_excel
from openpyxl import Workbook

def create_test_excel():
    wb = Workbook()
    ws = wb.active
    ws.append(["Task Description", "Email"])
    ws.append(["Complete project report", "john@example.com"])
    ws.append(["Prepare presentation", "jane@example.com"])
    excel_file = io.BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)
    return excel_file

app = create_app()
with app.app_context():
    test_file = create_test_excel()
    tasks = process_excel(test_file)
    print(f"Processed tasks: {tasks}")
    if tasks:
        print("Excel file processed successfully.")
    else:
        print("Failed to process Excel file.")
