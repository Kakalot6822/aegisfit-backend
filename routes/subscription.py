"""
Subscription management routes for AEGIS FIT Backend API
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Import models
from models.subscription import (
    SubscriptionPlan,
    SubscriptionRequest, 
    SubscriptionResponse,
    StripeWebhookEvent,
    PaymentStatus,
    SubscriptionStatus
)

logger = logging.getLogger(__name__)

subscription_router = APIRouter(prefix="/subscription", tags=["subscription"])


# Static subscription plans (in production, these might come from a database)
SUBSCRIPTION_PLANS = [
    {
        "id": "free",
        "name": "Free Plan",
        "description": "Basic fitness tracking with limited features",
        "price": 0.0,
        "currency": "USD",
        "interval": "month",
        "features": [
            "Basic workout tracking",
            "Limited progress analytics",
            "Community access",
            "Mobile app access"
        ],
        "is_popular": False,
        "max_users": 1,
        "max_projects": 3
    },
    {
        "id": "premium",
        "name": "Premium Plan",
        "description": "Full fitness tracking with advanced analytics",
        "price": 9.99,
        "currency": "USD",
        "interval": "month",
        "features": [
            "Unlimited workout tracking",
            "Advanced progress analytics",
            "Personalized workout plans",
            "Nutrition tracking",
            "Priority support",
            "Export data",
            "Multiple device sync"
        ],
        "is_popular": True,
        "max_users": 5,
        "max_projects": 10
    },
    {
        "id": "pro",
        "name": "Professional Plan",
        "description": "Complete fitness solution for serious athletes",
        "price": 19.99,
        "currency": "USD",
        "interval": "month",
        "features": [
            "Everything in Premium",
            "Personal trainer consultations",
            "Custom meal plans",
            "Advanced body composition analysis",
            "API access for integrations",
            "Team/coach dashboard",
            "White-label options"
        ],
        "is_popular": False,
        "max_users": 50,
        "max_projects": 100
    },
    {
        "id": "enterprise",
        "name": "Enterprise Plan",
        "description": "Scalable solution for large organizations",
        "price": 99.99,
        "currency": "USD",
        "interval": "month",
        "features": [
            "Everything in Professional",
            "Unlimited users and projects",
            "Custom integrations",
            "Dedicated support",
            "SSO integration",
            "Advanced analytics",
            "Custom reporting",
            "White-label dashboard"
        ],
        "is_popular": False,
        "max_users": -1,  # Unlimited
        "max_projects": -1  # Unlimited
    }
]


@subscription_router.get("/plans", response_model=List[SubscriptionPlan])
async def get_subscription_plans():
    """Get all available subscription plans"""
    try:
        logger.info("Fetching subscription plans")
        
        # In a real application, you might fetch this from a database
        # or from Stripe's API if you're using Stripe for plan management
        
        plans = [
            SubscriptionPlan(**plan_data) for plan_data in SUBSCRIPTION_PLANS
        ]
        
        logger.info(f"Successfully fetched {len(plans)} subscription plans")
        return plans
        
    except Exception as e:
        logger.error(f"Error fetching subscription plans: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to fetch subscription plans"
        )


@subscription_router.post("/create")
async def create_subscription(request: SubscriptionRequest):
    """Create a new subscription"""
    try:
        logger.info(f"Creating subscription for plan {request.plan_id} and user {request.user_id}")
        
        # Find the requested plan
        plan = None
        for plan_data in SUBSCRIPTION_PLANS:
            if plan_data["id"] == request.plan_id:
                plan = plan_data
                break
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")
        
        # Handle different plan types
        if plan["price"] == 0.0:
            # Free plan - activate immediately
            response = SubscriptionResponse(
                success=True,
                message="Free subscription activated successfully",
                subscription_id=f"free_{request.user_id}_{int(datetime.utcnow().timestamp())}",
                plan_id=request.plan_id,
                user_id=request.user_id,
                status=SubscriptionStatus.ACTIVE,
                created_at=datetime.utcnow()
            )
        else:
            # Paid plan - would normally integrate with Stripe
            # For demo purposes, return a placeholder response
            
            response = SubscriptionResponse(
                success=True,
                message="Subscription created successfully",
                subscription_id=f"sub_{request.user_id}_{int(datetime.utcnow().timestamp())}",
                plan_id=request.plan_id,
                user_id=request.user_id,
                status=SubscriptionStatus.PENDING,
                checkout_url="https://checkout.stripe.com/pay/example",
                created_at=datetime.utcnow()
            )
        
        logger.info(f"Successfully created subscription: {response.subscription_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subscription: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to create subscription"
        )


@subscription_router.get("/status/{user_id}")
async def get_subscription_status(user_id: str):
    """Get subscription status for a user"""
    try:
        logger.info(f"Getting subscription status for user {user_id}")
        
        # In a real application, you would fetch this from a database
        # For demo purposes, return a mock response
        
        # Check if user has any subscription (mock implementation)
        if user_id == "test_user":
            subscription = {
                "user_id": user_id,
                "subscription_id": f"sub_{user_id}",
                "plan_id": "premium",
                "status": SubscriptionStatus.ACTIVE,
                "payment_status": PaymentStatus.PAID,
                "current_period_start": datetime.utcnow(),
                "current_period_end": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
        else:
            subscription = {
                "user_id": user_id,
                "subscription_id": None,
                "plan_id": "free",
                "status": SubscriptionStatus.INACTIVE,
                "payment_status": PaymentStatus.PENDING,
                "current_period_start": None,
                "current_period_end": None,
                "created_at": None
            }
        
        logger.info(f"Successfully fetched subscription status for user {user_id}")
        return {
            "success": True,
            "subscription": subscription,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error getting subscription status: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to get subscription status"
        )


@subscription_router.post("/webhook")
async def handle_stripe_webhook(request: Request):
    """Handle Stripe webhook events"""
    try:
        # Get the raw body and signature
        payload = await request.body()
        sig_header = request.headers.get("stripe-signature")
        
        logger.info("Received Stripe webhook")
        
        if not sig_header:
            raise HTTPException(status_code=400, detail="Missing Stripe signature")
        
        # In a real application, you would verify the webhook signature
        # and process the event. For demo purposes, we just log it.
        
        import json
        try:
            event_data = json.loads(payload)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        event_type = event_data.get("type")
        event_id = event_data.get("id")
        
        logger.info(f"Processing Stripe webhook event: {event_type} (ID: {event_id})")
        
        # Handle different event types
        if event_type == "customer.subscription.created":
            logger.info("New subscription created")
            # Process new subscription
        elif event_type == "customer.subscription.updated":
            logger.info("Subscription updated")
            # Process subscription update
        elif event_type == "customer.subscription.deleted":
            logger.info("Subscription cancelled")
            # Process subscription cancellation
        elif event_type == "invoice.payment_succeeded":
            logger.info("Payment succeeded")
            # Process successful payment
        elif event_type == "invoice.payment_failed":
            logger.info("Payment failed")
            # Process failed payment
        else:
            logger.info(f"Unhandled event type: {event_type}")
        
        return {
            "success": True,
            "message": f"Webhook {event_type} processed successfully",
            "event_id": event_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Webhook processing failed"
        )


@subscription_router.post("/cancel/{subscription_id}")
async def cancel_subscription(subscription_id: str):
    """Cancel an existing subscription"""
    try:
        logger.info(f"Cancelling subscription: {subscription_id}")
        
        # In a real application, you would:
        # 1. Verify the subscription exists
        # 2. Cancel it in Stripe (if using Stripe)
        # 3. Update your database
        # 4. Send confirmation email
        
        response = {
            "success": True,
            "message": f"Subscription {subscription_id} cancelled successfully",
            "subscription_id": subscription_id,
            "cancelled_at": datetime.utcnow().isoformat() + "Z",
            "effective_date": datetime.utcnow().isoformat() + "Z"
        }
        
        logger.info(f"Successfully cancelled subscription: {subscription_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error cancelling subscription: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to cancel subscription"
        )