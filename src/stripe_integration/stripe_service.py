"""
Stripe service module for handling Stripe webhooks and events
"""

import json
import logging
import stripe
from flask import current_app

# Configure logging
logger = logging.getLogger(__name__)

class StripeWebhookService:
    """Service class for handling Stripe webhook events"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Stripe configuration"""
        stripe.api_key = app.config.get('STRIPE_SECRET_KEY')
        
    def verify_webhook_signature(self, payload, signature, endpoint_secret):
        """
        Verify the webhook signature from Stripe
        
        Args:
            payload (bytes): Raw request payload
            signature (str): Stripe signature header
            endpoint_secret (str): Webhook endpoint secret
            
        Returns:
            dict: Verified event object
            
        Raises:
            stripe.error.SignatureVerificationError: If signature verification fails
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, endpoint_secret
            )
            logger.info(f"Successfully verified webhook signature for event: {event['type']}")
            return event
        except Exception as e:
            # Handle signature verification errors
            if 'signature' in str(e).lower() or 'verification' in str(e).lower():
                logger.error(f"Webhook signature verification failed: {str(e)}")
                raise
            else:
                logger.error(f"Unexpected error in webhook verification: {str(e)}")
                raise
    
    def handle_payment_intent_succeeded(self, payment_intent):
        """
        Handle successful payment intent
        
        Args:
            payment_intent (dict): Stripe PaymentIntent object
        """
        amount = payment_intent.get('amount', 0)
        currency = payment_intent.get('currency', 'usd')
        customer_id = payment_intent.get('customer')
        
        logger.info(f"Payment succeeded: {amount/100} {currency.upper()} for customer {customer_id}")
        
        # TODO: Update user subscription status in database
        # TODO: Send confirmation email
        # TODO: Activate premium features
        
        return True
    
    def handle_payment_intent_failed(self, payment_intent):
        """
        Handle failed payment intent
        
        Args:
            payment_intent (dict): Stripe PaymentIntent object
        """
        customer_id = payment_intent.get('customer')
        failure_reason = payment_intent.get('last_payment_error', {}).get('message', 'Unknown error')
        
        logger.warning(f"Payment failed for customer {customer_id}: {failure_reason}")
        
        # TODO: Handle failed payment (retry, notification, etc.)
        
        return True
    
    def handle_customer_subscription_created(self, subscription):
        """
        Handle new subscription creation
        
        Args:
            subscription (dict): Stripe Subscription object
        """
        customer_id = subscription.get('customer')
        subscription_id = subscription.get('id')
        status = subscription.get('status')
        
        logger.info(f"New subscription {subscription_id} created for customer {customer_id} with status {status}")
        
        # TODO: Update user subscription in database
        # TODO: Send welcome email
        
        return True
    
    def handle_customer_subscription_updated(self, subscription):
        """
        Handle subscription updates
        
        Args:
            subscription (dict): Stripe Subscription object
        """
        customer_id = subscription.get('customer')
        subscription_id = subscription.get('id')
        status = subscription.get('status')
        
        logger.info(f"Subscription {subscription_id} updated for customer {customer_id} with status {status}")
        
        # TODO: Update subscription status in database
        # TODO: Handle plan changes, cancellations, etc.
        
        return True
    
    def handle_customer_subscription_deleted(self, subscription):
        """
        Handle subscription cancellation/deletion
        
        Args:
            subscription (dict): Stripe Subscription object
        """
        customer_id = subscription.get('customer')
        subscription_id = subscription.get('id')
        
        logger.info(f"Subscription {subscription_id} cancelled for customer {customer_id}")
        
        # TODO: Deactivate premium features
        # TODO: Update user status in database
        # TODO: Send cancellation confirmation
        
        return True
    
    def handle_invoice_payment_succeeded(self, invoice):
        """
        Handle successful invoice payment
        
        Args:
            invoice (dict): Stripe Invoice object
        """
        customer_id = invoice.get('customer')
        amount_paid = invoice.get('amount_paid', 0)
        subscription_id = invoice.get('subscription')
        
        logger.info(f"Invoice payment succeeded: {amount_paid/100} for customer {customer_id}, subscription {subscription_id}")
        
        # TODO: Extend subscription period
        # TODO: Send payment receipt
        
        return True
    
    def handle_invoice_payment_failed(self, invoice):
        """
        Handle failed invoice payment
        
        Args:
            invoice (dict): Stripe Invoice object
        """
        customer_id = invoice.get('customer')
        subscription_id = invoice.get('subscription')
        
        logger.warning(f"Invoice payment failed for customer {customer_id}, subscription {subscription_id}")
        
        # TODO: Send payment failure notification
        # TODO: Implement retry logic
        # TODO: Suspend service if needed
        
        return True
    
    def process_webhook_event(self, event):
        """
        Process incoming webhook event
        
        Args:
            event (dict): Verified Stripe event object
            
        Returns:
            bool: True if event was processed successfully
        """
        event_type = event.get('type')
        data_object = event.get('data', {}).get('object', {})
        
        logger.info(f"Processing webhook event: {event_type}")
        
        # Route event to appropriate handler
        handlers = {
            'payment_intent.succeeded': self.handle_payment_intent_succeeded,
            'payment_intent.payment_failed': self.handle_payment_intent_failed,
            'customer.subscription.created': self.handle_customer_subscription_created,
            'customer.subscription.updated': self.handle_customer_subscription_updated,
            'customer.subscription.deleted': self.handle_customer_subscription_deleted,
            'invoice.payment_succeeded': self.handle_invoice_payment_succeeded,
            'invoice.payment_failed': self.handle_invoice_payment_failed,
        }
        
        handler = handlers.get(event_type)
        if handler:
            try:
                return handler(data_object)
            except Exception as e:
                logger.error(f"Error processing {event_type}: {str(e)}")
                return False
        else:
            logger.info(f"Unhandled event type: {event_type}")
            return True  # Return True for unhandled events to acknowledge receipt

# Initialize service instance
stripe_service = StripeWebhookService()
