const emojiMap = {
    ':-)': '😊',
    ':)': '😊',
    ':-(': '😞',
    ':(': '😞',
    ':-D': '😃',
    ':D': '😃',
    ':-P': '😛',
    ':P': '😛',
    ';-)': '😉',
    ';)': '😉',
    ':-O': '😮',
    ':O': '😮',
    '<3': '❤️',
    ':-*': '😘',
    ':*': '😘'
    // Add more as needed
};

let enterDisabled = false;

function replaceEmoticonsWithEmoji(text) {
    for (const [emoticon, emoji] of Object.entries(emojiMap)) {
        text = text.split(emoticon).join(emoji);
    }
    return text;
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        if (enterDisabled) {
            event.preventDefault();
        } else {
            sendMessage();
        }
    }
}

function defaultFetchMessage(message) {
    return fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    });
}

function sendMessage(fetchMessageFunction = defaultFetchMessage) {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const message = userInput.value.trim();

    if (message === '') return;

    // Add user message to chat box
    addMessageToChat('user', message);

    // Clear input field and disable send button and enter key
    userInput.value = '';
    sendButton.disabled = true;
    enterDisabled = true;

    // Send message to the server using the provided fetch function
    fetchMessageFunction(message)
    .then(response => response.json())
    .then(data => {
        if (data && data.response) {
            addMessageToChat('bot', data.response);
        } else {
            addMessageToChat('bot', 'Sorry, something went wrong.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        addMessageToChat('bot', 'Sorry, something went wrong.');
    })
    .finally(() => {
        // Re-enable the send button and enter key after the response is handled
        sendButton.disabled = false;
        enterDisabled = false;
    });
}

function addMessageToChat(sender, message) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);

    // Replace emoticons with emoji
    const messageWithEmoji = replaceEmoticonsWithEmoji(message);

    // Convert Markdown to HTML
    const md = window.markdownit();
    let htmlContent = md.render(messageWithEmoji);

    // Wrap images in a clickable link
    htmlContent = htmlContent.replace(/<img src="(.*?)"(.*?)>/g, '<a href="$1" target="_blank"><img src="$1" class="chat-image"$2></a>');

    // Process each paragraph
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = htmlContent;
    const paragraphs = tempDiv.querySelectorAll('p');

    paragraphs.forEach(paragraph => {
        const firstChar = paragraph.textContent.trim().charAt(0);
        if (/[א-תء-يםןץףך]/.test(firstChar)) {
            paragraph.style.direction = 'rtl';
        } else {
            paragraph.style.direction = 'ltr';
        }
    });

    messageElement.innerHTML = tempDiv.innerHTML;
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
