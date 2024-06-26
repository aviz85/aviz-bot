document.addEventListener('DOMContentLoaded', function () {
    fetchPrompts();
});

function fetchPrompts() {
    fetch('/get_prompts')
        .then(response => response.json())
        .then(data => {
            console.log('Fetched prompts:', data);  // Debugging line to ensure we fetch the correct data
            const dropdown = document.getElementById('prompt-dropdown');
            data.prompts.forEach(prompt => {
                const option = document.createElement('option');
                option.value = prompt.label;
                option.text = prompt.label;
                dropdown.add(option);
            });
        })
        .catch(error => console.error('Error fetching prompts:', error));
}

function setPrompt() {
    const dropdown = document.getElementById('prompt-dropdown');
    const selectedPrompt = dropdown.value;
    if (selectedPrompt) {
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
}

function updateChatbotTitle(selectedPrompt) {
    const titleElement = document.querySelector('.chat-header h1');
    if (titleElement) {
        titleElement.textContent = labelToHebrew[selectedPrompt] || 'ברקוני הבוט';
    }
}

const labelToHebrew = {
    'helpful_assistant': '🛠️ עוזר מועיל',
    'funny_comedian': '😂 קומיקאי מצחיק',
    'barkuni': '🌦️ ברקוני',
    'sarcastic_friend': '😏 חבר סרקסטי',
    'professional_advisor': '💼 יועץ מקצועי',
    'cheerful_motivator': '😊 מעודד עליז',
    'wise_mentor': '🧠 מנטור חכם',
    'curious_explorer': '🔍 חוקר סקרן',
    'calm_meditator': '🧘 מתרגל מדיטציה רגוע',
    'tech_guru': '💻 גורו טכנולוגי',
    'storyteller': '📖 מספר סיפורים',
    'sarcastic': '😜 סרקסטי',
    'nonsense': '🤪 שטויות'
};
