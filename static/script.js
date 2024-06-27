const emojiMap = {
    ':-)': '😊',
    ':)': '😊',
    ':-(': '😞',
    ':(': '😞',
    ':-D': '😃',
    ':D': '😃',
    ':-P': '😛',
    ':P': '😛',
    ';)': '😉',
    ':-O': '😮',
    ':O': '😮',
    '<3': '❤️',
    ':-*': '😘',
    ':*': '😘'
    // Add more as needed
};

let enterDisabled = false;
let loadingMessageElement = null;

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

function getChatHistory() {
    const chatBox = document.getElementById('chat-box');
    const messageElements = chatBox.getElementsByClassName('message');
    const history = [];

    for (let element of messageElements) {
        const role = element.classList.contains('user') ? 'user' : 'assistant';
        
        // Extract text content without HTML tags
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = element.innerHTML;
        const content = tempDiv.textContent || tempDiv.innerText || "";
        
        history.push({
            role: role,
            content: [{ type: "text", text: content.trim() }]
        });
    }

    return history;
}

function defaultFetchMessage(message, history) {
    let fetchParams = {};
    try {
        fetchParams = JSON.parse(localStorage.getItem('fetchParams')) || {};
    } catch (e) {
        console.error('Error parsing fetchParams from localStorage', e);
    }

    return fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message, history: history, ...fetchParams })
    });
}

function sendMessage(fetchMessageFunction = defaultFetchMessage) {
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const message = userInput.value.trim();

    if (message === '') return;

    // Get chat history
    const history = getChatHistory();

    // Add user message to chat box
    addMessageToChat('user', message);

    // Clear input field and disable send button and enter key
    userInput.value = '';
    sendButton.disabled = true;
    enterDisabled = true;

    // Show loading message
    showLoadingMessage();

    // Send message to the server using the provided fetch function
    fetchMessageFunction(message, history)
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
        // Remove loading message
        if (loadingMessageElement) {
            loadingMessageElement.remove();
            loadingMessageElement = null;
        }
    });
}

function showLoadingMessage() {
    const chatBox = document.getElementById('chat-box');
    loadingMessageElement = document.createElement('div');
    loadingMessageElement.classList.add('message', 'bot');
    loadingMessageElement.innerHTML = '<span class="loading"><span>.</span><span>.</span><span>.</span></span>';
    chatBox.appendChild(loadingMessageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
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

    // Wrap Markdown audio links with audio player
    htmlContent = htmlContent.replace(/\[([^\]]+)\]\((.*?\.mp3)\)/g, (match, p1, p2) => {
        return `<figure>
                    <audio controls src="${p2}"></audio>
                    <a href="${p2}"> Download audio </a>
                </figure>`;
    });

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