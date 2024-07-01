document.addEventListener('DOMContentLoaded', function() {
    // אישור מחיקת קובץ
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('האם אתה בטוח שברצונך למחוק קובץ זה?')) {
                e.preventDefault();
            }
        });
    });

    // הוספת אנימציה פשוטה בעת העלאת קובץ
    const uploadForm = document.querySelector('form[action$="upload_file"]');
    const uploadButton = uploadForm.querySelector('button[type="submit"]');
    uploadForm.addEventListener('submit', function() {
        uploadButton.textContent = 'מעלה...';
        uploadButton.disabled = true;
    });
});