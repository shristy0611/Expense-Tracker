// Transactions page functionality

document.addEventListener('DOMContentLoaded', function() {
    loadTransactions();
    
    // Set up search functionality
    const searchInput = document.getElementById('search-transactions');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(function() {
            loadTransactions();
        }, 300));
    }
    
    // Set up category filter
    const categoryFilter = document.getElementById('category-filter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            loadTransactions();
        });
        
        // Load categories
        loadCategories();
    }
});

// Debounce function to prevent excessive API calls
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            func.apply(context, args);
        }, wait);
    };
}

async function loadCategories() {
    try {
        const categories = await fetchCategories();
        
        const categoryFilter = document.getElementById('category-filter');
        
        // Add "All Categories" option
        let options = '<option value="">All Categories</option>';
        
        // Add each category
        categories.forEach(category => {
            options += `<option value="${category}">${category}</option>`;
        });
        
        categoryFilter.innerHTML = options;
        
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function loadTransactions() {
    try {
        showSpinner();
        
        // Get search and filter values
        const searchTerm = document.getElementById('search-transactions').value.trim();
        const categoryFilter = document.getElementById('category-filter').value;
        
        // Build query parameters including currency
        const params = new URLSearchParams();
        if (searchTerm) params.append('search', searchTerm);
        if (categoryFilter) params.append('category', categoryFilter);
        params.append('currency', currentCurrency);
        const url = `/api/transactions?${params.toString()}`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error('Failed to fetch transactions');
        }
        
        const transactions = await response.json();
        renderTransactions(transactions);
        
    } catch (error) {
        console.error('Error loading transactions:', error);
        showError('Failed to load transactions. Please try again.');
    } finally {
        hideSpinner();
    }
}

function renderTransactions(transactions) {
    const tableBody = document.getElementById('transactions-table-body');
    const noTransactionsMessage = document.getElementById('no-transactions-message');
    
    if (transactions.length === 0) {
        tableBody.innerHTML = '';
        noTransactionsMessage.classList.remove('d-none');
        return;
    }
    
    noTransactionsMessage.classList.add('d-none');
    
    // Sort transactions by date (newest first)
    transactions.sort((a, b) => new Date(b.date) - new Date(a.date));
    
    let tableHtml = '';
    
    transactions.forEach(transaction => {
        tableHtml += `
            <tr data-id="${transaction.id}">
                <td>${formatDate(transaction.date)}</td>
                <td>${transaction.merchant}</td>
                <td>${transaction.category}</td>
                <td>${transaction.description}</td>
                <td class="text-end">${formatCurrency(transaction.amount)}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-primary edit-transaction" 
                            data-bs-toggle="modal" 
                            data-bs-target="#edit-transaction-modal"
                            onclick="prepareEditModal(${transaction.id})">
                        <i class="feather-edit-2"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger delete-transaction"
                            onclick="confirmDelete(${transaction.id})">
                        <i class="feather-trash-2"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = tableHtml;
}

async function prepareEditModal(transactionId) {
    try {
        showSpinner();
        
        const response = await fetch(`/api/transactions`);
        if (!response.ok) {
            throw new Error('Failed to fetch transactions');
        }
        
        const transactions = await response.json();
        const transaction = transactions.find(t => t.id === transactionId);
        
        if (!transaction) {
            throw new Error('Transaction not found');
        }
        
        // Populate modal form
        document.getElementById('edit-transaction-id').value = transaction.id;
        document.getElementById('edit-merchant').value = transaction.merchant;
        document.getElementById('edit-amount').value = transaction.amount;
        document.getElementById('edit-category').value = transaction.category;
        document.getElementById('edit-description').value = transaction.description;
        
    } catch (error) {
        console.error('Error preparing edit modal:', error);
        showError('Failed to load transaction details. Please try again.');
    } finally {
        hideSpinner();
    }
}

async function saveTransaction() {
    try {
        const transactionId = parseInt(document.getElementById('edit-transaction-id').value);
        const merchant = document.getElementById('edit-merchant').value.trim();
        const amount = parseFloat(document.getElementById('edit-amount').value);
        const category = document.getElementById('edit-category').value;
        const description = document.getElementById('edit-description').value.trim();
        
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
        
        showSpinner();
        
        // Update transaction
        const response = await fetch(`/api/transactions/${transactionId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                merchant,
                amount,
                category,
                description
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update transaction');
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('edit-transaction-modal'));
            modal.hide();
            
            showSuccess("Transaction updated successfully!");
            
            // Reload transactions
            loadTransactions();
        } else {
            showError(data.error || "Failed to update transaction");
        }
        
    } catch (error) {
        console.error('Error updating transaction:', error);
        showError('Failed to update transaction. Please try again.');
    } finally {
        hideSpinner();
    }
}

function confirmDelete(transactionId) {
    if (confirm("Are you sure you want to delete this transaction?")) {
        deleteTransaction(transactionId);
    }
}

async function deleteTransaction(transactionId) {
    try {
        showSpinner();
        
        const response = await fetch(`/api/transactions/${transactionId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error('Failed to delete transaction');
        }
        
        const data = await response.json();
        
        if (data.success) {
            showSuccess("Transaction deleted successfully!");
            
            // Remove the row from the table
            const row = document.querySelector(`tr[data-id="${transactionId}"]`);
            if (row) {
                row.remove();
            }
            
            // Check if the table is now empty
            const tableBody = document.getElementById('transactions-table-body');
            if (tableBody.children.length === 0) {
                document.getElementById('no-transactions-message').classList.remove('d-none');
            }
        } else {
            showError(data.error || "Failed to delete transaction");
        }
        
    } catch (error) {
        console.error('Error deleting transaction:', error);
        showError('Failed to delete transaction. Please try again.');
    } finally {
        hideSpinner();
    }
}
