// Upload functionality for receipt processing

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Dropzone
    if (document.getElementById('receipt-dropzone')) {
        initializeDropzone();
    }
    
    // Manual transaction form
    const manualForm = document.getElementById('manual-transaction-form');
    if (manualForm) {
        manualForm.addEventListener('submit', handleManualSubmit);
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
                    document.getElementById('category').value = response.transaction.category;
                    document.getElementById('description').value = response.transaction.description;
                    
                    // Show the extracted data
                    const extractedDataElement = document.getElementById('extracted-data');
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
                                    <dd class="col-sm-9">${formatCurrency(response.transaction.amount)}</dd>
                                    
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

async function handleManualSubmit(event) {
    event.preventDefault();
    
    const merchant = document.getElementById('merchant').value.trim();
    const amount = parseFloat(document.getElementById('amount').value);
    const category = document.getElementById('category').value;
    const description = document.getElementById('description').value.trim();
    
    // Validate input
    if (!merchant) {
        showError("Please enter a merchant name");
        return;
    }
    
    if (isNaN(amount) || amount <= 0) {
        showError("Please enter a valid amount");
        return;
    }
    
    if (!category) {
        showError("Please select a category");
        return;
    }
    
    // Create transaction object
    const transaction = {
        merchant,
        amount,
        category,
        description: description || `Purchase from ${merchant}`
    };
    
    try {
        showSpinner();
        
        const response = await fetch('/api/transactions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(transaction)
        });
        
        if (!response.ok) {
            throw new Error('Failed to add transaction');
        }
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess("Transaction added successfully!");
            // Clear the form
            document.getElementById('manual-transaction-form').reset();
            // Clear extracted data display
            document.getElementById('extracted-data').innerHTML = '';
        } else {
            showError(data.error || "Failed to add transaction");
        }
        
    } catch (error) {
        console.error('Error adding transaction:', error);
        showError('Failed to add transaction. Please try again.');
    } finally {
        hideSpinner();
    }
}
