// Global variables and functions
let messageCount = 0;
let documentCount = 0;

// Function to show modal
function showModal(content) {
    const backdrop = document.createElement('div');
    backdrop.className = 'selfie-modal-backdrop';
    const modal = document.createElement('div');
    modal.className = 'selfie-modal';
    modal.innerHTML = content;
    document.body.appendChild(backdrop);
    document.body.appendChild(modal);
    setTimeout(() => {
        backdrop.classList.add('active');
        modal.classList.add('active');
    }, 10);
    return { backdrop, modal };
}

// Function to close modal
function closeModal(backdrop, modal) {
    backdrop.classList.remove('active');
    modal.classList.remove('active');
    setTimeout(() => {
        backdrop.remove();
        modal.remove();
    }, 300);
}

function captureScreen() {
    const flash = document.createElement('div');
    flash.className = 'flash';
    document.body.appendChild(flash);
    flash.classList.add('active');

    const slider = document.querySelector('#mode-slider');
    const sliderHeight = slider ? slider.offsetHeight : 0;
    let originalSliderDisplay = '';

    if (slider) {
        originalSliderDisplay = slider.style.display;
    }

    setTimeout(() => {
        const chatContainer = document.querySelector('.chat-container');
        html2canvas(chatContainer, {
            backgroundColor: null,
            useCORS: true,
            scrollY: -window.scrollY
        }).then(canvas => {
            // Determine the amount to crop from the top
            const topCrop = 0; // Adjust this value as needed

            // Crop the captured image
            const croppedCanvas = document.createElement('canvas');
            const ctx = croppedCanvas.getContext('2d');
            croppedCanvas.width = canvas.width;
            croppedCanvas.height = canvas.height - sliderHeight - topCrop;
            
            // Draw the captured image onto the new canvas, excluding the top and slider areas
            ctx.drawImage(
                canvas, 
                0, topCrop, // Source X, Y
                canvas.width, canvas.height - sliderHeight - topCrop, // Source Width, Height
                0, 0, // Destination X, Y
                canvas.width, canvas.height - sliderHeight - topCrop // Destination Width, Height
            );

            // Pass the cropped canvas to combineWithBackground
            combineWithBackground(croppedCanvas);
        }).catch(error => {
            console.error('Screenshot failed:', error);
            alert('Failed to take screenshot. Please try again.');
        }).finally(() => {
            flash.remove();
            if (slider) {
                slider.style.display = originalSliderDisplay;
            }
        });
    }, 500);
}

function combineWithBackground(chatCanvas) {
    // Create a new canvas for the final image
    const finalCanvas = document.createElement('canvas');
    const ctx = finalCanvas.getContext('2d');

    // Determine the size of the rectangular canvas (3:2 aspect ratio)
    const height = Math.max(chatCanvas.width, chatCanvas.height) * 1.3;
    const width = height * 1.5;
    finalCanvas.width = width;
    finalCanvas.height = height;

    // Load a random background image
    const backgroundImage = new Image();
    const randomNum = Math.floor(Math.random() * 10) + 1;
    backgroundImage.src = `/custom/static/assets/background-${randomNum}.png`;

    backgroundImage.onload = () => {
        // Calculate scaling factor to fill the canvas while maintaining aspect ratio
        const scale = Math.max(width / backgroundImage.width, height / backgroundImage.height);
        const scaledWidth = backgroundImage.width * scale;
        const scaledHeight = backgroundImage.height * scale;

        // Draw background image, centered and scaled
        const x = (width - scaledWidth) / 2;
        const y = (height - scaledHeight) / 2;
        ctx.drawImage(backgroundImage, x, y, scaledWidth, scaledHeight);

        // Calculate position to center the chat screenshot
        const chatX = (width - chatCanvas.width) / 2;
        const chatY = (height - chatCanvas.height) / 2;

        // Create a rounded rectangle path for the chat screenshot
        const cornerRadius = 20; // Adjust this value to change the roundness of corners
        ctx.beginPath();
        ctx.moveTo(chatX + cornerRadius, chatY);
        ctx.lineTo(chatX + chatCanvas.width - cornerRadius, chatY);
        ctx.arcTo(chatX + chatCanvas.width, chatY, chatX + chatCanvas.width, chatY + cornerRadius, cornerRadius);
        ctx.lineTo(chatX + chatCanvas.width, chatY + chatCanvas.height - cornerRadius);
        ctx.arcTo(chatX + chatCanvas.width, chatY + chatCanvas.height, chatX + chatCanvas.width - cornerRadius, chatY + chatCanvas.height, cornerRadius);
        ctx.lineTo(chatX + cornerRadius, chatY + chatCanvas.height);
        ctx.arcTo(chatX, chatY + chatCanvas.height, chatX, chatY + chatCanvas.height - cornerRadius, cornerRadius);
        ctx.lineTo(chatX, chatY + cornerRadius);
        ctx.arcTo(chatX, chatY, chatX + cornerRadius, chatY, cornerRadius);
        ctx.closePath();

        // Create a clipping region
        ctx.save();
        ctx.clip();

        // Draw chat screenshot in the center with rounded corners
        ctx.drawImage(chatCanvas, chatX, chatY);

        // Restore the context
        ctx.restore();

        // Convert to data URL and show in modal
        const combinedImageDataUrl = finalCanvas.toDataURL('image/png');
        showScreenshotModal(combinedImageDataUrl);
    };

    backgroundImage.onerror = () => {
        console.error('Failed to load background image');
        showScreenshotModal(chatCanvas.toDataURL('image/png')); // Fallback to original screenshot
    };
}

