# Stripe Webhook Integration Guide

## Overview

This guide explains how to set up and use the secure Stripe webhook integration in your Flask OAuth application.

## Features

✅ **Secure Signature Verification** - All we## File Structure

```
src/
├── stripe_integration/
│   ├── __init__.py
│   ├── stripe_service.py     # Main service class
│   └── webhook_routes.py     # Flask routes
├── config/
│   └── config.py            # Updated with Stripe config
└── app/
    └── app.py               # Main app with Stripe integration

tests/
└── integration/
    └── test_stripe_webhook.py # Test script
.env.example                 # Environment template
```ied using Stripe's signature mechanism  
✅ **Comprehensive Event Handling** - Supports all major Stripe events  
✅ **Structured Service Layer** - Clean separation of concerns with dedicated service classes  
✅ **Error Handling & Logging** - Proper error handling with detailed logging  
✅ **Testing Support** - Built-in test endpoints and test script  

## Supported Webhook Events

| Event Type | Description | Handler Method |
|------------|-------------|----------------|
| `payment_intent.succeeded` | Payment completed successfully | `handle_payment_intent_succeeded` |
| `payment_intent.payment_failed` | Payment failed | `handle_payment_intent_failed` |
| `customer.subscription.created` | New subscription created | `handle_customer_subscription_created` |
| `customer.subscription.updated` | Subscription updated | `handle_customer_subscription_updated` |
| `customer.subscription.deleted` | Subscription cancelled | `handle_customer_subscription_deleted` |
| `invoice.payment_succeeded` | Invoice payment succeeded | `handle_invoice_payment_succeeded` |
| `invoice.payment_failed` | Invoice payment failed | `handle_invoice_payment_failed` |

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements/requirements.txt
```

### 2. Configure Environment Variables

Add these variables to your `.env` file:

```bash
# Stripe Configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_actual_webhook_secret_here
```

### 3. Configure Stripe Dashboard

1. Go to [Stripe Dashboard > Webhooks](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. Set endpoint URL: `https://yourdomain.com/stripe/webhook`
4. Select events to listen to:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the webhook secret to your `.env` file

## Testing

### 1. Test Webhook Configuration

```bash
curl http://localhost:5000/stripe/webhook/test
```

Expected response:
```json
{
  "status": "webhook endpoint active",
  "webhook_secret_configured": true,
  "stripe_key_configured": true,
  "endpoint": "/stripe/webhook"
}
```

### 2. Run Automated Tests

```bash
python tests/integration/test_stripe_webhook.py
```

For custom testing:
```bash
python tests/integration/test_stripe_webhook.py --url http://localhost:5000 --secret whsec_your_secret
```

### 3. Test with Stripe CLI

Install Stripe CLI and forward events:

```bash
# Install Stripe CLI
# See: https://stripe.com/docs/stripe-cli

# Forward events to your local endpoint
stripe listen --forward-to localhost:5000/stripe/webhook

# Trigger test events
stripe trigger payment_intent.succeeded
stripe trigger customer.subscription.created
```

## API Endpoints

### Webhook Endpoint
- **URL**: `/stripe/webhook`
- **Method**: `POST`
- **Headers**: `Stripe-Signature` (required)
- **Body**: Stripe event JSON payload

### Test Endpoint
- **URL**: `/stripe/webhook/test`
- **Method**: `GET`
- **Purpose**: Verify webhook configuration

### Development Events Endpoint
- **URL**: `/stripe/events`
- **Method**: `GET`
- **Purpose**: List recent Stripe events (development only)

## Security Features

### Signature Verification
All incoming webhooks are verified using Stripe's signature mechanism:

```python
event = stripe.Webhook.construct_event(
    payload, signature, endpoint_secret
)
```

### Error Handling
- Invalid signatures return `400 Bad Request`
- Missing signatures return `400 Bad Request`
- Processing errors return `500 Internal Server Error`
- Successful processing returns `200 OK`

### Logging
All webhook events are logged with appropriate levels:
- `INFO`: Successful processing
- `WARNING`: Failed payments, cancellations
- `ERROR`: Signature verification failures, processing errors

## Customization

### Adding New Event Handlers

1. Add handler method to `StripeWebhookService`:

```python
def handle_new_event(self, event_data):
    """Handle new event type"""
    # Your custom logic here
    logger.info(f"Processing new event: {event_data}")
    return True
```

2. Register handler in `process_webhook_event`:

```python
handlers = {
    # ... existing handlers
    'new.event.type': self.handle_new_event,
}
```

### Database Integration

Modify handler methods to update your database:

```python
def handle_payment_intent_succeeded(self, payment_intent):
    customer_id = payment_intent.get('customer')
    amount = payment_intent.get('amount')
    
    # Update user subscription in database
    user = User.query.filter_by(stripe_customer_id=customer_id).first()
    if user:
        user.subscription_status = 'active'
        user.last_payment_date = datetime.utcnow()
        db.session.commit()
    
    return True
```

## Production Deployment

### 1. Security Checklist
- [ ] Use strong webhook secret
- [ ] Enable HTTPS for webhook endpoint
- [ ] Use production Stripe keys
- [ ] Configure proper logging
- [ ] Set up monitoring/alerts

### 2. Monitoring
Monitor webhook delivery in Stripe Dashboard:
- Go to Webhooks section
- Click on your endpoint
- Review delivery attempts and responses

### 3. Debugging
Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `400 Invalid signature` | Wrong webhook secret | Check `STRIPE_WEBHOOK_SECRET` |
| `500 Internal server error` | Processing error | Check application logs |
| No events received | Wrong endpoint URL | Verify URL in Stripe Dashboard |
| Events not processed | Handler error | Check handler implementation |

## File Structure

```
src/
├── stripe_integration/
│   ├── __init__.py
│   ├── stripe_service.py     # Main service class
│   └── webhook_routes.py     # Flask routes
├── config/
│   └── config.py            # Updated with Stripe config
└── app/
    └── app.py               # Main app with Stripe integration

test_stripe_webhook.py       # Test script
.env.example                 # Environment template
```

## Support

For questions or issues:
1. Check the logs for detailed error messages
2. Verify webhook configuration in Stripe Dashboard
3. Test with the provided test script
4. Review Stripe documentation: https://stripe.com/docs/webhooks

---

**Security Note**: Never commit your actual Stripe keys to version control. Always use environment variables for sensitive configuration.
