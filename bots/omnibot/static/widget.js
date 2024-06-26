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
    { value: 'storyteller', label: '📖 מספר סיפורים' },
    { value: 'sarcastic', label: '😜 סרקסטי' },
    { value: 'nonsense', label: '🤪 שטויות' }
];

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
    updateMode(0);
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
        updateChatbotTitle(selectedPrompt);
    })
    .catch(error => console.error('Error setting prompt:', error));
}

function updateChatbotTitle(selectedPrompt) {
    const titleElement = document.querySelector('.chat-header h1');
    if (titleElement) {
        const mode = modeLabels.find(mode => mode.value === selectedPrompt);
        titleElement.textContent = mode ? mode.label : 'ברקוני הבוט';
    }
}