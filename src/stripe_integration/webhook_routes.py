"""
Stripe webhook routes for handling Stripe events
"""

import json
import logging
from flask import Blueprint, request, jsonify, current_app
import stripe

from .stripe_service import stripe_service

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
stripe_bp = Blueprint('stripe', __name__, url_prefix='/stripe')

@stripe_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """
    Secure Stripe webhook endpoint for handling events
    
    This endpoint:
    1. Verifies the webhook signature for security
    2. Processes the event using the StripeWebhookService
    3. Returns appropriate responses to Stripe
    """
    # Get raw payload and signature
    payload = request.data
    signature = request.headers.get('Stripe-Signature')
    endpoint_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    
    if not endpoint_secret:
        logger.error("STRIPE_WEBHOOK_SECRET not configured")
        return jsonify({'error': 'Webhook secret not configured'}), 500
    
    if not signature:
        logger.error("Missing Stripe signature header")
        return jsonify({'error': 'Missing signature'}), 400
    
    try:
        # Parse payload as JSON for basic validation
        try:
            json.loads(payload)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {str(e)}")
            return jsonify({'error': 'Invalid JSON payload'}), 400
        
        # Verify webhook signature and get event
        event = stripe_service.verify_webhook_signature(
            payload, signature, endpoint_secret
        )
        
        # Process the event
        success = stripe_service.process_webhook_event(event)
        
        if success:
            logger.info(f"Successfully processed webhook event: {event.get('type')}")
            return jsonify({'status': 'success'}), 200
        else:
            logger.error(f"Failed to process webhook event: {event.get('type')}")
            return jsonify({'error': 'Event processing failed'}), 500
            
    except Exception as e:
        # Handle Stripe signature verification errors
        if 'signature' in str(e).lower() or 'verification' in str(e).lower():
            logger.error(f"Webhook signature verification failed: {str(e)}")
            return jsonify({'error': 'Invalid signature'}), 400
        else:
            logger.error(f"Unexpected error processing webhook: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500

@stripe_bp.route('/webhook/test', methods=['GET'])
def webhook_test():
    """
    Test endpoint to verify webhook configuration
    """
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    stripe_key = current_app.config.get('STRIPE_SECRET_KEY')
    
    return jsonify({
        'status': 'webhook endpoint active',
        'webhook_secret_configured': bool(webhook_secret),
        'stripe_key_configured': bool(stripe_key),
        'endpoint': '/stripe/webhook'
    })

@stripe_bp.route('/events', methods=['GET'])
def list_recent_events():
    """
    Development endpoint to list recent Stripe events
    (Only enable in development mode)
    """
    if not current_app.config.get('DEBUG'):
        return jsonify({'error': 'Not available in production'}), 403
    
    try:
        # List recent events from Stripe (using direct API call for compatibility)
        import requests
        stripe_key = current_app.config.get('STRIPE_SECRET_KEY')
        
        if not stripe_key:
            return jsonify({'error': 'Stripe key not configured'}), 500
        
        response = requests.get(
            'https://api.stripe.com/v1/events',
            auth=(stripe_key, ''),
            params={'limit': 10}
        )
        
        if response.status_code == 200:
            events_data = response.json()
            event_list = []
            for event in events_data.get('data', []):
                event_list.append({
                    'id': event.get('id'),
                    'type': event.get('type'),
                    'created': event.get('created'),
                    'object': event.get('data', {}).get('object', {}).get('object', 'unknown')
                })
            
            return jsonify({
                'events': event_list,
                'count': len(event_list)
            })
        else:
            return jsonify({'error': 'Failed to fetch events from Stripe'}), 500
        
    except Exception as e:
        logger.error(f"Error fetching events: {str(e)}")
        return jsonify({'error': 'Failed to fetch events'}), 500
