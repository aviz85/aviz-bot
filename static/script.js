function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function sendMessage() {
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();
    
    if (message === '') return;

    // Add user message to chat box
    addMessageToChat('user', message);

    // Clear input field
    userInput.value = '';

    // Send message to the server
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        if (data.response) {
            addMessageToChat('bot', data.response);
        } else {
            addMessageToChat('bot', 'Sorry, something went wrong.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        addMessageToChat('bot', 'Sorry, something went wrong.');
    });
}

function addMessageToChat(sender, message) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function clearChat() {
    const chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = '';
    
    // Clear chat history on the server
    fetch('/reset', {
        method: 'POST'
    })
    .then(response => {
        if (response.ok) {
            console.log('Chat history cleared');
        } else {
            console.error('Failed to clear chat history');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
