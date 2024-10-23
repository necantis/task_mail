import unittest
import os
import tempfile
import pandas as pd
from flask import url_for
from app import app

class TestFileUpload(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.test_uploads_dir = 'uploads'
        os.makedirs(self.test_uploads_dir, exist_ok=True)

    def create_test_excel(self):
        # Create a temporary Excel file
        df = pd.DataFrame({
            'Task': ['Review quarterly report', 'Schedule team meeting'],
            'E-mail': ['test@example.com', 'team@example.com'],
            'Recipient': ['John Doe', 'Team Lead']
        })
        temp_excel = os.path.join(self.test_uploads_dir, 'test_tasks.xlsx')
        df.to_excel(temp_excel, index=False)
        return temp_excel

    def create_test_pdf(self):
        # Create a temporary PDF file with some test content
        from reportlab.pdfgen import canvas
        temp_pdf = os.path.join(self.test_uploads_dir, 'test_document.pdf')
        c = canvas.Canvas(temp_pdf)
        c.drawString(100, 750, "This is a test document.")
        c.drawString(100, 700, "It contains some statements for analysis.")
        c.save()
        return temp_pdf

    def test_excel_upload(self):
        excel_file = self.create_test_excel()
        with open(excel_file, 'rb') as f:
            response = self.client.post(
                '/upload',
                data={'file': (f, 'test_tasks.xlsx')},
                content_type='multipart/form-data'
            )
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['type'], 'excel_processing')
            self.assertIn('generated_emails', data)
            self.assertTrue(len(data['generated_emails']) > 0)

    def test_pdf_upload(self):
        pdf_file = self.create_test_pdf()
        with open(pdf_file, 'rb') as f:
            response = self.client.post(
                '/upload',
                data={'file': (f, 'test_document.pdf')},
                content_type='multipart/form-data'
            )
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['type'], 'pdf_analysis')
            self.assertIn('results', data)
            self.assertTrue(isinstance(data['results'], dict))

    def test_invalid_file(self):
        temp_txt = os.path.join(self.test_uploads_dir, 'test.txt')
        with open(temp_txt, 'w') as f:
            f.write('This is not a valid file')
        
        with open(temp_txt, 'rb') as f:
            response = self.client.post(
                '/upload',
                data={'file': (f, 'test.txt')},
                content_type='multipart/form-data'
            )
            self.assertEqual(response.status_code, 400)

    def tearDown(self):
        # Clean up test files
        for file in os.listdir(self.test_uploads_dir):
            os.remove(os.path.join(self.test_uploads_dir, file))
        os.rmdir(self.test_uploads_dir)

if __name__ == '__main__':
    unittest.main()
