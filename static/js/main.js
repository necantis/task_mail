document.addEventListener('DOMContentLoaded', function() {
    // Get all the required elements
    const elements = {
        taskForm: document.getElementById('task-form'),
        documentForm: document.getElementById('document-form'),
        taskList: document.getElementById('task-list'),
        analysisResult: document.getElementById('analysis-result'),
        emailGenerator: document.getElementById('email-generator'),
        generatedEmail: document.getElementById('generated-email'),
        fileType: document.getElementById('fileType'),
        fileUploadSection: document.getElementById('fileUploadSection'),
        gsheetSection: document.getElementById('gsheetSection'),
        fileInput: document.getElementById('file')
    };

    // File type change handler
    if (elements.fileType) {
        elements.fileType.addEventListener('change', function() {
            if (this.value === 'gsheet') {
                elements.fileUploadSection?.classList.add('d-none');
                elements.gsheetSection?.classList.remove('d-none');
                elements.fileInput?.removeAttribute('required');
            } else {
                elements.fileUploadSection?.classList.remove('d-none');
                elements.gsheetSection?.classList.add('d-none');
                elements.fileInput?.setAttribute('required', 'required');
                
                if (elements.fileInput) {
                    // Update accepted file types
                    if (this.value === 'excel') {
                        elements.fileInput.setAttribute('accept', '.xlsx');
                    } else if (this.value === 'word') {
                        elements.fileInput.setAttribute('accept', '.docx');
                    }
                }
            }
        });
    }

    // Task form submit handler
    if (elements.taskForm && elements.taskList) {
        elements.taskForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(elements.taskForm);
            const fileType = formData.get('fileType');
            let endpoint = '/upload_';

            if (fileType === 'excel') {
                endpoint += 'excel';
            } else if (fileType === 'word') {
                endpoint += 'word';
            } else if (fileType === 'gsheet') {
                endpoint += 'gsheet';
            }

            fetch(endpoint, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    elements.taskList.innerHTML = `<li class="list-group-item list-group-item-danger">${data.error}</li>`;
                } else {
                    elements.taskList.innerHTML = '';
                    data.tasks.forEach(task => {
                        const li = document.createElement('li');
                        li.className = 'list-group-item';
                        li.textContent = `${task.description} (Email: ${task.email}, Recipient: ${task.recipient})`;
                        if (elements.emailGenerator) {
                            li.addEventListener('click', () => {
                                const taskInput = elements.emailGenerator.querySelector('input[name="task"]');
                                const emailInput = elements.emailGenerator.querySelector('input[name="email"]');
                                const recipientInput = elements.emailGenerator.querySelector('input[name="recipient"]');
                                
                                if (taskInput && emailInput && recipientInput) {
                                    taskInput.value = task.description;
                                    emailInput.value = task.email;
                                    recipientInput.value = task.recipient;
                                }
                            });
                        }
                        elements.taskList.appendChild(li);
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                elements.taskList.innerHTML = `<li class="list-group-item list-group-item-danger">An error occurred while processing the file.</li>`;
            });
        });
    }

    // Document form submit handler
    if (elements.documentForm && elements.analysisResult) {
        elements.documentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(elements.documentForm);
            fetch('/analyze_documents', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    elements.analysisResult.textContent = data.error;
                } else {
                    elements.analysisResult.textContent = data.analysis;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                elements.analysisResult.textContent = 'An error occurred while analyzing the documents.';
            });
        });
    }

    // Email generator submit handler
    if (elements.emailGenerator && elements.generatedEmail) {
        elements.emailGenerator.addEventListener('submit', function(e) {
            e.preventDefault();
            const taskInput = elements.emailGenerator.querySelector('input[name="task"]');
            const emailInput = elements.emailGenerator.querySelector('input[name="email"]');
            const recipientInput = elements.emailGenerator.querySelector('input[name="recipient"]');
            
            if (!taskInput || !emailInput || !recipientInput) return;
            
            const task = taskInput.value;
            const email = emailInput.value;
            const recipient = recipientInput.value;
            
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
                    elements.generatedEmail.textContent = data.error;
                } else {
                    elements.generatedEmail.textContent = data.email;
                }
            })
            .catch(error => {
                console.error('Error:', error);
                elements.generatedEmail.textContent = 'An error occurred while generating the email.';
            });
        });
    }
});
