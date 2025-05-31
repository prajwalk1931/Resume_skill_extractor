document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const resultArea = document.getElementById('resultArea');

    // Add drag and drop styles
    dropZone.style.border = '2px dashed #ccc';
    dropZone.style.borderRadius = '10px';
    dropZone.style.padding = '20px';
    dropZone.style.textAlign = 'center';
    dropZone.style.cursor = 'pointer';
    dropZone.style.backgroundColor = 'transparent';

    // Handle drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#007bff';
        dropZone.style.backgroundColor = '#e9f4ff';
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#ccc';
        dropZone.style.backgroundColor = 'transparent';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = '#ccc';
        dropZone.style.backgroundColor = 'transparent';
        
        const file = e.dataTransfer.files[0];
        if (file && file.type === 'application/pdf') {
            handleFile(file);
        } else {
            showToast('Please upload a PDF file', 'error');
        }
    });

    // Handle click to open file picker
    dropZone.addEventListener('click', () => {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.pdf';
        fileInput.style.display = 'none';
        
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file && file.type === 'application/pdf') {
                handleFile(file);
            } else {
                showToast('Please upload a PDF file', 'error');
            }
        });
        
        document.body.appendChild(fileInput);
        fileInput.click();
        fileInput.remove();
    });

    async function handleFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        // Show loading state
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading';
        loadingDiv.innerHTML = '<div class="loading-spinner"></div>';
        document.body.appendChild(loadingDiv);

        try {
            const response = await fetch('http://localhost:8000/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Failed to upload resume');
            }

            const data = await response.json();
            
            if (data.status === 'success') {
                // Remove loading state
                loadingDiv.remove();
                displayResults(data.data);
                // Show success message
                showToast('Resume processed successfully!');
            } else {
                loadingDiv.remove();
                showToast('Error processing resume: ' + data.message, 'error');
            }
        } catch (error) {
            loadingDiv.remove();
            console.error('Error:', error);
            showToast('Error uploading file. Please try again.', 'error');
        }
    }

    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        // Remove toast after 3 seconds
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    function displayResults(data) {
        resultArea.classList.remove('d-none');
        const skillsList = document.getElementById('skillsList');
        const basicInfo = document.getElementById('basicInfo');

        // Display basic info
        basicInfo.innerHTML = `
            <div class="basic-info">
                <p><strong>Name:</strong> ${data.name || 'Not found'}</p>
                <p><strong>Email:</strong> ${data.email || 'Not found'}</p>
                <p><strong>Phone:</strong> ${data.phone || 'Not found'}</p>
            </div>
        `;

        // Display skills
        if (data.skills && data.skills.length > 0) {
            skillsList.innerHTML = `
                <div class="skills-grid">
                    ${data.skills.map(skill => 
                        `<div class="skill-badge">
                            <span class="badge bg-primary">${skill}</span>
                        </div>`
                    ).join('')}
                </div>
            `;
        } else {
            skillsList.innerHTML = '<p class="text-muted">No skills found</p>';
        }

    }
});
