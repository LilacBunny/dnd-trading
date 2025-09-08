// Dashboard JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Enhanced table interactions
    const tableRows = document.querySelectorAll('.table-hover tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('click', function() {
            // Highlight selected row
            tableRows.forEach(r => r.classList.remove('table-active'));
            this.classList.add('table-active');
        });
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Add loading state to submit buttons
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                submitBtn.disabled = true;
                
                // Re-enable after 3 seconds in case of page reload issues
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 3000);
            }
        });
    });

    // Update last update timestamp
    const updateTimestamp = () => {
        const now = new Date();
        const timestamp = now.toLocaleString();
        const timestampElement = document.getElementById('last-update');
        if (timestampElement) {
            timestampElement.textContent = timestamp;
        }
    };

    // Update timestamp on page load
    updateTimestamp();

    // Alert auto-dismiss
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) {
            setTimeout(() => {
                alert.style.opacity = '0';
                alert.style.transition = 'opacity 0.5s ease';
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, 500);
            }, 5000);
        }
    });
});

// Utility functions
if (!window.DashboardUtils) {
    const formatCurrency = (amount, currency = 'gp') => {
        const formatted = parseFloat(amount).toFixed(2);
        return `${formatted} ${currency}`;
    };

    const calculatePercentageChange = (oldValue, newValue) => {
        if (oldValue === 0) return 0;
        return ((newValue - oldValue) / oldValue) * 100;
    };

    const addTrendIndicator = (element, change) => {
        element.classList.remove('text-success', 'text-danger', 'text-muted');
        
        if (change > 2) {
            element.classList.add('text-success');
            element.innerHTML = '<i class="fas fa-arrow-up"></i> Rising';
        } else if (change < -2) {
            element.classList.add('text-danger');
            element.innerHTML = '<i class="fas fa-arrow-down"></i> Falling';
        } else {
            element.classList.add('text-muted');
            element.innerHTML = '<i class="fas fa-minus"></i> Stable';
        }
    };

    // Export functions for use in other scripts
    window.DashboardUtils = {
        formatCurrency,
        calculatePercentageChange,
        addTrendIndicator
    };
}