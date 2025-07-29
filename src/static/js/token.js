/**
 * Token Page JavaScript
 * Handles token display and API testing functionality
 */

$(document).ready(function() {
    initTokenPage();
});

function initTokenPage() {
    // Get token from global variable (set by template)
    const token = typeof window.pageToken !== 'undefined' ? window.pageToken : '';
    
    if (token) {
        initTokenFunctionality(token);
    }
}

/**
 * Initialize token page functionality
 * @param {string} token - JWT token
 */
function initTokenFunctionality(token) {
    initTokenCopyButton(token);
    initCodeExampleCopyButtons();
    initEndpointTestButtons(token);
}

/**
 * Initialize token copy button
 * @param {string} token - JWT token to copy
 */
function initTokenCopyButton(token) {
    $('#copyTokenBtn').click(function() {
        copyToClipboard(token, $(this));
    });
}

/**
 * Initialize copy buttons for code examples
 */
function initCodeExampleCopyButtons() {
    $('.copy-btn').click(function() {
        const targetId = $(this).data('target');
        let text = $('#' + targetId).html()
            .replace(/<br>/g, '\n')
            .replace(/&nbsp;/g, ' ')
            .replace(/&lt;/g, '<')
            .replace(/&gt;/g, '>')
            .replace(/&amp;/g, '&');
        
        copyToClipboard(text, $(this));
    });
}

/**
 * Initialize endpoint test buttons
 * @param {string} token - JWT token for authentication
 */
function initEndpointTestButtons(token) {
    $('.test-endpoint-btn').click(function() {
        const endpoint = $(this).data('endpoint');
        testEndpoint(endpoint, token, $(this));
    });
}

/**
 * Test an API endpoint
 * @param {string} endpoint - API endpoint to test
 * @param {string} token - JWT token for authentication
 * @param {jQuery} $button - Button element that triggered the test
 */
function testEndpoint(endpoint, token, $button) {
    const originalText = showButtonLoading($button);
    
    makeAuthenticatedAPICall(endpoint, token)
        .then(data => {
            displayTestResult(formatJSON(data));
        })
        .catch(xhr => {
            handleTestError(xhr);
        })
        .finally(() => {
            hideButtonLoading($button, originalText);
        });
}

/**
 * Display test result
 * @param {string} resultText - Formatted result text
 */
function displayTestResult(resultText) {
    $('#testOutput').text(resultText);
    $('#testResults').removeClass('hidden');
    smoothScrollTo('#testResults');
}

/**
 * Handle test errors
 * @param {Object} xhr - jQuery XHR object
 */
function handleTestError(xhr) {
    let errorMsg = 'Unknown error';
    
    try {
        const errorData = JSON.parse(xhr.responseText);
        errorMsg = errorData.message || errorData.error || xhr.responseText;
    } catch (e) {
        errorMsg = xhr.responseText || `HTTP ${xhr.status}`;
    }
    
    const errorText = `Error (${xhr.status}): ${errorMsg}`;
    displayTestResult(errorText);
}
