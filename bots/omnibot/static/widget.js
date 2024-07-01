// widget.js
const modeLabels = [
    { value: 'helpful_assistant', label: '🛠️ עוזר מועיל' },
    { value: 'funny_comedian', label: '😂 קומיקאי מצחיק' },
    { value: 'barkuni', label: '👾 ברקוני' },
    { value: 'sarcastic_friend', label: '😏 חבר סרקסטי' },
    { value: 'professional_advisor', label: '💼 יועץ מקצועי' },
    { value: 'cheerful_motivator', label: '😊 מעודד עליז' },
    { value: 'wise_mentor', label: '🧠 מנטור חכם' },
    { value: 'curious_explorer', label: '🔍 חוקר סקרן' },
    { value: 'calm_meditator', label: '🧘 מתרגל מדיטציה רגוע' },
    { value: 'tech_guru', label: '💻 גורו טכנולוגי' },
    { value: 'enthusiastic_marketer', label: '🤑 איש מכירות ללא מעצורים'},    
    { value: 'inventive_thinker', label: '💡 חושב יצירתי' },
    { value: 'argumentative_debater', label: '🗣️ ווכחן' },
    { value: 'angry_companion', label: '😡 חבר כועס' },
    { value: 'nonsense', label: '🤪 שטויות' },
];

let currentPersonality = null;
let shouldCheckPersonality = false;

document.addEventListener('DOMContentLoaded', function() {
    const slider = document.getElementById('mode-slider');
    const sliderLabel = document.getElementById('slider-label');
    slider.max = modeLabels.length - 1;
    
    function updateMode(index) {
        const mode = modeLabels[index];
        setPrompt(mode.value);
    }

    slider.addEventListener('input', function() {
        updateMode(this.value);
    });

    // Initialize with first mode
    updateMode(3);
    slider.value = 3;

    // Initial personality check
    checkAndUpdatePersonality();
});

function setPrompt(selectedPrompt) {
    fetch('/set_prompt', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ label: selectedPrompt })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Prompt set:', data);
        currentPersonality = selectedPrompt;
        updateChatbotTitle(selectedPrompt);
    })
    .catch(error => console.error('Error setting prompt:', error));
}

function updateChatbotTitle(selectedPrompt) {
    const titleElement = document.querySelector('.chat-header h1');
    if (titleElement) {
        const mode = modeLabels.find(mode => mode.value === selectedPrompt);
        titleElement.textContent = mode ? mode.label : '😏 חבר סרקסטי';
    }
}

function checkAndUpdatePersonality() {
    if (!shouldCheckPersonality) return;
    
    fetch('/get_current_personality', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        const serverPersonality = data.current_personality;
        if (serverPersonality !== currentPersonality) {
            currentPersonality = serverPersonality;
            const personalityIndex = modeLabels.findIndex(mode => mode.value === serverPersonality);
            
            if (personalityIndex !== -1) {
                const slider = document.querySelector('#mode-slider');
                if (slider) {
                    slider.value = personalityIndex;
                }
                updateChatbotTitle(serverPersonality);
            }
        }
    })
    .catch(error => console.error('Error:', error))
    .finally(() => {
        shouldCheckPersonality = false;
    });
}

// Modified fetch override to set flag for personality check after specific operations
const originalFetch = window.fetch;
window.fetch = function(url, options) {
    return originalFetch.apply(this, arguments).then(response => {
        // Set flag to check personality after chat messages or other relevant operations
        if (url.includes('/chat') || url.includes('/some_other_relevant_endpoint')) {
            shouldCheckPersonality = true;
        }
        
        if (shouldCheckPersonality) {
            checkAndUpdatePersonality();
        }
        
        return response;
    });
};