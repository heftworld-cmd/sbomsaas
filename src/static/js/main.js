/**
 * Main JavaScript for Flask OAuth App
 * Common functionality shared across pages
 */

$(document).ready(function() {
    // Initialize common functionality
    initHoverEffects();
    initAlerts();
    initCopyFunctionality();
    initProfilePictures();
});

/**
 * Initialize profile picture error handling
 */
function initProfilePictures() {
    // Handle profile picture load errors
    $('img[alt="Profile"]').on('error', function() {
        const $img = $(this);
        const userName = $img.closest('.flex').find('h1, span, p').first().text().trim();
        const initial = userName ? userName.charAt(0).toUpperCase() : 'U';
        
        // Create fallback avatar
        const size = $img.hasClass('w-16') ? 'w-16 h-16 text-xl' : 'w-8 h-8 text-sm';
        const $fallback = $(`
            <div class="avatar-fallback rounded-full ${size}">
                ${initial}
            </div>
        `);
        
        $img.replaceWith($fallback);
    });
}

/**
 * Initialize hover effects for elements with hover-scale class
 */
function initHoverEffects() {
    $('.hover-scale').hover(
        function() { $(this).addClass('transform scale-105'); },
        function() { $(this).removeClass('transform scale-105'); }
    );
}

/**
 * Initialize alert handling
 */
function initAlerts() {
    // Show alerts if there are any in URL params
    const urlParams = new URLSearchParams(window.location.search);
    const error = urlParams.get('error');
    if (error) {
        showAlert('Error: ' + error, 'error');
    }

    // Handle alert close buttons
    $(document).on('click', '.alert .close-btn', function() {
        $(this).closest('.alert').fadeOut(300);
    });
}

/**
 * Initialize copy functionality for elements with copy-btn class
 */
function initCopyFunctionality() {
    $(document).on('click', '.copy-btn', function() {
        const targetId = $(this).data('target');
        let text = '';
        
        if (targetId) {
            text = $('#' + targetId).text().replace(/<br>/g, '\n');
        } else {
            // If no target, try to find the text in a sibling element
            text = $(this).closest('.code-block, .token-display').text();
        }
        
        copyToClipboard(text, $(this));
    });
}

/**
 * Show alert message to user
 * @param {string} message - The message to display
 * @param {string} type - Alert type: 'info', 'success', 'warning', 'error'
 */
function showAlert(message, type = 'info') {
    const alertClass = `alert alert-${type}`;
    const alertHtml = `
        <div class="${alertClass}" role="alert">
            <span class="block sm:inline">${message}</span>
            <span class="close-btn">&times;</span>
        </div>
    `;
    $('main').prepend(alertHtml);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        $('.alert').first().fadeOut(300);
    }, 5000);
}

/**
 * Copy text to clipboard and show feedback
 * @param {string} text - Text to copy
 * @param {jQuery} $button - Button element to show feedback on
 */
function copyToClipboard(text, $button) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            showCopyFeedback($button);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
            showAlert('Failed to copy to clipboard', 'error');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            showCopyFeedback($button);
        } catch (err) {
            console.error('Fallback copy failed: ', err);
            showAlert('Failed to copy to clipboard', 'error');
        }
        
        document.body.removeChild(textArea);
    }
}

/**
 * Show copy feedback on button
 * @param {jQuery} $button - Button to show feedback on
 */
function showCopyFeedback($button) {
    const originalText = $button.text();
    const originalClasses = $button.attr('class');
    
    $button.text('Copied!')
           .removeClass('btn-blue btn-gray')
           .addClass('btn-green');
    
    setTimeout(() => {
        $button.text(originalText)
               .attr('class', originalClasses);
    }, 2000);
}

/**
 * Get cookie value by name
 * @param {string} name - Cookie name
 * @returns {string|null} Cookie value or null if not found
 */
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

/**
 * Show loading state on button
 * @param {jQuery} $button - Button element
 * @returns {string} Original button text
 */
function showButtonLoading($button) {
    const originalText = $button.html();
    $button.html('<span class="loading-spinner">⟳</span> Loading...')
           .prop('disabled', true);
    return originalText;
}

/**
 * Restore button from loading state
 * @param {jQuery} $button - Button element
 * @param {string} originalText - Original button text to restore
 */
function hideButtonLoading($button, originalText) {
    $button.html(originalText)
           .prop('disabled', false);
}

/**
 * Make authenticated API call with Bearer token
 * @param {string} endpoint - API endpoint to call
 * @param {string} token - Bearer token for authentication
 * @param {Object} options - Additional options (method, data, etc.)
 * @returns {Promise} jQuery AJAX promise
 */
function makeAuthenticatedAPICall(endpoint, token, options = {}) {
    const defaultOptions = {
        url: endpoint,
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        }
    };
    
    return $.ajax($.extend({}, defaultOptions, options));
}

/**
 * Format JSON for display
 * @param {Object} data - Data to format
 * @returns {string} Formatted JSON string
 */
function formatJSON(data) {
    return JSON.stringify(data, null, 2);
}

/**
 * Smooth scroll to element
 * @param {string|jQuery} target - Target element selector or jQuery object
 */
function smoothScrollTo(target) {
    const $target = typeof target === 'string' ? $(target) : target;
    if ($target.length) {
        $('html, body').animate({
            scrollTop: $target.offset().top - 20
        }, 500);
    }
}
