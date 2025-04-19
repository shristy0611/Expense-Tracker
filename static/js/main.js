// Main JavaScript file for common functionality across the application

// Default currency
let currentCurrency = localStorage.getItem('preferredCurrency') || 'USD';

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

// Get currency symbol for current currency
function getCurrencySymbol(currencyCode) {
    const currencies = {
        'USD': '$',
        'EUR': '€',
        'JPY': '¥',
        'GBP': '£',
        'AUD': 'A$',
        'CAD': 'C$',
        'CHF': 'CHF',
        'CNY': '¥',
        'INR': '₹'
    };
    
    return currencies[currencyCode] || currencyCode;
}

// Format currency with the current selected currency
function formatCurrency(amount, currency = currentCurrency) {
    const formatter = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    
    return formatter.format(amount);
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

// Fetch currencies from the server
async function fetchCurrencies() {
    try {
        const response = await fetch('/api/currencies');
        if (!response.ok) {
            throw new Error('Failed to fetch currencies');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching currencies:', error);
        return ['USD', 'EUR', 'JPY', 'GBP', 'AUD', 'CAD', 'CHF', 'CNY', 'INR'];
    }
}

// Get exchange rates
async function getExchangeRates(baseCurrency = 'USD') {
    try {
        const response = await fetch(`/api/exchange-rates?base=${baseCurrency}`);
        if (!response.ok) {
            throw new Error('Failed to fetch exchange rates');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching exchange rates:', error);
        return { success: false, error: 'Failed to fetch exchange rates' };
    }
}

// Force update of exchange rates
async function updateExchangeRates() {
    try {
        showSpinner();
        const response = await fetch('/api/update-exchange-rates', {
            method: 'POST'
        });
        if (!response.ok) {
            throw new Error('Failed to update exchange rates');
        }
        const result = await response.json();
        
        if (result.success) {
            showSuccess('Exchange rates updated successfully!');
            return true;
        } else {
            showError(result.error || 'Failed to update exchange rates');
            return false;
        }
    } catch (error) {
        console.error('Error updating exchange rates:', error);
        showError('Failed to update exchange rates. Please try again later.');
        return false;
    } finally {
        hideSpinner();
    }
}

// Set current currency and store preference
function setCurrentCurrency(currency) {
    currentCurrency = currency;
    localStorage.setItem('preferredCurrency', currency);
    
    // Update currency display
    const currentCurrencyEl = document.getElementById('currentCurrency');
    if (currentCurrencyEl) {
        currentCurrencyEl.textContent = currency;
    }
    
    // Reload the page with the new currency
    const url = new URL(window.location.href);
    url.searchParams.set('currency', currency);
    window.location.href = url.toString();
}

// Initialize UI
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
    
    // Initialize currency selector
    const currentCurrencyEl = document.getElementById('currentCurrency');
    const currencySelector = document.getElementById('currencySelector');
    
    if (currentCurrencyEl) {
        // Get currency from URL or localStorage
        const urlParams = new URLSearchParams(window.location.search);
        const urlCurrency = urlParams.get('currency');
        
        // If currency is specified in URL, update current currency
        if (urlCurrency) {
            currentCurrency = urlCurrency;
            localStorage.setItem('preferredCurrency', urlCurrency);
        }
        
        // Update displayed currency
        currentCurrencyEl.textContent = currentCurrency;
    }
    
    // Setup currency selector click handlers
    if (currencySelector) {
        const currencyOptions = currencySelector.querySelectorAll('.currency-option');
        currencyOptions.forEach(option => {
            option.addEventListener('click', function(e) {
                e.preventDefault();
                const selectedCurrency = this.dataset.currency;
                setCurrentCurrency(selectedCurrency);
            });
        });
    }
    
    // Add currency selection to forms
    const currencySelects = document.querySelectorAll('select.currency-select');
    currencySelects.forEach(select => {
        select.value = currentCurrency;
    });
});

// Export data functionality
function exportData(format) {
    window.location.href = `/api/export-data?format=${format}&currency=${currentCurrency}`;
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
            body: JSON.stringify({ 
                question,
                currency: currentCurrency
            })
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
