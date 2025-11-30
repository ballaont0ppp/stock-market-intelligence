/**
 * Main JavaScript file for Stock Portfolio Platform
 * Handles common client-side functionality
 */

(function() {
    'use strict';

    // Initialize Lucide icons
    function initIcons() {
        if (typeof lucide !== 'undefined') {
            lucide.createIcons();
        }
    }

    // Auto-dismiss flash messages after 5 seconds
    function initFlashMessages() {
        const flashMessages = document.querySelectorAll('.alert:not(.alert-permanent)');
        
        flashMessages.forEach(function(message) {
            // Add close button if not present
            if (!message.querySelector('.btn-close')) {
                const closeBtn = document.createElement('button');
                closeBtn.type = 'button';
                closeBtn.className = 'btn-close';
                closeBtn.setAttribute('data-bs-dismiss', 'alert');
                closeBtn.setAttribute('aria-label', 'Close');
                message.appendChild(closeBtn);
            }
            
            // Auto-dismiss after 5 seconds
            setTimeout(function() {
                const bsAlert = new bootstrap.Alert(message);
                bsAlert.close();
            }, 5000);
        });
    }

    // Notification dropdown toggle
    function initNotificationDropdown() {
        const notificationBtn = document.getElementById('notificationDropdown');
        const notificationMenu = document.getElementById('notificationMenu');
        
        if (notificationBtn && notificationMenu) {
            notificationBtn.addEventListener('click', function(e) {
                e.preventDefault();
                notificationMenu.classList.toggle('show');
            });
            
            // Close dropdown when clicking outside
            document.addEventListener('click', function(e) {
                if (!notificationBtn.contains(e.target) && !notificationMenu.contains(e.target)) {
                    notificationMenu.classList.remove('show');
                }
            });
        }
    }

    // Mobile sidebar toggle
    function initMobileSidebar() {
        const menuToggle = document.querySelector('.topbar-menu-toggle');
        const sidebar = document.querySelector('.sidebar');
        const overlay = document.querySelector('.sidebar-overlay');
        
        if (menuToggle && sidebar) {
            menuToggle.addEventListener('click', function() {
                sidebar.classList.toggle('open');
                if (overlay) {
                    overlay.classList.toggle('open');
                }
            });
            
            if (overlay) {
                overlay.addEventListener('click', function() {
                    sidebar.classList.remove('open');
                    overlay.classList.remove('open');
                });
            }
        }
    }

    // Form validation helper
    function initFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        
        Array.from(forms).forEach(function(form) {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    }

    // Number formatting helper
    function formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    }

    // Percentage formatting helper
    function formatPercentage(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'percent',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value / 100);
    }

    // Debounce helper for search inputs
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Confirm dialog helper
    function confirmAction(message, callback) {
        if (confirm(message)) {
            callback();
        }
    }

    // Copy to clipboard helper
    function copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(function() {
                showToast('Copied to clipboard!', 'success');
            }).catch(function(err) {
                console.error('Failed to copy:', err);
            });
        }
    }

    // Simple toast notification
    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} position-fixed top-0 end-0 m-3`;
        toast.style.zIndex = '9999';
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(function() {
            toast.remove();
        }, 3000);
    }

    // Table sorting helper
    function initTableSorting() {
        const sortableTables = document.querySelectorAll('table.sortable');
        
        sortableTables.forEach(function(table) {
            const headers = table.querySelectorAll('th[data-sortable]');
            
            headers.forEach(function(header, index) {
                header.style.cursor = 'pointer';
                header.addEventListener('click', function() {
                    sortTable(table, index);
                });
            });
        });
    }

    function sortTable(table, columnIndex) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const isAscending = table.dataset.sortOrder !== 'asc';
        
        rows.sort(function(a, b) {
            const aValue = a.cells[columnIndex].textContent.trim();
            const bValue = b.cells[columnIndex].textContent.trim();
            
            // Try to parse as number
            const aNum = parseFloat(aValue.replace(/[$,]/g, ''));
            const bNum = parseFloat(bValue.replace(/[$,]/g, ''));
            
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return isAscending ? aNum - bNum : bNum - aNum;
            }
            
            // String comparison
            return isAscending ? 
                aValue.localeCompare(bValue) : 
                bValue.localeCompare(aValue);
        });
        
        rows.forEach(function(row) {
            tbody.appendChild(row);
        });
        
        table.dataset.sortOrder = isAscending ? 'asc' : 'desc';
    }

    // Initialize Chart.js defaults
    function initChartDefaults() {
        if (typeof Chart !== 'undefined') {
            Chart.defaults.font.family = "'Inter', sans-serif";
            Chart.defaults.color = '#64748b';
            Chart.defaults.plugins.legend.display = true;
            Chart.defaults.plugins.legend.position = 'bottom';
        }
    }

    // Initialize all functionality on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        initIcons();
        initFlashMessages();
        initNotificationDropdown();
        initMobileSidebar();
        initFormValidation();
        initTableSorting();
        initChartDefaults();
    });

    // Expose utilities globally
    window.StockPortfolio = {
        formatCurrency: formatCurrency,
        formatPercentage: formatPercentage,
        debounce: debounce,
        confirmAction: confirmAction,
        copyToClipboard: copyToClipboard,
        showToast: showToast
    };

})();
