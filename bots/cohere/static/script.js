function uploadDocuments() {
    const input = document.getElementById('document-upload');
    const files = input.files;
    if (files.length === 0) {
        alert('Please select at least one document to upload.');
        return;
    }

    const formData = new FormData();
    for (const file of files) {
        formData.append('documents', file);
    }

    const loadingAnimation = document.getElementById('loading-animation');
    const uploadedFilesContainer = document.getElementById('uploaded-files');
    
    // Show loading animation
    loadingAnimation.style.display = 'block';

    fetch('/upload-documents', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Hide loading animation
        loadingAnimation.style.display = 'none';

        if (data.error) {
            alert(data.error);
        } else {
            const sessionId = data.session_id;
            alert('Documents uploaded successfully.');
            
            // Display uploaded filenames
            uploadedFilesContainer.innerHTML = '';
            for (const file of files) {
                const fileElement = document.createElement('div');
                fileElement.classList.add('uploaded-file');
                fileElement.textContent = file.name;
                uploadedFilesContainer.appendChild(fileElement);
            }

            // Update fetchParams in localStorage
            if (typeof(Storage) !== 'undefined') {
                let fetchParams = {};
                try {
                    fetchParams = JSON.parse(localStorage.getItem('fetchParams')) || {};
                } catch (e) {
                    console.error('Error parsing fetchParams from localStorage', e);
                }
                fetchParams.session_id = sessionId;
                localStorage.setItem('fetchParams', JSON.stringify(fetchParams));
            } else {
                alert('Local storage is not supported by your browser.');
            }
        }
    })
    .catch(error => {
        // Hide loading animation
        loadingAnimation.style.display = 'none';

        console.error('Error uploading documents:', error);
        alert('An error occurred while uploading documents.');
    });
}
