// Reports page functionality

document.addEventListener('DOMContentLoaded', function() {
    // AI Insights for Reports
    const askAIButton = document.getElementById('ask-report-ai-btn');
    if (askAIButton) {
        askAIButton.addEventListener('click', async function() {
            const questionInput = document.getElementById('report-ai-question');
            const aiResponseDiv = document.getElementById('report-ai-response');
            const question = questionInput.value.trim();
            if (!question) {
                showError('Please enter a question for the AI.');
                return;
            }
            try {
                showSpinner();
                const currency = localStorage.getItem('preferredCurrency') || 'USD';
                const response = await fetch('/api/analyze-finances', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question, currency })
                });
                if (!response.ok) {
                    throw new Error('Failed to analyze report');
                }
                const data = await response.json();
                if (data.success) {
                    aiResponseDiv.innerHTML = `
                        <div class="card my-3">
                            <div class="card-header bg-primary text-white">
                                <strong>AI Report Analysis</strong>
                            </div>
                            <div class="card-body">
                                <h5 class="card-title">${question}</h5>
                                <p class="card-text">${data.answer.replace(/\n/g, '<br>')}</p>
                            </div>
                        </div>
                    `;
                    questionInput.value = '';
                } else {
                    showError(data.error || 'AI failed to analyze report');
                }
            } catch (error) {
                showError('Failed to analyze report. Please try again later.');
                console.error('AI report analysis error:', error);
            } finally {
                hideSpinner();
            }
        });
    }
    loadReportData();
    
    // Setup period selector
    const periodSelector = document.getElementById('report-period');
    if (periodSelector) {
        periodSelector.addEventListener('change', loadReportData);
    }
    
    // Setup export buttons
    const exportJsonBtn = document.getElementById('export-json');
    const exportCsvBtn = document.getElementById('export-csv');
    
    if (exportJsonBtn) {
        exportJsonBtn.addEventListener('click', function() {
            exportData('json');
        });
    }
    
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', function() {
            exportData('csv');
        });
    }
});

async function loadReportData() {
    try {
        showSpinner();
        
        // Get all transactions in selected currency
        const currentCurrency = localStorage.getItem('preferredCurrency') || 'USD';
        const response = await fetch(`/api/transactions?currency=${currentCurrency}`);
        if (!response.ok) {
            throw new Error('Failed to fetch transactions');
        }
        
        const transactions = await response.json();
        
        // Filter by period if selected
        const period = document.getElementById('report-period').value;
        const filteredTransactions = filterTransactionsByPeriod(transactions, period);
        
        // Update transaction count
        document.getElementById('transaction-count').textContent = filteredTransactions.length;
        
        // Generate reports
        generateExpensesByCategory(filteredTransactions);
        generateMonthlyTrends(filteredTransactions);
        generateTopMerchants(filteredTransactions);
        generateTransactionSummary(filteredTransactions);
        
    } catch (error) {
        console.error('Error loading report data:', error);
        showError('Failed to load report data. Please try again.');
    } finally {
        hideSpinner();
    }
}

function filterTransactionsByPeriod(transactions, period) {
    if (!period || period === 'all') {
        return transactions;
    }
    
    const today = new Date();
    let cutoffDate = new Date();
    
    switch (period) {
        case 'week':
            cutoffDate.setDate(today.getDate() - 7);
            break;
        case 'month':
            cutoffDate.setMonth(today.getMonth() - 1);
            break;
        case 'quarter':
            cutoffDate.setMonth(today.getMonth() - 3);
            break;
        case 'year':
            cutoffDate.setFullYear(today.getFullYear() - 1);
            break;
    }
    
    return transactions.filter(transaction => {
        const transactionDate = new Date(transaction.date);
        return transactionDate >= cutoffDate;
    });
}

