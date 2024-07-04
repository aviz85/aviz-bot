// dashboard.js
document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadButton = document.getElementById('upload-button');
    const uploadProgress = document.getElementById('upload-progress');
    const appendProgress = document.getElementById('append-progress');
    const fileList = document.getElementById('file-list');

    // File drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        handleFiles(files);
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        const files = e.target.files;
        handleFiles(files);
    });

    // Upload button click
    uploadButton.addEventListener('click', () => {
        fileInput.click();
    });

    function handleFiles(files) {
        for (const file of files) {
            if (file.type === 'text/plain' || file.type === 'application/pdf' || file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
                uploadFile(file);
            } else {
                alert('Invalid file type. Please upload only txt, pdf, or docx files.');
            }
        }
    }

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const uploadProgress = document.getElementById('upload-progress');
    const appendProgress = document.getElementById('append-progress');

    try {
        // Upload file
        if (uploadProgress) {
            uploadProgress.style.display = 'block';
        }
        const uploadResponse = await fetch('/upload_file', {
            method: 'POST',
            body: formData,
        });

        if (!uploadResponse.ok) {
            throw new Error(`HTTP error! status: ${uploadResponse.status}`);
        }

        const uploadResult = await uploadResponse.json();
        console.log('Upload result:', uploadResult);

        // Update upload progress
        if (uploadProgress && uploadProgress.querySelector('.progress')) {
            uploadProgress.querySelector('.progress').style.width = '100%';
        }

        // Wait a moment to ensure the file is fully saved
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Append knowledge
        if (appendProgress) {
            appendProgress.style.display = 'block';
        }
        
        console.log('Appending knowledge with file path:', uploadResult.file_path);
        
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

        // Update append progress
        if (appendProgress && appendProgress.querySelector('.progress')) {
            appendProgress.querySelector('.progress').style.width = '100%';
        }

        // Update file list
        await updateFileList();

        console.log('File uploaded and knowledge appended successfully');

    } catch (error) {
        console.error('Detailed error:', error);
        alert(`An error occurred: ${error.message}`);
    } finally {
        setTimeout(() => {
            if (uploadProgress) {
                uploadProgress.style.display = 'none';
                if (uploadProgress.querySelector('.progress')) {
                    uploadProgress.querySelector('.progress').style.width = '0';
                }
            }
            if (appendProgress) {
                appendProgress.style.display = 'none';
                if (appendProgress.querySelector('.progress')) {
                    appendProgress.querySelector('.progress').style.width = '0';
                }
            }
        }, 1000);
    }
}

async function updateFileList() {
    try {
        const response = await fetch('/get_file_list');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const files = await response.json();
        console.log('Retrieved file list:', files);

        const fileList = document.getElementById('file-list');
        fileList.innerHTML = '';
        files.forEach(file => {
            const li = document.createElement('li');
            li.textContent = file;
            const deleteButton = document.createElement('span');
            deleteButton.textContent = '❌';
            deleteButton.classList.add('delete-file');
            deleteButton.onclick = () => confirmDelete(file);
            li.appendChild(deleteButton);
            fileList.appendChild(li);
        });
    } catch (error) {
        console.error('Error fetching file list:', error);
    }
}

    function confirmDelete(filename) {
        if (confirm(`Are you sure you want to delete ${filename}?`)) {
            deleteFile(filename);
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
                updateFileList();
            } else {
                alert('Failed to delete file');
            }
        })
        .catch(error => console.error('Error deleting file:', error));
    }

    // Initial file list update
    updateFileList();
});