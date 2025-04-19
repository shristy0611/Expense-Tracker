// Dashboard-specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    
    // Setup AI question form
    const askButton = document.getElementById('ask-button');
    if (askButton) {
        askButton.addEventListener('click', askAIQuestion);
    }
    
    const questionInput = document.getElementById('ai-question');
    if (questionInput) {
        questionInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                askAIQuestion();
            }
        });
    }
});

async function loadDashboardData() {
    try {
        showSpinner();
        
        const response = await fetch('/api/dashboard-data');
        if (!response.ok) {
            throw new Error('Failed to fetch dashboard data');
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Update total expenses
            document.getElementById('total-expenses').textContent = formatCurrency(data.total_expenses);
            
            // Render expense by category chart
            renderCategoryChart(data.expenses_by_category);
            
            // Render monthly expense chart
            renderMonthlyChart(data.expenses_by_month);
            
            // Render recent transactions
            renderRecentTransactions(data.recent_transactions);
            
            // Render top merchants
            renderTopMerchants(data.top_merchants);
        } else {
            showError(data.error || 'Failed to load dashboard data');
        }
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showError('Failed to load dashboard data. Please refresh the page.');
    } finally {
        hideSpinner();
    }
}

function renderCategoryChart(expensesByCategory) {
    const ctx = document.getElementById('category-chart').getContext('2d');
    
    // Convert data for Chart.js
    const labels = Object.keys(expensesByCategory);
    const values = Object.values(expensesByCategory);
    
    // Generate colors
    const colors = generateChartColors(labels.length);
    
    // Create chart
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
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

function renderMonthlyChart(expensesByMonth) {
    const ctx = document.getElementById('monthly-chart').getContext('2d');
    
    // Sort months chronologically
    const sortedMonths = Object.keys(expensesByMonth).sort();
    const values = sortedMonths.map(month => expensesByMonth[month]);
    
    // Format month labels (YYYY-MM to MMM YYYY)
    const labels = sortedMonths.map(month => {
        const [year, monthNum] = month.split('-');
        const date = new Date(parseInt(year), parseInt(monthNum) - 1, 1);
        return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
    });
    
    // Create chart
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Monthly Expenses',
                data: values,
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
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

function renderRecentTransactions(transactions) {
    const container = document.getElementById('recent-transactions');
    
    if (transactions.length === 0) {
        container.innerHTML = '<div class="text-center p-3">No transactions found</div>';
        return;
    }
    
    let html = '';
    
    transactions.forEach(transaction => {
        html += `
            <div class="card mb-2">
                <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-0">${transaction.merchant}</h6>
                            <small class="text-muted">${formatDate(transaction.date)} · ${transaction.category}</small>
                        </div>
                        <div class="text-end">
                            <h6 class="mb-0">${formatCurrency(transaction.amount)}</h6>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function renderTopMerchants(merchants) {
    const container = document.getElementById('top-merchants');
    
    if (merchants.length === 0) {
        container.innerHTML = '<div class="text-center p-3">No merchant data available</div>';
        return;
    }
    
    let html = '';
    
    merchants.forEach(merchant => {
        html += `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div>${merchant.name}</div>
                <div><strong>${formatCurrency(merchant.amount)}</strong></div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

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
