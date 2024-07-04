let personas = [];
let unsavedChanges = false;
let currentOpenEmojiPicker = null;


document.addEventListener('DOMContentLoaded', function() {
    fetchPersonas();
    fetchCurrentPersona();
    loadGlobalInstructions();
    fetchFileList();
    setupButtonListeners();
    setupUnsavedChangesWarning();
});

function fetchPersonas() {
    fetch('/get_personas')
        .then(response => response.json())
        .then(data => {
            personas = data;
            updatePersonasList();
        })
        .catch(error => console.error('Error fetching personas:', error));
}

function updatePersonasList() {
    const personaList = document.getElementById('persona-list');
    if (personaList) {
        personaList.innerHTML = '';
        personas.forEach(persona => {
            const li = document.createElement('li');
            li.textContent = `${persona.display_name} (${persona.slug}) - ${persona.emojicon}`;
            li.onclick = () => setPersona(persona.slug);
            personaList.appendChild(li);
        });
    }

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
    console.log("Creating persona item for:", persona.slug);
    const item = document.createElement('div');
    item.className = 'persona-item';
    item.innerHTML = `
        <p class="persona-slug">${persona.slug}</p>
        <input type="text" class="persona-display-name" value="${persona.display_name}" placeholder="שם תצוגה">
        <div class="emoji-picker-container">
            <button type="button" class="emoji-picker-button persona-emojicon">${persona.emojicon || '😀'}</button>
            <emoji-picker class="emoji-picker" style="display: none; position: absolute; z-index: 1000;"></emoji-picker>
        </div>
        <textarea class="persona-prompt" rows="3" cols="50" placeholder="תוכן הפרומפט">${persona.prompt || ''}</textarea>
        <button class="save-persona">שמור</button>
        <button class="delete-persona">מחק</button>`;

    const inputs = item.querySelectorAll('input, textarea');
    inputs.forEach(input => {
        input.addEventListener('input', () => {
            unsavedChanges = true;
        });
    });

    const emojiButton = item.querySelector('.emoji-picker-button');
    const emojiPicker = item.querySelector('emoji-picker');

    emojiButton.addEventListener('click', (event) => {
        event.stopPropagation();
        if (currentOpenEmojiPicker && currentOpenEmojiPicker !== emojiPicker) {
            currentOpenEmojiPicker.style.display = 'none';
        }
        if (emojiPicker.style.display === 'none') {
            emojiPicker.style.display = 'block';
            const rect = emojiButton.getBoundingClientRect();
            emojiPicker.style.top = `${rect.bottom + window.scrollY}px`;
            emojiPicker.style.left = `${rect.left + window.scrollX}px`;
            currentOpenEmojiPicker = emojiPicker;
        } else {
            emojiPicker.style.display = 'none';
            currentOpenEmojiPicker = null;
        }
    });

    emojiPicker.addEventListener('emoji-click', event => {
        emojiButton.textContent = event.detail.unicode;
        emojiPicker.style.display = 'none';
        currentOpenEmojiPicker = null;
        unsavedChanges = true;
    });

    document.addEventListener('click', (event) => {
        if (currentOpenEmojiPicker && !currentOpenEmojiPicker.contains(event.target) && event.target !== emojiButton) {
            currentOpenEmojiPicker.style.display = 'none';
            currentOpenEmojiPicker = null;
        }
    });

    item.querySelector('.save-persona').addEventListener('click', () => savePersona(item, persona.slug));
    item.querySelector('.delete-persona').addEventListener('click', () => deletePersona(item, persona.slug, false));

    return item;
}

function setPersona(slug) {
    fetch('/set_persona', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ slug: slug }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error setting persona:', data.error);
        } else {
            console.log('Persona set successfully:', data.message);
            fetchCurrentPersona();
        }
    })
    .catch(error => console.error('Error setting persona:', error));
}

function fetchCurrentPersona() {
    fetch('/get_current_persona')
        .then(response => response.json())
        .then(persona => {
            if (persona.error) {
                console.error('Error fetching current persona:', persona.error);
            } else {
                document.getElementById('current-persona').textContent = 
                    `Current Persona: ${persona.display_name} (${persona.slug}) - ${persona.emojicon}`;
            }
        })
        .catch(error => console.error('Error fetching current persona:', error));
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

        const personasList = document.getElementById('personas-list');
        if (personasList) {
            const newPersonaItem = createPersonaItem(newPersona, true);
            newPersonaItem.classList.add('unsaved');
            personasList.appendChild(newPersonaItem);
            setUnsavedChanges(true);
        }
    }
}

function saveNewPersona(item, slug) {
    const data = {
        slug: slug,
        display_name: item.querySelector('.persona-display-name').value,
        emojicon: item.querySelector('.persona-emojicon').innerHTML,
        prompt: item.querySelector('.persona-prompt').value
    };
    fetch('/dashboard/personas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(createdPersona => {
        console.log('New persona created:', createdPersona);
        item.classList.remove('unsaved', 'new-persona');
        //item.querySelector('.save-new-persona').remove();
        //const saveButton = item.querySelector('.save-persona');
        //saveButton.replaceWith(saveButton.cloneNode(true));
        //item.querySelector('.save-persona').addEventListener('click', () => savePersona(item, slug));
        //const deleteButton = item.querySelector('.delete-persona');
        //deleteButton.replaceWith(deleteButton.cloneNode(true));
        item.querySelector('.delete-persona').addEventListener('click', () => deletePersona(item, slug, false));
        alert('פרסונה חדשה נוצרה בהצלחה');
        setUnsavedChanges(false);
    })
    .catch(error => {
        console.error('Error creating new persona:', error);
        alert('שגיאה ביצירת פרסונה חדשה');
    });
}

