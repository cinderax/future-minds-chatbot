/**
 * RAG Assistant - Main JavaScript File
 * This file contains common functionality used across the application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Toggle mobile sidebar functionality
    const toggleMobileNav = () => {
        const sidebar = document.querySelector('.sidebar');
        const content = document.querySelector('.content');
        
        if (window.innerWidth <= 768) {
            // Add mobile toggle button if it doesn't exist
            if (!document.getElementById('sidebar-toggle')) {
                const toggleBtn = document.createElement('button');
                toggleBtn.id = 'sidebar-toggle';
                toggleBtn.className = 'sidebar-toggle';
                toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
                
                document.querySelector('header').prepend(toggleBtn);
                
                toggleBtn.addEventListener('click', function() {
                    sidebar.classList.toggle('active');
                    content.classList.toggle('sidebar-open');
                });
                
                // Close sidebar when clicking outside
                document.addEventListener('click', function(e) {
                    if (!sidebar.contains(e.target) && e.target !== toggleBtn && sidebar.classList.contains('active')) {
                        sidebar.classList.remove('active');
                        content.classList.remove('sidebar-open');
                    }
                });
            }
        } else {
            // Remove toggle button on larger screens
            const toggleBtn = document.getElementById('sidebar-toggle');
            if (toggleBtn) {
                toggleBtn.remove();
            }
        }
    };
    
    // Initialize mobile nav
    toggleMobileNav();
    
    // Re-check on window resize
    window.addEventListener('resize', toggleMobileNav);

    // Initialize tooltips if function exists
    if (typeof initTooltips === 'function') {
        initTooltips();
    }
    
    // Add form input validation styling
    const formInputs = document.querySelectorAll('input, textarea, select');
    
    formInputs.forEach(input => {
        // Add validation styling on blur
        input.addEventListener('blur', function() {
            if (this.hasAttribute('required') && !this.value.trim()) {
                this.classList.add('invalid');
            } else {
                this.classList.remove('invalid');
            }
        });
        
        // Remove validation styling when input changes
        input.addEventListener('input', function() {
            if (this.classList.contains('invalid') && this.value.trim()) {
                this.classList.remove('invalid');
            }
        });
    });
    
    // Add smooth scrolling for all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                const target = document.querySelector(targetId);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // Handle form submission errors globally
    const handleFormError = (form, errorMessage) => {
        // Create error message element if it doesn't exist
        let errorElement = form.querySelector('.form-error');
        
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'form-error';
            form.prepend(errorElement);
        }
        
        errorElement.textContent = errorMessage;
        errorElement.style.display = 'block';
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 5000);
    };
    
    // Add error handling to all forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredInputs = form.querySelectorAll('[required]');
            let hasError = false;
            
            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('invalid');
                    hasError = true;
                }
            });
            
            if (hasError) {
                e.preventDefault();
                handleFormError(form, 'Please fill in all required fields.');
            }
        });
    });
    
    // Add CSS for dynamic elements
    const style = document.createElement('style');
    style.textContent = `
        .sidebar-toggle {
            background: transparent;
            border: none;
            color: var(--primary-color);
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0.5rem;
            display: none;
        }
        
        @media (max-width: 768px) {
            .sidebar-toggle {
                display: block;
            }
            
            .sidebar {
                transform: translateX(-100%);
                transition: transform 0.3s ease;
            }
            
            .sidebar.active {
                transform: translateX(0);
            }
            
            .content {
                margin-left: 0;
                transition: margin-left 0.3s ease;
            }
            
            .content.sidebar-open {
                margin-left: 60px;
            }
        }
        
        .form-error {
            background-color: var(--danger-color);
            color: white;
            padding: 0.75rem;
            border-radius: var(--border-radius);
            margin-bottom: 1rem;
            display: none;
        }
        
        input.invalid, textarea.invalid, select.invalid {
            border-color: var(--danger-color);
            box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.25);
        }
        
        .tooltip {
            position: relative;
            display: inline-block;
        }
        
        .tooltip .tooltip-text {
            visibility: hidden;
            width: 120px;
            background-color: var(--dark-color);
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -60px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .tooltip .tooltip-text::after {
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: var(--dark-color) transparent transparent transparent;
        }
        
        .tooltip:hover .tooltip-text {
            visibility: visible;
            opacity: 1;
        }
    `;
    
    document.head.appendChild(style);
});

/**
 * Initialize tooltips for elements with data-tooltip attribute
 */
function initTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        const tooltipText = element.getAttribute('data-tooltip');
        
        // Make the element a tooltip container
        element.classList.add('tooltip');
        
        // Create tooltip text element
        const tooltip = document.createElement('span');
        tooltip.className = 'tooltip-text';
        tooltip.textContent = tooltipText;
        
        // Add to element
        element.appendChild(tooltip);
    });
}

/**
 * Format date to a readable format
 * @param {string} dateString - Date string in any valid format
 * @param {boolean} includeTime - Whether to include time in the result
 * @returns {string} Formatted date string
 */
function formatDate(dateString, includeTime = false) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    if (isNaN(date)) return dateString;
    
    const options = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    
    if (includeTime) {
        options.hour = '2-digit';
        options.minute = '2-digit';
    }
    
    return date.toLocaleDateString('en-US', options);
}

/**
 * Truncate text to a specific length and add ellipsis
 * @param {string} text - The text to truncate
 * @param {number} maxLength - Maximum length before truncation
 * @returns {string} Truncated text with ellipsis if needed
 */
function truncateText(text, maxLength = 100) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

/**
 * Debounce function to limit how often a function is called
 * @param {Function} func - The function to debounce
 * @param {number} wait - Time in milliseconds to wait
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 300) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            func.apply(this, args);
        }, wait);
    };
}