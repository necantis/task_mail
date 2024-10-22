document.addEventListener('DOMContentLoaded', function() {
    const excelForm = document.getElementById('excel-form');
    const pdfForm = document.getElementById('pdf-form');
    const taskList = document.getElementById('task-list');
    const analysisResult = document.getElementById('analysis-result');
    const emailGenerator = document.getElementById('email-generator');
    const generatedEmail = document.getElementById('generated-email');

    excelForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(excelForm);
        fetch('/upload_excel', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                taskList.innerHTML = `<li class="list-group-item list-group-item-danger">${data.error}</li>`;
            } else {
                taskList.innerHTML = '';
                data.tasks.forEach(task => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item';
                    li.textContent = `${task.description} (Email: ${task.email}, Recipient: ${task.recipient})`;
                    li.addEventListener('click', () => {
                        emailGenerator.querySelector('input[name="task"]').value = task.description;
                        emailGenerator.querySelector('input[name="email"]').value = task.email;
                        emailGenerator.querySelector('input[name="recipient"]').value = task.recipient;
                    });
                    taskList.appendChild(li);
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            taskList.innerHTML = `<li class="list-group-item list-group-item-danger">An error occurred while processing the Excel file.</li>`;
        });
    });

    pdfForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(pdfForm);
        fetch('/upload_pdf', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                analysisResult.textContent = data.error;
            } else {
                analysisResult.textContent = data.analysis;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            analysisResult.textContent = 'An error occurred while analyzing the PDFs.';
        });
    });

    emailGenerator.addEventListener('submit', function(e) {
        e.preventDefault();
        const task = emailGenerator.querySelector('input[name="task"]').value;
        const email = emailGenerator.querySelector('input[name="email"]').value;
        const recipient = emailGenerator.querySelector('input[name="recipient"]').value;
        fetch('/generate_email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ task, email, recipient }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                generatedEmail.textContent = data.error;
            } else {
                generatedEmail.textContent = data.email;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            generatedEmail.textContent = 'An error occurred while generating the email.';
        });
    });
});
