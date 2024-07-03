let currentPersona = null;
let shouldCheckPersona = false;
let personas = [];

document.addEventListener('DOMContentLoaded', function() {
    const slider = document.getElementById('mode-slider');
    const sliderLabel = document.getElementById('slider-label');
    
    // Fetch personas list when the page loads
    loadPersonas();

    slider.addEventListener('input', function() {
        updateMode(this.value);
    });

    // Initial persona check
    checkAndUpdatePersona();

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
            updateSliderOptions();
            updatePersonasList();
            // Initialize with sarcastic_friend or first available persona
            const defaultIndex = personas.findIndex(p => p.slug === 'sarcastic_friend');
            updateMode(defaultIndex !== -1 ? defaultIndex : 0);
            const slider = document.getElementById('mode-slider');
            if (slider) {
                slider.value = defaultIndex !== -1 ? defaultIndex : 0;
            }
        })
        .catch(error => console.error('Error fetching personas:', error));
}

function updateSliderOptions() {
    const slider = document.getElementById('mode-slider');
    if (slider) {
        slider.innerHTML = '';
        personas.forEach((persona, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = `${persona.emojicon} ${persona.display_name}`;
            slider.appendChild(option);
        });
        slider.max = personas.length - 1;
    }
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

function updateMode(index) {
    const persona = personas[index];
    setPersona(persona.slug);
}

function setPersona(selectedPersonaSlug) {
    fetch('/set_persona', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ slug: selectedPersonaSlug })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Persona set:', data);
        currentPersona = selectedPersonaSlug;
        updateChatbotTitle(data.display_name, data.emojicon);
    })
    .catch(error => console.error('Error setting persona:', error));
}

function updateChatbotTitle(displayName, emojicon) {
    const titleElement = document.querySelector('.chat-header h1');
    if (titleElement) {
        titleElement.textContent = `${emojicon} ${displayName}`;
    }
}

function checkAndUpdatePersona() {
    if (!shouldCheckPersona) return;
    
    fetch('/get_current_persona', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.slug !== currentPersona) {
            currentPersona = data.slug;
            const personaIndex = personas.findIndex(p => p.slug === data.slug);
            
            if (personaIndex !== -1) {
                const slider = document.querySelector('#mode-slider');
                if (slider) {
                    slider.value = personaIndex;
                }
                updateChatbotTitle(data.display_name, data.emojicon);
            }
        }
    })
    .catch(error => console.error('Error:', error))
    .finally(() => {
        shouldCheckPersona = false;
    });
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
    fetch('/get_global_instructions')
        .then(response => response.json())
        .then(data => {
            document.getElementById('global-instructions').value = data.instructions || '';
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
        console.log('Global instructions updated:', data);
        alert('הנחיות כלליות נשמרו בהצלחה');
    })
    .catch(error => {
        console.error('Error saving global instructions:', error);
        alert('שגיאה בשמירת ההנחיות הכלליות');
    });
}

// Modified fetch override to set flag for persona check after specific operations
const originalFetch = window.fetch;
window.fetch = function(url, options) {
    return originalFetch.apply(this, arguments).then(response => {
        // Set flag to check persona after chat messages or other relevant operations
        if (url.includes('/chat') || url.includes('/set_persona')) {
            shouldCheckPersona = true;
        }
        
        if (shouldCheckPersona) {
            checkAndUpdatePersona();
        }
        
        return response;
    });
};

function setupFileUpload() {
    // Implement file upload functionality here
}

function updateFileList() {
    // Implement file list update functionality here
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