#!/usr/bin/env python3
"""
Script to test Stripe webhook functionality
"""

import json
import requests
import hmac
import hashlib
import time
from datetime import datetime

def create_test_event():
    """Create a test webhook event payload"""
    return {
        "id": "evt_test_" + str(int(time.time())),
        "object": "event",
        "api_version": "2020-08-27",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": "pi_test_" + str(int(time.time())),
                "object": "payment_intent",
                "amount": 2000,
                "currency": "usd",
                "customer": "cus_test_customer",
                "status": "succeeded"
            }
        },
        "livemode": False,
        "pending_webhooks": 1,
        "request": {
            "id": None,
            "idempotency_key": None
        },
        "type": "payment_intent.succeeded"
    }

def create_stripe_signature(payload, secret):
    """Create a Stripe-compatible signature"""
    timestamp = int(time.time())
    payload_str = json.dumps(payload, separators=(',', ':'))
    signed_payload = f"{timestamp}.{payload_str}"
    
    signature = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return f"t={timestamp},v1={signature}"

def test_webhook_endpoint(base_url="http://localhost:5000", webhook_secret="whsec_test_secret"):
    """Test the webhook endpoint"""
    
    print("🧪 Testing Stripe Webhook Endpoint")
    print("=" * 50)
    
    # Test 1: Check webhook configuration
    print("\n1. Testing webhook configuration...")
    try:
        response = requests.get(f"{base_url}/stripe/webhook/test")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Webhook endpoint is active")
            print(f"   - Webhook secret configured: {data.get('webhook_secret_configured')}")
            print(f"   - Stripe key configured: {data.get('stripe_key_configured')}")
        else:
            print(f"❌ Webhook test endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing webhook configuration: {e}")
    
    # Test 2: Send a test webhook event
    print("\n2. Testing webhook event processing...")
    try:
        # Create test event
        test_event = create_test_event()
        payload = json.dumps(test_event, separators=(',', ':'))
        
        # Create signature
        signature = create_stripe_signature(test_event, webhook_secret.replace('whsec_', ''))
        
        headers = {
            'Content-Type': 'application/json',
            'Stripe-Signature': signature
        }
        
        response = requests.post(
            f"{base_url}/stripe/webhook",
            data=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Webhook event processed successfully")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Webhook processing failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error sending test webhook: {e}")
    
    # Test 3: Test invalid signature
    print("\n3. Testing signature validation...")
    try:
        test_event = create_test_event()
        payload = json.dumps(test_event, separators=(',', ':'))
        
        headers = {
            'Content-Type': 'application/json',
            'Stripe-Signature': 'invalid_signature'
        }
        
        response = requests.post(
            f"{base_url}/stripe/webhook",
            data=payload,
            headers=headers
        )
        
        if response.status_code == 400:
            print("✅ Invalid signature correctly rejected")
        else:
            print(f"❌ Invalid signature should be rejected but got: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing invalid signature: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Webhook testing completed!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Stripe webhook endpoint')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='Base URL of the Flask app')
    parser.add_argument('--secret', default='whsec_test_secret',
                       help='Webhook secret for testing')
    
    args = parser.parse_args()
    
    test_webhook_endpoint(args.url, args.secret)
