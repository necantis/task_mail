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
            taskList.innerHTML = '';
            data.tasks.forEach(task => {
                const li = document.createElement('li');
                li.className = 'list-group-item';
                li.textContent = `${task.description} (${task.email})`;
                li.addEventListener('click', () => {
                    emailGenerator.querySelector('input[name="task"]').value = task.description;
                    emailGenerator.querySelector('input[name="email"]').value = task.email;
                });
                taskList.appendChild(li);
            });
        })
        .catch(error => console.error('Error:', error));
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
            analysisResult.textContent = data.analysis;
        })
        .catch(error => console.error('Error:', error));
    });

    emailGenerator.addEventListener('submit', function(e) {
        e.preventDefault();
        const task = emailGenerator.querySelector('input[name="task"]').value;
        const email = emailGenerator.querySelector('input[name="email"]').value;
        fetch('/generate_email', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ task, email }),
        })
        .then(response => response.json())
        .then(data => {
            generatedEmail.textContent = data.email;
        })
        .catch(error => console.error('Error:', error));
    });
});
