// Main JavaScript functionality for Security Checker

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    const scanForm = document.getElementById('scanForm');
    const urlInput = document.getElementById('urlInput');
    const scanButton = document.getElementById('scanButton');
    const aiCheckbox = document.getElementById('ai-checkbox');
    const openaiKeyContainer = document.getElementById('openai-key-container');
    const openaiKeyInput = document.getElementById('openai-key-input');
    
    if (aiCheckbox && openaiKeyContainer) {
        aiCheckbox.addEventListener('change', function() {
            if (aiCheckbox.checked) {
                openaiKeyContainer.style.display = 'block';
            } else {
                openaiKeyContainer.style.display = 'none';
                if (openaiKeyInput) openaiKeyInput.value = '';
                sessionStorage.removeItem('openai_api_key');
            }
        });
        // On page load, show/hide based on checkbox
        if (aiCheckbox.checked) {
            openaiKeyContainer.style.display = 'block';
        }
    }
    
    if (scanForm) {
        setupFormSubmission(scanForm, urlInput, scanButton, aiCheckbox, openaiKeyInput);
    }
    
    setupScoreCircle();
    setupResponsiveFeatures();
}

function setupFormSubmission(form, input, button, aiCheckbox, openaiKeyInput) {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const url = input.value.trim();
        if (!url) {
            showAlert('Please enter a website URL', 'error');
            return;
        }
        
        if (!isValidUrl(url)) {
            showAlert('Please enter a valid URL (e.g., example.com or https://example.com)', 'error');
            return;
        }
        
        // AI key logic
        let includeAI = aiCheckbox && aiCheckbox.checked;
        let openaiKey = '';
        
        if (includeAI) {
            if (openaiKeyInput) {
                openaiKey = openaiKeyInput.value.trim();
            }
            if (!openaiKey) {
                showAlert('Please enter your OpenAI API key for AI-powered recommendations.', 'error');
                return;
            }
            sessionStorage.setItem('openai_api_key', openaiKey);
        } else {
            sessionStorage.removeItem('openai_api_key');
        }
        
        startScan(url, button, includeAI, openaiKey);
    });
    
    // Real-time URL validation
    input.addEventListener('input', function() {
        validateUrlInput(input);
    });
    
    // Auto-add https:// if missing
    input.addEventListener('blur', function() {
        const url = input.value.trim();
        if (url && !url.startsWith('http://') && !url.startsWith('https://')) {
            input.value = 'https://' + url;
        }
    });
}

function isValidUrl(string) {
    try {
        // Add protocol if missing
        const urlString = string.startsWith('http') ? string : 'https://' + string;
        const url = new URL(urlString);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch (_) {
        return false;
    }
}

function validateUrlInput(input) {
    const url = input.value.trim();
    
    if (url && !isValidUrl(url)) {
        input.style.borderColor = '#dc3545';
        input.style.boxShadow = '0 0 0 3px rgba(220, 53, 69, 0.1)';
    } else {
        input.style.borderColor = '#e1e5e9';
        input.style.boxShadow = 'none';
    }
}

function startScan(url, button, includeAI, openaiKey) {
    // Show loading state
    setLoadingState(button, true);
    
    // Prepare form data
    const formData = new FormData();
    formData.append('url', url);
    
    // Only include AI parameters if AI is enabled and key is provided
    if (includeAI && openaiKey) {
        formData.append('include_ai', '1');
        formData.append('openai_api_key', openaiKey);
    }
    
    fetch('/analyze', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.text();
    })
    .then(html => {
        // Replace current page content with results
        document.documentElement.innerHTML = html;
        
        // Re-initialize features for the new page
        setupScoreCircle();
        
        // Scroll to top
        window.scrollTo(0, 0);
    })
    .catch(error => {
        console.error('Scan failed:', error);
        showAlert('Scan failed: ' + error.message, 'error');
        setLoadingState(button, false);
    });
}

function setLoadingState(button, isLoading) {
    const buttonText = button.querySelector('.button-text');
    const loadingSpinner = button.querySelector('.loading-spinner');
    
    if (isLoading) {
        button.classList.add('loading');
        button.disabled = true;
        buttonText.style.display = 'none';
        loadingSpinner.style.display = 'inline-block';
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
    } else {
        button.classList.remove('loading');
        button.disabled = false;
        if (buttonText) buttonText.style.display = 'inline';
        if (loadingSpinner) loadingSpinner.style.display = 'none';
    }
}