function savePersona(item, slug) {
        fetch('/get_personas')
            .then(response => response.json())
            .then(data => {
                let personaExists = data.some(persona => persona.slug === slug);

                if (personaExists) {
                    saveExistedPersona(item, slug);
                } else {
                    saveNewPersona(item, slug);
                }
            })
            .catch(error => {
                console.error('Error fetching personas:', error);
            });
    

}

function saveExistedPersona(item, slug) {
    const data = {
        display_name: item.querySelector('.persona-display-name').value,
        emojicon: item.querySelector('.persona-emojicon').innerHTML,
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
        item.classList.remove('unsaved');
        alert('פרסונה עודכנה בהצלחה');
        setUnsavedChanges(false);
        fetchPersonas();
    })
    .catch(error => {
        console.error('Error updating persona:', error);
        alert('שגיאה בעדכון הפרסונה');
    });
}

function deletePersona(item, slug, isNew) {
    if (confirm(`האם אתה בטוח שברצונך למחוק את הפרסונה ${slug}?`)) {
        if (isNew) {
            item.remove();
            setUnsavedChanges(false);
            alert('פרסונה נמחקה בהצלחה');
        } else {
            fetch(`/dashboard/personas/${slug}`, { method: 'DELETE' })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        console.error('Error deleting persona:', data.error);
                        alert('שגיאה במחיקת הפרסונה');
                    } else {
                        item.remove();
                        setUnsavedChanges(false);
                        alert('פרסונה נמחקה בהצלחה');
                    }
                })
                .catch(error => {
                    console.error('Error deleting persona:', error);
                    alert('שגיאה במחיקת הפרסונה');
                });
        }
    }
}

function loadGlobalInstructions() {
    fetch('/get_global_instructions')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error getting global instructions:', data.error);
            } else {
                document.getElementById('global-instructions').value = data.instructions || '';
            }
        })
        .catch(error => console.error('Error loading global instructions:', error));
}

function saveGlobalInstructions() {
    const instructions = document.getElementById('global-instructions').value;
    fetch('/set_global_instructions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ instructions: instructions })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error setting global instructions:', data.error);
        } else {
            console.log('Global instructions updated:', data);
            alert('הנחיות כלליות נשמרו בהצלחה');
        }
    })
    .catch(error => {
        console.error('Error saving global instructions:', error);
        alert('שגיאה בשמירת ההנחיות הכלליות');
    });
}

function uploadFile(event) {
    event.preventDefault();
    const formData = new FormData(event.target);

    fetch('/upload_file', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error uploading file:', data.error);
        } else {
            console.log('File uploaded successfully:', data.message);
            fetchFileList();
        }
    })
    .catch(error => console.error('Error uploading file:', error));
}

function appendKnowledge(filename) {
    fetch('/append_knowledge', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filename: filename }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error appending knowledge:', data.error);
        } else {
            console.log('Knowledge appended successfully:', data.message);
        }
    })
    .catch(error => console.error('Error appending knowledge:', error));
}

function fetchFileList() {
    fetch('/get_file_list')
        .then(response => response.json())
        .then(files => {
            const fileList = document.getElementById('file-list');
            fileList.innerHTML = '';
            files.forEach(file => {
                const li = document.createElement('li');
                li.textContent = file;
                const appendButton = document.createElement('button');
                appendButton.textContent = 'Append';
                appendButton.onclick = () => appendKnowledge(file);
                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'Delete';
                deleteButton.onclick = () => deleteFile(file);
                li.appendChild(appendButton);
                li.appendChild(deleteButton);
                fileList.appendChild(li);
            });
        })
        .catch(error => console.error('Error fetching file list:', error));
}

function deleteFile(filename) {
    if (confirm(`Are you sure you want to delete the file: ${filename}?`)) {
        fetch('/delete_file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ filename: filename }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('Error deleting file:', data.error);
            } else {
                console.log('File deleted successfully:', data.message);
                fetchFileList();
            }
        })
        .catch(error => console.error('Error deleting file:', error));
    }
}

function setUnsavedChanges(value) {
    unsavedChanges = value;
    updateUnsavedChangesWarning();
}

function updateUnsavedChangesWarning() {
    const warningElement = document.getElementById('unsaved-changes-warning');
    if (warningElement) {
        warningElement.style.display = unsavedChanges ? 'block' : 'none';
    }
}

function setupUnsavedChangesWarning() {
    window.onbeforeunload = function() {
        if (unsavedChanges) {
            return "You have unsaved changes. Are you sure you want to leave?";
        }
    };
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

    const createPersonaForm = document.getElementById('create-persona-form');
    if (createPersonaForm) {
        createPersonaForm.addEventListener('submit', event => {
            event.preventDefault();
            addNewPersona();
        });
    }

    const uploadForm = document.getElementById('upload-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', uploadFile);
    }

    const setInstructionsForm = document.getElementById('set-instructions-form');
    if (setInstructionsForm) {
        setInstructionsForm.addEventListener('submit', event => {
            event.preventDefault();
            saveGlobalInstructions();
        });
    }
}