// Main JavaScript file for common functionality across the application

// Show loading spinner
function showSpinner() {
    document.getElementById('spinner').classList.remove('d-none');
}

// Hide loading spinner
function hideSpinner() {
    document.getElementById('spinner').classList.add('d-none');
}

// Display error messages
function showError(message) {
    const errorAlert = document.createElement('div');
    errorAlert.className = 'alert alert-danger alert-dismissible fade show';
    errorAlert.role = 'alert';
    errorAlert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const alertContainer = document.getElementById('alert-container');
    alertContainer.appendChild(errorAlert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        errorAlert.classList.remove('show');
        setTimeout(() => {
            alertContainer.removeChild(errorAlert);
        }, 150);
    }, 5000);
}

// Display success messages
function showSuccess(message) {
    const successAlert = document.createElement('div');
    successAlert.className = 'alert alert-success alert-dismissible fade show';
    successAlert.role = 'alert';
    successAlert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const alertContainer = document.getElementById('alert-container');
    alertContainer.appendChild(successAlert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        successAlert.classList.remove('show');
        setTimeout(() => {
            alertContainer.removeChild(successAlert);
        }, 150);
    }, 5000);
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Fetch categories from the server
async function fetchCategories() {
    try {
        const response = await fetch('/api/categories');
        if (!response.ok) {
            throw new Error('Failed to fetch categories');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching categories:', error);
        showError('Failed to load expense categories. Please refresh the page.');
        return [];
    }
}

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize all popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Set active navigation link
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });
});

// Export data functionality
function exportData(format) {
    window.location.href = `/api/export-data?format=${format}`;
}

// Ask AI analysis question
async function askAIQuestion() {
    const questionInput = document.getElementById('ai-question');
    const question = questionInput.value.trim();
    
    if (!question) {
        showError('Please enter a question to analyze your finances.');
        return;
    }
    
    try {
        showSpinner();
        
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question })
        });
        
        if (!response.ok) {
            throw new Error('Failed to analyze finances');
        }
        
        const data = await response.json();
        
        if (data.success) {
            const aiResponseElement = document.getElementById('ai-response');
            aiResponseElement.innerHTML = `
                <div class="card my-3">
                    <div class="card-header bg-primary text-white">
                        <strong>AI Analysis</strong>
                    </div>
                    <div class="card-body">
                        <h5 class="card-title">${question}</h5>
                        <p class="card-text">${data.answer.replace(/\n/g, '<br>')}</p>
                    </div>
                </div>
            `;
            questionInput.value = '';
        } else {
            showError(data.error || 'Failed to analyze finances');
        }
        
    } catch (error) {
        console.error('Error analyzing finances:', error);
        showError('Failed to analyze finances. Please try again later.');
    } finally {
        hideSpinner();
    }
}
