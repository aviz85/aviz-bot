// Counter for message exchanges
let messageCount = 0;

// Function to increment message count and check if it's time to show the modal
function incrementMessageCount() {
    messageCount++;
    if (messageCount === 3) {
    	setTimeout(showSelfieModal, 750);
    }
}

// Function to show the selfie modal
function showSelfieModal() {
    const backdrop = document.createElement('div');
    backdrop.className = 'selfie-modal-backdrop';
    document.body.appendChild(backdrop);

    const modal = document.createElement('div');
    modal.className = 'selfie-modal';
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close-button">&times;</span>
            <p>אפשר סלפי? 📸</p>
            <button class="selfie-button">יאללה</button>
        </div>
    `;
    document.body.appendChild(modal);

    // Add flash element
    const flash = document.createElement('div');
    flash.className = 'flash';
    document.body.appendChild(flash);

    // Activate the modal and backdrop with a small delay
    setTimeout(() => {
        backdrop.classList.add('active');
        modal.classList.add('active');
    }, 10);

    // Close button functionality
    const closeButton = modal.querySelector('.close-button');
    closeButton.onclick = () => {
        closeModal(backdrop, modal, flash);
    };

    // Selfie button functionality
    const selfieButton = modal.querySelector('.selfie-button');
    selfieButton.onclick = () => {
        flash.classList.add('active');
        setTimeout(() => {
            takeScreenshot(backdrop, modal, flash);
        }, 500);
    };
}

// Function to close the modal
function closeModal(backdrop, modal, flash) {
    backdrop.classList.remove('active');
    modal.classList.remove('active');
    setTimeout(() => {
        backdrop.remove();
        modal.remove();
        flash.remove();
    }, 300);
}

function takeScreenshot(backdrop, modal, flash) {
    const chatContainer = document.querySelector('.chat-container');
    const slider = document.querySelector('#mode-slider'); // Adjust this selector to match your slider's class or ID
    
    // Store the original display value
    let originalDisplay = '';
    if (slider) {
        originalDisplay = slider.style.display;
    }

    // Function to capture the screenshot
    const captureScreenshot = () => {
        // Hide the slider
        if (slider) {
            slider.style.display = 'none';
        }

        // Take the screenshot
        html2canvas(chatContainer, {
            backgroundColor: null,
            useCORS: true,
            scrollY: -window.scrollY
        }).then(canvas => {
            // Immediately show the slider again
            if (slider) {
                slider.style.display = originalDisplay;
            }

            const imageDataUrl = canvas.toDataURL('image/png');
            showScreenshotModal(imageDataUrl, backdrop, modal, flash);
        });
    };

    // Ensure the entire chat container is visible
    chatContainer.scrollIntoView({behavior: "auto", block: "start"});

    // Wait a bit for any scrolling to finish before capturing
    setTimeout(captureScreenshot, 100);
}
// Function to show the screenshot in a new modal
function showScreenshotModal(imageDataUrl, backdrop, modal, flash) {
    closeModal(backdrop, modal, flash);

    const screenshotBackdrop = document.createElement('div');
    screenshotBackdrop.className = 'selfie-modal-backdrop';
    document.body.appendChild(screenshotBackdrop);

    const screenshotModal = document.createElement('div');
    screenshotModal.className = 'selfie-modal screenshot-modal';
    screenshotModal.innerHTML = `
        <div class="modal-content">
            <span class="close-button">&times;</span>
            <div class="screenshot-container">
                <img src="${imageDataUrl}" alt="Chat Selfie" class="screenshot-image">
            </div>
            <button class="download-button">
                <i class="fas fa-download"></i> הורדה
            </button>
        </div>
    `;
    document.body.appendChild(screenshotModal);

    // Activate the modal and backdrop with a small delay
    setTimeout(() => {
        screenshotBackdrop.classList.add('active');
        screenshotModal.classList.add('active');
    }, 10);

    // Close button functionality
    const closeButton = screenshotModal.querySelector('.close-button');
    closeButton.onclick = () => {
        closeModal(screenshotBackdrop, screenshotModal);
    };

    // Download button functionality
    const downloadButton = screenshotModal.querySelector('.download-button');
    downloadButton.onclick = () => {
        const link = document.createElement('a');
        link.href = imageDataUrl;
        link.download = 'chat-selfie.png';
        link.click();
    };
}


// Override the existing addMessageToChat function to include the message counter
const originalAddMessageToChat = addMessageToChat;
addMessageToChat = function(sender, message) {
    originalAddMessageToChat(sender, message);
    if (sender === 'bot') {
        incrementMessageCount();
    }
};

// Load html2canvas library
const script = document.createElement('script');
script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
document.head.appendChild(script);