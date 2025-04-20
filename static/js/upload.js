// Upload functionality for receipt processing

document.addEventListener('DOMContentLoaded', function() {
    // Manual transaction form first
    const manualForm = document.getElementById('manual-transaction-form');
    if (manualForm) {
        manualForm.addEventListener('submit', handleManualSubmit);
        console.log('[DEBUG] Manual transaction form event listener attached');
    } else {
        console.error('[ERROR] Manual transaction form not found!');
    }

    // Initialize Dropzone (wrapped to avoid blocking errors)
    const dropzoneEl = document.getElementById('receipt-dropzone');
    if (dropzoneEl) {
        try {
            // Prevent double initialization
            if (Dropzone.instances && Dropzone.instances.length > 0) {
                Dropzone.instances.forEach(instance => instance.destroy());
            }
            initializeDropzone();
            console.log('[DEBUG] Dropzone initialized successfully');
        } catch (error) {
            console.warn('[WARN] Dropzone initialization error:', error);
        }
    }

    // Currency select change handler
    const currencySelect = document.getElementById('currency');
    if (currencySelect) {
        currencySelect.addEventListener('change', updateCurrencySymbol);
        // Initialize currency symbol
        updateCurrencySymbol();
    }
});

function initializeDropzone() {
    // Initialize Dropzone.js
    Dropzone.autoDiscover = false;
    
    const myDropzone = new Dropzone("#receipt-dropzone", {
        url: "/api/process-receipt",
        paramName: "receipt",
        maxFilesize: 5, // MB
        acceptedFiles: "image/*",
        dictDefaultMessage: `
            <i class="feather-upload-cloud" style="font-size: 3rem;"></i>
            <p class="mt-2">Drag and drop receipt image or click to upload</p>
            <p class="text-muted small">Supported formats: JPG, PNG, etc.</p>
        `,
        autoProcessQueue: true,
        addRemoveLinks: true,
        dictRemoveFile: "Remove",
        init: function() {
            this.on("sending", function(file) {
                showSpinner();
            });
            
            this.on("success", function(file, response) {
                hideSpinner();
                
                if (response.success) {
                    showSuccess("Receipt processed successfully!");
                    
                    // Pre-fill the manual form with extracted data
                    document.getElementById('merchant').value = response.transaction.merchant;
                    document.getElementById('amount').value = response.transaction.amount;
                    if (response.transaction.currency) {
                        document.getElementById('currency').value = response.transaction.currency;
                        updateCurrencySymbol();
                    }
                    document.getElementById('category').value = response.transaction.category;
                    document.getElementById('description').value = response.transaction.description;
                    
                    // Auto-submit the manual transaction form after receipt processing
                    const manualForm = document.getElementById('manual-transaction-form');
                    if (manualForm) {
                        console.log('[DEBUG] Auto-submitting manual transaction form');
                        manualForm.requestSubmit();
                    }
                    
                    // Show the extracted data
                    const extractedDataElement = document.getElementById('extracted-data');
                    const currency = response.transaction.currency || currentCurrency;
                    
                    extractedDataElement.innerHTML = `
                        <div class="card mt-4">
                            <div class="card-header bg-primary text-white">
                                <strong>Extracted Receipt Data</strong>
                            </div>
                            <div class="card-body">
                                <dl class="row mb-0">
                                    <dt class="col-sm-3">Merchant:</dt>
                                    <dd class="col-sm-9">${response.transaction.merchant}</dd>
                                    
                                    <dt class="col-sm-3">Date:</dt>
                                    <dd class="col-sm-9">${response.transaction.date}</dd>
                                    
                                    <dt class="col-sm-3">Amount:</dt>
                                    <dd class="col-sm-9">${formatCurrency(response.transaction.amount, currency)}</dd>
                                    
                                    <dt class="col-sm-3">Currency:</dt>
                                    <dd class="col-sm-9">${currency}</dd>
                                    
                                    <dt class="col-sm-3">Category:</dt>
                                    <dd class="col-sm-9">${response.transaction.category}</dd>
                                </dl>
                            </div>
                        </div>
                        
                        <div class="card mt-3">
                            <div class="card-header bg-secondary text-white">
                                <strong>Raw Text</strong>
                            </div>
                            <div class="card-body">
                                <pre class="mb-0">${response.raw_text}</pre>
                            </div>
                        </div>
                    `;
                    
                    // Remove the file after processing
                    setTimeout(() => {
                        this.removeFile(file);
                    }, 3000);
                } else {
                    showError(response.error || "Failed to process receipt");
                    this.removeFile(file);
                }
            });
            
            this.on("error", function(file, errorMessage) {
                hideSpinner();
                showError(typeof errorMessage === 'string' ? errorMessage : "Failed to upload receipt");
                this.removeFile(file);
            });
        }
    });
}

// Update currency symbol based on selected currency
function updateCurrencySymbol() {
    const currencySelect = document.getElementById('currency');
    const currencySymbol = document.getElementById('currency-symbol');
    
    if (currencySelect && currencySymbol) {
        const selectedCurrency = currencySelect.value;
        currencySymbol.textContent = getCurrencySymbol(selectedCurrency);
    }
}

async function handleManualSubmit(event) {
    console.log('[DEBUG] handleManualSubmit triggered');
    event.preventDefault();
    
    const merchant = document.getElementById('merchant').value.trim();
    const amount = parseFloat(document.getElementById('amount').value);
    const currency = document.getElementById('currency').value;
    const category = document.getElementById('category').value;
    const description = document.getElementById('description').value.trim();
    
    // Validate input
    if (!merchant) {
        showError("Please enter a merchant name");
        console.error('[ERROR] Merchant name missing');
        return;
    }
    
    if (isNaN(amount) || amount <= 0) {
        showError("Please enter a valid amount");
        console.error('[ERROR] Amount invalid:', amount);
        return;
    }
    
    if (!category) {
        showError("Please select a category");
        console.error('[ERROR] Category missing');
        return;
    }
    
    // Create transaction object
    const transaction = {
        merchant,
        amount,
        currency,
        category,
        description: description || `Purchase from ${merchant}`
    };
    
    try {
        showSpinner();
        console.log('[DEBUG] Sending transaction:', transaction);
        
        const response = await fetch('/api/transactions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(transaction)
        });
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('[ERROR] Failed to add transaction:', errorText);
            showError('Failed to add transaction: ' + errorText);
            hideSpinner();
            return;
        }
        
        const data = await response.json();
        console.log('[DEBUG] Transaction saved, response:', data);
        
        if (data.success) {
            showSuccess("Transaction added successfully!");
            // Clear the form
            document.getElementById('manual-transaction-form').reset();
            // Reset currency to default
            document.getElementById('currency').value = currentCurrency;
            updateCurrencySymbol();
            // Clear extracted data display
            document.getElementById('extracted-data').innerHTML = '';
        } else {
            showError(data.error || "Failed to add transaction");
        }
        
    } catch (error) {
        showError(error.message || 'An error occurred');
        console.error('[ERROR] Exception in handleManualSubmit:', error);
    } finally {
        hideSpinner();
    }
}
