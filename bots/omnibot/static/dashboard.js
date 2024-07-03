// Global variables
let currentPersona = null;
let personas = [];

document.addEventListener('DOMContentLoaded', function() {
    // Load personas
    loadPersonas();
    
    // Load global instructions
    loadGlobalInstructions();
    
    // File upload functionality
    setupFileUpload();
    
    // Initial file list update
    updateFileList();
    
    // Add listeners for buttons
    setupButtonListeners();
});

function loadPersonas() {
    fetch('/get_personas')
        .then(response => response.json())
        .then(data => {
            personas = data;
            updatePersonasList();
        })
        .catch(error => console.error('Error fetching personas:', error));
}

function updatePersonasList() {
    const personasList = document.getElementById('personas-list');
    if (personasList) {
        personasList.innerHTML = '';
        personas.forEach(persona => {
            const personaItem = createPersonaItem(persona);
            personasList.appendChild(personaItem);
        });
    }
}

function createPersonaItem(persona) {
    const item = document.createElement('div');
    item.className = 'persona-item';
    item.innerHTML = `
        <p class="persona-slug">${persona.slug}</p>
        <input type="text" class="persona-display-name" value="${persona.display_name}" placeholder="שם תצוגה">
        <input type="text" class="persona-emojicon" value="${persona.emojicon}" placeholder="אימוג'י">
        <textarea class="persona-prompt" rows="3" cols="50" placeholder="תוכן הפרומפט">${persona.prompt || ''}</textarea>
        <button class="save-persona">שמור</button>
        <button class="delete-persona">מחק</button>
    `;

    item.querySelector('.save-persona').addEventListener('click', () => savePersona(item, persona.slug));
    item.querySelector('.delete-persona').addEventListener('click', () => deletePersona(persona.slug));

    return item;
}

function savePersona(item, slug) {
    const data = {
        display_name: item.querySelector('.persona-display-name').value,
        emojicon: item.querySelector('.persona-emojicon').value,
        prompt: item.querySelector('.persona-prompt').value
    };

    fetch('/dashboard/personas/' + slug, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(updatedPersona => {
        console.log('Persona updated:', updatedPersona);
        alert('פרסונה עודכנה בהצלחה');
        loadPersonas();  // Reload all personas to reflect changes
    })
    .catch(error => {
        console.error('Error updating persona:', error);
        alert('שגיאה בעדכון הפרסונה');
    });
}

function deletePersona(slug) {
    if (confirm('האם אתה בטוח שברצונך למחוק פרסונה זו?')) {
        fetch('/dashboard/personas/' + slug, { method: 'DELETE' })
            .then(response => {
                if (response.ok) {
                    loadPersonas();  // Reload all personas to reflect changes
                    alert('פרסונה נמחקה בהצלחה');
                } else {
                    throw new Error('Failed to delete persona');
                }
            })
            .catch(error => {
                console.error('Error deleting persona:', error);
                alert('שגיאה במחיקת הפרסונה');
            });
    }
}

function loadGlobalInstructions() {
    fetch('/dashboard/global_instructions')
        .then(response => response.json())
        .then(data => {
            document.getElementById('global-instructions').value = data.instructions || '';
        })
        .catch(error => console.error('Error loading global instructions:', error));
}

function saveGlobalInstructions() {
    const instructions = document.getElementById('global-instructions').value;
    fetch('/dashboard/global_instructions', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ global_instructions: instructions })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Global instructions updated:', data);
        alert('הנחיות כלליות נשמרו בהצלחה');
    })
    .catch(error => {
        console.error('Error saving global instructions:', error);
        alert('שגיאה בשמירת ההנחיות הכלליות');
    });
}

function setupFileUpload() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadButton = document.getElementById('upload-button');

    if (dropZone && fileInput && uploadButton) {
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            handleFiles(files);
        });

        fileInput.addEventListener('change', (e) => {
            const files = e.target.files;
            handleFiles(files);
        });

        uploadButton.addEventListener('click', () => {
            fileInput.click();
        });
    }
}