function setupScoreCircle() {
    const scoreCircles = document.querySelectorAll('.score-circle');
    
    scoreCircles.forEach(circle => {
        const score = parseFloat(circle.dataset.score);
        animateScoreCircle(circle, score);
    });
}

function animateScoreCircle(circle, score) {
    // Calculate the percentage for the circle progress
    const percentage = (score / 10) * 100;
    
    // Create a dynamic border color based on score
    let borderColor;
    if (score >= 8) {
        borderColor = '#28a745'; // Green
    } else if (score >= 6) {
        borderColor = '#ffc107'; // Yellow
    } else if (score >= 4) {
        borderColor = '#fd7e14'; // Orange
    } else {
        borderColor = '#dc3545'; // Red
    }
    
    // Animate the border color change
    circle.style.transition = 'border-color 1s ease-in-out';
    circle.style.borderColor = borderColor;
    
    // Add a subtle animation effect
    setTimeout(() => {
        circle.style.transform = 'scale(1.05)';
        setTimeout(() => {
            circle.style.transform = 'scale(1)';
        }, 200);
    }, 500);
}

function showAlert(message, type = 'info') {
    const alertsContainer = document.querySelector('.alerts') || createAlertsContainer();
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)}"></i>
        ${message}
    `;
    
    alertsContainer.appendChild(alert);
    
    // Auto-remove alert after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
    
    // Scroll to alert
    alert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function createAlertsContainer() {
    const container = document.createElement('div');
    container.className = 'alerts';
    
    const main = document.querySelector('.main .container');
    if (main && main.firstChild) {
        main.insertBefore(container, main.firstChild);
    }
    
    return container;
}

function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle',
        'error': 'exclamation-triangle',
        'warning': 'exclamation-triangle',
        'info': 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function setupResponsiveFeatures() {
    // Handle mobile menu if needed
    setupMobileOptimizations();
    
    // Handle window resize
    window.addEventListener('resize', debounce(handleResize, 250));
}

function setupMobileOptimizations() {
    // Optimize touch interactions for mobile
    const buttons = document.querySelectorAll('button, .btn');
    
    buttons.forEach(button => {
        button.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.95)';
        });
        
        button.addEventListener('touchend', function() {
            this.style.transform = '';
        });
    });
    
    // Improve form experience on mobile
    const urlInput = document.getElementById('urlInput');
    if (urlInput && isMobileDevice()) {
        urlInput.setAttribute('autocomplete', 'url');
        urlInput.setAttribute('autocorrect', 'off');
        urlInput.setAttribute('autocapitalize', 'off');
        urlInput.setAttribute('spellcheck', 'false');
    }
}

function handleResize() {
    // Handle any responsive adjustments needed
    const isMobile = window.innerWidth <= 768;
    
    // Adjust layout for mobile if needed
    if (isMobile) {
        document.body.classList.add('mobile-view');
    } else {
        document.body.classList.remove('mobile-view');
    }
}

function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

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

// API Analysis Functions
function analyzeWithAPI(url) {
    return fetch('/api/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        return data;
    });
}

// Utility Functions
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString();
}

function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text);
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            showAlert('Copied to clipboard!', 'success');
        } catch (err) {
            showAlert('Failed to copy to clipboard', 'error');
        }
        
        document.body.removeChild(textArea);
    }
}

// Demo URL functions
function fillUrl(url) {
    const urlInput = document.getElementById('urlInput');
    if (urlInput) {
        urlInput.value = url;
        urlInput.focus();
        validateUrlInput(urlInput);
    }
}

// Initialize tooltips if needed
function initializeTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const element = event.target;
    const tooltipText = element.getAttribute('data-tooltip');
    
    if (!tooltipText) return;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = tooltipText;
    tooltip.id = 'current-tooltip';
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
}

function hideTooltip() {
    const tooltip = document.getElementById('current-tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Performance monitoring
function trackPageLoad() {
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(function() {
                const perfData = window.performance.timing;
                const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
                console.log('Page load time:', pageLoadTime + 'ms');
            }, 0);
        });
    }
}

// Initialize performance tracking
trackPageLoad();