function generateExpensesByCategory(transactions) {
    // Group transactions by category
    const categoriesMap = {};
    
    transactions.forEach(transaction => {
        const category = transaction.category;
        if (categoriesMap[category]) {
            categoriesMap[category] += transaction.amount;
        } else {
            categoriesMap[category] = transaction.amount;
        }
    });
    
    // Convert to array and sort by amount
    const categories = Object.keys(categoriesMap)
        .map(category => ({
            category,
            amount: categoriesMap[category]
        }))
        .sort((a, b) => b.amount - a.amount);
    
    // Calculate total
    const total = categories.reduce((sum, category) => sum + category.amount, 0);
    
    // Render chart
    renderCategoryPieChart(categories);
    
    // Render table
    const tableBody = document.getElementById('category-breakdown-body');
    
    if (categories.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="3" class="text-center">No data available</td></tr>';
        return;
    }
    
    let tableHtml = '';
    
    categories.forEach(item => {
        const percentage = (item.amount / total * 100).toFixed(1);
        
        tableHtml += `
            <tr>
                <td>${item.category}</td>
                <td class="text-end">${formatCurrency(item.amount)}</td>
                <td class="text-end">${percentage}%</td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = tableHtml;
}

function renderCategoryPieChart(categories) {
    const ctx = document.getElementById('category-pie-chart').getContext('2d');
    
    // Check if chart already exists and destroy it
    if (window.categoryPieChart instanceof Chart) {
        window.categoryPieChart.destroy();
    }
    
    // Prepare data
    const labels = categories.map(item => item.category);
    const data = categories.map(item => item.amount);
    
    // Generate colors
    const colors = generateChartColors(categories.length);
    
    // Create chart
    window.categoryPieChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderColor: 'rgba(0, 0, 0, 0.1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: 'white',
                        padding: 10,
                        usePointStyle: true,
                        pointStyle: 'circle'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((acc, curr) => acc + curr, 0);
                            const percentage = Math.round((value / total) * 100);
                            return `${label}: ${formatCurrency(value)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

function generateMonthlyTrends(transactions) {
    // Group transactions by month
    const monthsMap = {};
    
    transactions.forEach(transaction => {
        const date = new Date(transaction.date);
        const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        
        if (monthsMap[monthKey]) {
            monthsMap[monthKey] += transaction.amount;
        } else {
            monthsMap[monthKey] = transaction.amount;
        }
    });
    
    // Convert to array and sort by month
    const monthKeys = Object.keys(monthsMap).sort();
    const months = monthKeys.map(month => ({
        month,
        amount: monthsMap[month]
    }));
    
    // Render chart
    renderMonthlyTrendChart(months);
}

function renderMonthlyTrendChart(months) {
    const ctx = document.getElementById('monthly-trend-chart').getContext('2d');
    
    // Check if chart already exists and destroy it
    if (window.monthlyTrendChart instanceof Chart) {
        window.monthlyTrendChart.destroy();
    }
    
    // Format labels (YYYY-MM to MMM YYYY)
    const labels = months.map(item => {
        const [year, month] = item.month.split('-');
        const date = new Date(parseInt(year), parseInt(month) - 1, 1);
        return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    });
    
    const data = months.map(item => item.amount);
    
    // Create chart
    window.monthlyTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Monthly Expenses',
                data: data,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Expenses: ${formatCurrency(context.raw)}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        },
                        color: 'white'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: 'white'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

function generateTopMerchants(transactions) {
    // Group transactions by merchant
    const merchantsMap = {};
    
    transactions.forEach(transaction => {
        const merchant = transaction.merchant;
        if (merchantsMap[merchant]) {
            merchantsMap[merchant] += transaction.amount;
        } else {
            merchantsMap[merchant] = transaction.amount;
        }
    });
    
    // Convert to array and sort by amount
    const merchants = Object.keys(merchantsMap)
        .map(merchant => ({
            merchant,
            amount: merchantsMap[merchant]
        }))
        .sort((a, b) => b.amount - a.amount)
        .slice(0, 10); // Get top 10
    
    // Render chart
    renderTopMerchantsChart(merchants);
}

function renderTopMerchantsChart(merchants) {
    const ctx = document.getElementById('top-merchants-chart').getContext('2d');
    
    // Check if chart already exists and destroy it
    if (window.topMerchantsChart instanceof Chart) {
        window.topMerchantsChart.destroy();
    }
    
    // Prepare data
    const labels = merchants.map(item => item.merchant);
    const data = merchants.map(item => item.amount);
    
    // Create chart
    window.topMerchantsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Spending by Merchant',
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Spent: ${formatCurrency(context.raw)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        },
                        color: 'white'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    ticks: {
                        color: 'white'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

function generateTransactionSummary(transactions) {
    // Calculate summary data
    const total = transactions.reduce((sum, tx) => sum + tx.amount, 0);
    const count = transactions.length;
    const average = count > 0 ? total / count : 0;
    
    // Find max and min transactions
    let maxTransaction = { amount: 0 };
    let minTransaction = { amount: Number.MAX_VALUE };
    
    transactions.forEach(tx => {
        if (tx.amount > maxTransaction.amount) {
            maxTransaction = tx;
        }
        if (tx.amount < minTransaction.amount) {
            minTransaction = tx;
        }
    });
    
    // Update UI
    document.getElementById('total-spent').textContent = formatCurrency(total);
    document.getElementById('average-transaction').textContent = formatCurrency(average);
    
    if (count > 0) {
        document.getElementById('largest-expense').innerHTML = `
            ${formatCurrency(maxTransaction.amount)} <small class="text-muted">at ${maxTransaction.merchant}</small>
        `;
        document.getElementById('smallest-expense').innerHTML = `
            ${formatCurrency(minTransaction.amount)} <small class="text-muted">at ${minTransaction.merchant}</small>
        `;
    } else {
        document.getElementById('largest-expense').textContent = formatCurrency(0);
        document.getElementById('smallest-expense').textContent = formatCurrency(0);
    }
}

// Utility function to generate chart colors (copied from dashboard.js)
function generateChartColors(count) {
    const colors = [
        'rgba(75, 192, 192, 0.8)',  // Teal
        'rgba(54, 162, 235, 0.8)',  // Blue
        'rgba(255, 159, 64, 0.8)',  // Orange
        'rgba(153, 102, 255, 0.8)', // Purple
        'rgba(255, 99, 132, 0.8)',  // Red
        'rgba(255, 205, 86, 0.8)',  // Yellow
        'rgba(201, 203, 207, 0.8)', // Gray
        'rgba(69, 161, 118, 0.8)',  // Green
        'rgba(162, 86, 178, 0.8)',  // Violet
        'rgba(235, 125, 52, 0.8)',  // Coral
        'rgba(99, 107, 252, 0.8)',  // Indigo
        'rgba(255, 180, 194, 0.8)'  // Pink
    ];
    
    // If we need more colors than predefined, generate them
    if (count > colors.length) {
        for (let i = colors.length; i < count; i++) {
            const r = Math.floor(Math.random() * 255);
            const g = Math.floor(Math.random() * 255);
            const b = Math.floor(Math.random() * 255);
            colors.push(`rgba(${r}, ${g}, ${b}, 0.8)`);
        }
    }
    
    return colors.slice(0, count);
}
