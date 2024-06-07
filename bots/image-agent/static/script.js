// Connect to the WebSocket
const socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('connect', function() {
    console.log('WebSocket connected!');
});

socket.on('image_started', function(data) {
    console.log(data.message);
    // Update UI to show that image generation has started
    addMessageToChat('bot', 'Image generation started...');
});

socket.on('image_progress', function(data) {
    console.log(data.progress);
    // Update UI to show progress
    addMessageToChat('bot', `Image generation progress: ${data.progress}`);
});

socket.on('image_completed', function(data) {
    console.log('Image generated:', data.image_url);
    // Update UI to show the generated image
    addMessageToChat('bot', `Image generated: <a href="${data.image_url}" target="_blank"><img src="${data.image_url}" class="chat-image"></a>`);
});

socket.on('error', function(data) {
    console.error(data.message);
    // Handle errors
    addMessageToChat('bot', 'Sorry, something went wrong.');
});

function handleImageGeneration(prompt) {
    socket.emit('generate_image', { prompt: prompt });
}

function fetchMessageWithImageHandling(message) {
    return fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
    .then(response => {
        if (response.status === 201) {
            handleImageGeneration(message);
        } else {
            return response;
        }
    });
}

// Use the overridden fetch function in the main sendMessage call
sendMessage(fetchMessageWithImageHandling);
