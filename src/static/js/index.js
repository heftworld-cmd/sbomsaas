/**
 * Index Page JavaScript
 * Handles home page functionality and API testing
 */

$(document).ready(function() {
    initIndexPage();
});

function initIndexPage() {
    // Only initialize API test if user is logged in
    if (typeof window.userLoggedIn !== 'undefined' && window.userLoggedIn) {
        initAPITest();
    }
}

/**
 * Initialize API test functionality for logged-in users
 */
function initAPITest() {
    $('#testApiBtn').click(function() {
        testAPIFromBrowser();
    });
}

/**
 * Test API from browser using cookie authentication
 */
function testAPIFromBrowser() {
    const $button = $('#testApiBtn');
    const originalText = showButtonLoading($button);
    
    // Try to get token from cookie first
    const token = getCookie('auth_token');
    
    if (token) {
        makeAuthenticatedAPICall('/api/profile', token)
            .then(data => {
                displayBrowserAPIResult(formatJSON(data));
            })
            .catch(xhr => {
                handleBrowserAPIError(xhr);
            })
            .finally(() => {
                hideButtonLoading($button, originalText);
            });
    } else {
        // Fallback: try direct API call (might work with session)
        $.ajax({
            url: '/api/profile',
            method: 'GET',
            success: function(data) {
                displayBrowserAPIResult(formatJSON(data));
            },
            error: function(xhr) {
                handleBrowserAPIError(xhr);
            },
            complete: function() {
                hideButtonLoading($button, originalText);
            }
        });
    }
}

/**
 * Display API result in browser test section
 * @param {string} resultText - Formatted result text
 */
function displayBrowserAPIResult(resultText) {
    $('#apiResult pre').text(resultText);
    $('#apiResult').removeClass('hidden');
}

/**
 * Handle browser API test errors
 * @param {Object} xhr - jQuery XHR object
 */
function handleBrowserAPIError(xhr) {
    let errorMsg = 'Unknown error';
    
    try {
        const errorData = JSON.parse(xhr.responseText);
        errorMsg = errorData.message || errorData.error || xhr.responseText;
    } catch (e) {
        errorMsg = xhr.responseText || `HTTP ${xhr.status}`;
    }
    
    displayBrowserAPIResult(`Error: ${errorMsg}`);
    showAlert('No authentication token found', 'error');
}