function handleFiles(files) {
    for (const file of files) {
        if (file.type === 'text/plain' || file.type === 'application/pdf' || file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
            uploadFile(file);
        } else {
            alert('סוג קובץ לא חוקי. אנא העלה רק קבצי txt, pdf, או docx.');
        }
    }
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const uploadProgress = document.getElementById('upload-progress');
    const appendProgress = document.getElementById('append-progress');

    try {
        if (uploadProgress) {
            uploadProgress.style.display = 'block';
        }
        const uploadResponse = await fetch('/upload_file', {
            method: 'POST',
            body: formData,
        });

        if (!uploadResponse.ok) {
            throw new Error(`HTTP error! status: ${uploadResponse.status}`);
        }

        const uploadResult = await uploadResponse.json();
        console.log('Upload result:', uploadResult);

        if (uploadProgress && uploadProgress.querySelector('.progress')) {
            uploadProgress.querySelector('.progress').style.width = '100%';
        }

        await new Promise(resolve => setTimeout(resolve, 1000));

        if (appendProgress) {
            appendProgress.style.display = 'block';
        }
        
        const appendResponse = await fetch('/append_knowledge', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ filename: uploadResult.filename }),
        });

        if (!appendResponse.ok) {
            throw new Error(`HTTP error! status: ${appendResponse.status}`);
        }

        const appendResult = await appendResponse.json();
        console.log('Append result:', appendResult);

        if (appendProgress && appendProgress.querySelector('.progress')) {
            appendProgress.querySelector('.progress').style.width = '100%';
        }

        await updateFileList();

        console.log('File uploaded and knowledge appended successfully');
        alert('הקובץ הועלה והידע נוסף בהצלחה');

    } catch (error) {
        console.error('Detailed error:', error);
        alert(`אירעה שגיאה: ${error.message}`);
    } finally {
        setTimeout(() => {
            if (uploadProgress) {
                uploadProgress.style.display = 'none';
                if (uploadProgress.querySelector('.progress')) {
                    uploadProgress.querySelector('.progress').style.width = '0';
                }
            }
            if (appendProgress) {
                appendProgress.style.display = 'none';
                if (appendProgress.querySelector('.progress')) {
                    appendProgress.querySelector('.progress').style.width = '0';
                }
            }
        }, 1000);
    }
}

async function updateFileList() {
    try {
        const response = await fetch('/get_file_list');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const files = await response.json();
        console.log('Retrieved file list:', files);

        const fileList = document.getElementById('file-list');
        if (fileList) {
            fileList.innerHTML = '';
            files.forEach(file => {
                const li = document.createElement('li');
                li.textContent = file;
                const deleteButton = document.createElement('span');
                deleteButton.textContent = '❌';
                deleteButton.classList.add('delete-file');
                deleteButton.onclick = () => confirmDelete(file);
                li.appendChild(deleteButton);
                fileList.appendChild(li);
            });
        }
    } catch (error) {
        console.error('Error fetching file list:', error);
        alert('שגיאה בטעינת רשימת הקבצים');
    }
}

function confirmDelete(filename) {
    if (confirm(`האם אתה בטוח שברצונך למחוק את ${filename}?`)) {
        deleteFile(filename);
    }
}

function deleteFile(filename) {
    fetch('/delete_file', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filename: filename }),
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            updateFileList();
            alert('הקובץ נמחק בהצלחה');
        } else {
            throw new Error('Failed to delete file');
        }
    })
    .catch(error => {
        console.error('Error deleting file:', error);
        alert('שגיאה במחיקת הקובץ');
    });
}

function setupButtonListeners() {
    const saveGlobalInstructionsButton = document.getElementById('save-global-instructions');
    if (saveGlobalInstructionsButton) {
        saveGlobalInstructionsButton.addEventListener('click', saveGlobalInstructions);
    }

    const addPersonaButton = document.getElementById('add-persona');
    if (addPersonaButton) {
        addPersonaButton.addEventListener('click', addNewPersona);
    }
}

function addNewPersona() {
    const slug = prompt('הכנס מזהה ייחודי לפרסונה החדשה:');
    if (slug) {
        const newPersona = {
            slug: slug,
            display_name: '',
            emojicon: '',
            prompt: ''
        };

        fetch('/dashboard/personas', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newPersona)
        })
        .then(response => response.json())
        .then(createdPersona => {
            console.log('New persona created:', createdPersona);
            loadPersonas();  // Reload all personas to reflect changes
            alert('פרסונה חדשה נוצרה בהצלחה');
        })
        .catch(error => {
            console.error('Error creating new persona:', error);
            alert('שגיאה ביצירת פרסונה חדשה');
        });
    }
}