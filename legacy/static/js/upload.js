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
            // Append user-selected currency to upload request and show spinner
            this.on("sending", function(file, xhr, formData) {
                showSpinner();
                const currencySelect = document.getElementById('currency');
                if (currencySelect) {
                    formData.append('currency', currencySelect.value);
                }
            });
            
            this.on("success", function(file, response) {
                console.log('[DEBUG] processReceipt response:', response);
                hideSpinner();
                
                if (response.success) {
                    showSuccess("Receipt processed successfully!");
                    
                    // Pre-fill the manual form with extracted data
                    document.getElementById('merchant').value = response.transaction.merchant;
                    document.getElementById('amount').value = response.transaction.amount;
                    // Always set currency from AI output, fallback to current selection
                    const currencySelect = document.getElementById('currency');
                    const serverCurrency = response.transaction.currency || currencySelect.value;
                    console.log('[DEBUG] Setting currency to', serverCurrency);
                    currencySelect.value = serverCurrency;
                    updateCurrencySymbol();
                    // Set category from AI output, fallback to 'Other'
                    const categorySelect = document.getElementById('category');
                    let serverCategory = response.transaction.category;
                    if (!serverCategory || ![...categorySelect.options].some(opt => opt.value === serverCategory)) {
                        serverCategory = 'Other';
                    }
                    console.log('[DEBUG] Setting category to', serverCategory);
                    categorySelect.value = serverCategory;
                    document.getElementById('description').value = response.transaction.description;
                    document.getElementById('date').value = response.transaction.date;
                    document.getElementById('shop_name').value = response.transaction.shop_name || '';
                    // Populate dynamic items editor
                    if (typeof populateExtractedItems === 'function') populateExtractedItems(response.transaction.items || []);
                    document.getElementById('tax').value = response.transaction.tax || '';
                    document.getElementById('payment_method').value = response.transaction.payment_method || '';
                    document.getElementById('receipt_number').value = response.transaction.receipt_number || '';
                    document.getElementById('address').value = response.transaction.address || '';
                    document.getElementById('phone_number').value = response.transaction.phone_number || '';
                    document.getElementById('notes').value = response.transaction.notes || '';
                    // Store raw OCR text into hidden form field
                    document.getElementById('receipt_data').value = response.transaction.receipt_data;
                    
                    // Show the extracted data
                    const extractedDataElement = document.getElementById('extracted-data');
                    // Use updated currency selection for display
                    const currency = document.getElementById('currency').value;
                    
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
                                    <dd class="col-sm-9">${categorySelect.value}</dd>
                                    
                                    <dt class="col-sm-3">Shop Name:</dt>
                                    <dd class="col-sm-9">${response.transaction.shop_name || ''}</dd>
                                    
                                    <dt class="col-sm-3">Items:</dt>
                                    <dd class="col-sm-9">${response.transaction.items.map(i =>
                                        i.name + ' (' + i.quantity + (currency ? ' ' + currency : '') +
                                        (i.price != null ? ' @ ' + formatCurrency(i.price, currency) : '') +
                                        ')'
                                    ).join(', ') || '<em>No items detected</em>'}</dd>
                                    
                                    <dt class="col-sm-3">Tax:</dt>
                                    <dd class="col-sm-9">${formatCurrency(response.transaction.tax || 0, currency)}</dd>
                                    
                                    <dt class="col-sm-3">Payment Method:</dt>
                                    <dd class="col-sm-9">${response.transaction.payment_method || ''}</dd>
                                    
                                    <dt class="col-sm-3">Receipt #:</dt>
                                    <dd class="col-sm-9">${response.transaction.receipt_number || ''}</dd>
                                    
                                    <dt class="col-sm-3">Address:</dt>
                                    <dd class="col-sm-9">${response.transaction.address || ''}</dd>
                                    
                                    <dt class="col-sm-3">Phone:</dt>
                                    <dd class="col-sm-9">${response.transaction.phone_number || ''}</dd>
                                    
                                    <dt class="col-sm-3">Notes:</dt>
                                    <dd class="col-sm-9">${response.transaction.notes || ''}</dd>
                                </dl>
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
        date: document.getElementById('date').value,
        merchant,
        amount,
        currency,
        category,
        description: description || `Purchase from ${merchant}`,
        receipt_data: document.getElementById('receipt_data').value,
        items: JSON.parse(document.getElementById('items').value || '[]'),
        shop_name: document.getElementById('shop_name').value,
        tax: parseFloat(document.getElementById('tax').value) || 0,
        payment_method: document.getElementById('payment_method').value,
        receipt_number: document.getElementById('receipt_number').value,
        address: document.getElementById('address').value,
        phone_number: document.getElementById('phone_number').value,
        notes: document.getElementById('notes').value
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

// Dynamic items editor
;(function() {
    const container = document.getElementById('items-container');
    const btn = document.getElementById('add-item-button');
    let list = [];

    function updateHidden() {
        document.getElementById('items').value = JSON.stringify(list);
    }
    function render() {
        container.innerHTML = '';
        list.forEach((item, idx) => {
            const row = document.createElement('div');
            row.className = 'input-group mb-2';
            row.innerHTML = `
                <input type="text" class="form-control me-1" placeholder="Name" value="${item.name}" data-index="${idx}" data-field="name">
                <input type="number" class="form-control me-1" placeholder="Quantity" value="${item.quantity}" step="0.01" min="0" data-index="${idx}" data-field="quantity">
                <input type="number" class="form-control me-1" placeholder="Price" value="${item.price}" step="0.01" min="0" data-index="${idx}" data-field="price">
                <button type="button" class="btn btn-outline-danger" data-index="${idx}">&times;</button>
            `;
            container.appendChild(row);
        });
        updateHidden();
    }

    container.addEventListener('input', e => {
        const idx = e.target.dataset.index;
        const field = e.target.dataset.field;
        list[idx][field] = e.target.value;
        updateHidden();
    });
    container.addEventListener('click', e => {
        if (e.target.matches('button[data-index]')) {
            const idx = e.target.dataset.index;
            list.splice(idx, 1);
            render();
        }
    });
    btn.addEventListener('click', () => {
        list.push({name:'',quantity:'',price:''});
        render();
    });
    window.populateExtractedItems = items => {
        list = items || [];
        render();
    };
})();