function showScreenshotModal(imageDataUrl) {
    const { backdrop, modal } = showModal(`
        <div class="modal-content">
            <span class="close-button">&times;</span>
            <div class="screenshot-container">
                <img src="${imageDataUrl}" alt="Chat Selfie" class="screenshot-image">
            </div>
            <button class="download-button">
                <i class="fas fa-download"></i> הורדה
            </button>
        </div>
    `);

    modal.querySelector('.close-button').onclick = () => closeModal(backdrop, modal);
    modal.querySelector('.download-button').onclick = () => {
        const link = document.createElement('a');
        link.href = imageDataUrl;
        link.download = 'chat-selfie.png';
        link.click();
        closeModal(backdrop, modal);
    };
}

// Function to increment message count and check if it's time to show the modal
function incrementMessageCount() {
    messageCount++;
    if (messageCount === 3) {
        //setTimeout(showSelfieModal, 1750); // can we selfie ?
    }
}

// Function to show the selfie modal
function showSelfieModal() {
    const { backdrop, modal } = showModal(`
        <div class="modal-content">
            <span class="close-button">&times;</span>
            <p>אפשר סלפי? 📸</p>
            <button class="selfie-button">יאללה</button>
        </div>
    `);

    modal.querySelector('.close-button').onclick = () => closeModal(backdrop, modal);
    modal.querySelector('.selfie-button').onclick = () => {
        closeModal(backdrop, modal);
        captureScreen();
    };
}

// Function to add capture screen button and file upload button
function addHeaderButtons() {
    const chatHeader = document.querySelector('.chat-header');
    if (chatHeader) {
        // Create a spacer element
        const spacer = document.createElement('div');
        spacer.className = 'header-spacer';
        chatHeader.appendChild(spacer);

        // Create a container for the buttons
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'header-buttons';
        
        // Add file upload button
        const uploadButton = document.createElement('button');
        uploadButton.id = 'upload-button';
        uploadButton.className = 'upload-button';
        uploadButton.innerHTML = `
            <i class="fas fa-file-upload"></i>
            <span id="document-counter" class="document-counter">0</span>
        `;
        buttonContainer.appendChild(uploadButton);

        // Add capture screen button
        const captureButton = document.createElement('button');
        captureButton.innerHTML = '📸';
        captureButton.className = 'capture-screen-button';
        captureButton.onclick = captureScreen;
        buttonContainer.appendChild(captureButton);

        // Add the button container to the chat header
        chatHeader.appendChild(buttonContainer);

        // Create file input
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.id = 'file-input';
        fileInput.style.display = 'none';
        chatHeader.appendChild(fileInput);

        // Add event listeners
        uploadButton.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', handleFileUpload);
    }
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        uploadFile(file);
    }
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    try {
        // Upload file
        const uploadResponse = await fetch('/upload_file', {
            method: 'POST',
            body: formData,
        });
        if (!uploadResponse.ok) {
            throw new Error(`HTTP error! status: ${uploadResponse.status}`);
        }
        const uploadResult = await uploadResponse.json();
        console.log('Upload result:', uploadResult);

        // Append knowledge
        const appendResponse = await fetch('/append_knowledge', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ filename: uploadResult.filename }),
        });
        if (!appendResponse.ok) {
            throw new Error(`HTTP error! status: ${appendResponse.status}`);
        }
        const appendResult = await appendResponse.json();
        console.log('Append result:', appendResult);

        console.log('File uploaded and knowledge appended successfully');
        updateDocumentCount();
    } catch (error) {
        console.error('Error:', error);
        alert(`An error occurred: ${error.message}`);
        // Delete the file if there was an error
        if (uploadResult && uploadResult.filename) {
            deleteFile(uploadResult.filename);
        }
    }
}

function deleteFile(filename) {
    fetch('/delete_file', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filename: filename }),
    })
    .then(response => response.json())
    .then(result => {
        if (result.success) {
            updateDocumentCount();
        } else {
            alert('Failed to delete file');
        }
    })
    .catch(error => console.error('Error deleting file:', error));
}

async function updateDocumentCount() {
    try {
        const response = await fetch('/get_file_list');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const fileList = await response.json();
        documentCount = fileList.length;
        updateCounterDisplay();
    } catch (error) {
        console.error('Error updating document count:', error);
    }
}

function updateCounterDisplay() {
    const counter = document.getElementById('document-counter');
    if (counter) {
        counter.textContent = documentCount;
        counter.style.display = documentCount > 0 ? 'inline' : 'none';
    }
}

// Load html2canvas library and initialize
function loadHtml2Canvas() {
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
    script.onload = () => {
        addHeaderButtons();
        updateDocumentCount(); // Initial count update
        // Override the existing addMessageToChat function to include the message counter
        const originalAddMessageToChat = window.addMessageToChat;
        window.addMessageToChat = function(sender, message) {
            originalAddMessageToChat(sender, message);
            if (sender === 'bot') {
                incrementMessageCount();
            }
        };
    };
    document.head.appendChild(script);
}

// Initialize everything when the DOM is ready
document.addEventListener('DOMContentLoaded', loadHtml2Canvas);