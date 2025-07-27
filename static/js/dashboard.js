/**
 * Dashboard JavaScript
 * Handles dashboard-specific functionality
 */

$(document).ready(function() {
    initDashboard();
});

function initDashboard() {
    // Get auth token from template or API
    let authToken = typeof window.authToken !== 'undefined' ? window.authToken : '';
    
    // Initialize event listeners
    initAPIButtons(authToken);
    initResultsHandling();
}

/**
 * Initialize API button event listeners
 * @param {string} authToken - Authentication token
 */
function initAPIButtons(authToken) {
    $('#loadProfileBtn').click(function() {
        makeAPICall('/api/profile', 'loadProfileBtn', authToken);
    });

    $('#loadDataBtn').click(function() {
        makeAPICall('/api/data', 'loadDataBtn', authToken);
    });

    $('#testProtectedBtn').click(function() {
        makeAPICall('/api/protected', 'testProtectedBtn', authToken);
    });
}

/**
 * Initialize results handling
 */
function initResultsHandling() {
    $('#clearResults').click(function() {
        $('#apiResults').addClass('hidden');
        $('#apiOutput').text('');
    });
}

/**
 * Get authentication token (fallback method)
 * @returns {Promise<string>} Authentication token
 */
function getAuthToken() {
    return new Promise((resolve, reject) => {
        // First try to get from global variable
        if (typeof window.authToken !== 'undefined' && window.authToken) {
            resolve(window.authToken);
            return;
        }
        
        // Fallback: get token via API
        $.ajax({
            url: '/api/get-auth-token',
            method: 'GET',
            success: function(data) {
                window.authToken = data.token;
                resolve(data.token);
            },
            error: function(xhr) {
                reject('Failed to get auth token');
            }
        });
    });
}

/**
 * Make API call with Bearer token authentication
 * @param {string} endpoint - API endpoint to call
 * @param {string} buttonId - ID of the button that triggered the call
 * @param {string} token - Optional pre-existing token
 */
function makeAPICall(endpoint, buttonId, token = null) {
    const $button = $('#' + buttonId);
    
    // Show loading state
    const originalText = showButtonLoading($button);

    // Get token if not provided
    const tokenPromise = token ? Promise.resolve(token) : getAuthToken();

    tokenPromise.then(authToken => {
        if (!authToken) {
            showAlert('No authentication token found', 'error');
            return;
        }

        return makeAuthenticatedAPICall(endpoint, authToken);
    }).then(data => {
        if (data) {
            displayAPIResult(formatJSON(data));
        }
    }).catch(error => {
        handleAPIError(error);
    }).finally(() => {
        hideButtonLoading($button, originalText);
    });
}

/**
 * Display API result in the results section
 * @param {string} resultText - Formatted result text to display
 */
function displayAPIResult(resultText) {
    $('#apiOutput').text(resultText);
    $('#apiResults').removeClass('hidden');
    smoothScrollTo('#apiResults');
}

/**
 * Handle API call errors
 * @param {Object} xhr - jQuery XHR object or error
 */
function handleAPIError(xhr) {
    let errorMsg = 'Unknown error';
    
    if (typeof xhr === 'string') {
        errorMsg = xhr;
    } else if (xhr.responseText) {
        try {
            const errorData = JSON.parse(xhr.responseText);
            errorMsg = errorData.message || errorData.error || xhr.responseText;
        } catch (e) {
            errorMsg = xhr.responseText || `HTTP ${xhr.status}`;
        }
    }
    
    const errorText = `Error${xhr.status ? ` (${xhr.status})` : ''}: ${errorMsg}`;
    displayAPIResult(errorText);
    showAlert(`API Error: ${errorMsg}`, 'error');
}
