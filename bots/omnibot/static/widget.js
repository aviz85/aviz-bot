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
});

function loadPersonas() {
    fetch('/get_personas')
        .then(response => response.json())
        .then(data => {
            personas = data;
            updateSliderOptions();
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
                alert ("helo" + data.emojicon)
                updateChatbotTitle(data.display_name, data.emojicon);
            }
        }
    })
    .catch(error => console.error('Error:', error))
    .finally(() => {
        shouldCheckPersona = false;
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