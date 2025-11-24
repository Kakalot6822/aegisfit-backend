"""
Stripe integration service for payment processing
"""

import stripe
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class StripeService:
    """Service for handling Stripe payment operations"""
    
    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize Stripe service
        
        Args:
            secret_key: Stripe secret key
        """
        self.secret_key = secret_key
        self.available = bool(secret_key)
        
        if self.available:
            try:
                stripe.api_key = secret_key
                logger.info("Stripe service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Stripe: {e}")
                self.available = False
        else:
            logger.warning("Stripe service not available - no secret key provided")
    
    def is_available(self) -> bool:
        """Check if Stripe service is available"""
        return self.available
    
    def create_customer(self, email: str, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new Stripe customer
        
        Args:
            email: Customer email
            name: Customer name (optional)
            
        Returns:
            Customer data dictionary
        """
        if not self.available:
            raise ValueError("Stripe service not available")
        
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata={
                    "created_by": "aegis-fit-backend",
                    "created_at": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Created Stripe customer: {customer.id}")
            return {
                "id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "created": customer.created,
                "metadata": dict(customer.metadata)
            }
            
        except Exception as e:
            logger.error(f"Error creating Stripe customer: {e}")
            raise
    
    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new subscription
        
        Args:
            customer_id: Stripe customer ID
            price_id: Stripe price ID
            trial_days: Trial period in days (optional)
            
        Returns:
            Subscription data dictionary
        """
        if not self.available:
            raise ValueError("Stripe service not available")
        
        try:
            subscription_data = {
                "customer": customer_id,
                "items": [{"price": price_id}],
                "payment_behavior": "default_incomplete",
                "expand": ["latest_invoice.payment_intent"],
                "metadata": {
                    "created_by": "aegis-fit-backend",
                    "created_at": datetime.utcnow().isoformat()
                }
            }
            
            if trial_days:
                subscription_data["trial_period_days"] = trial_days
            
            subscription = stripe.Subscription.create(**subscription_data)
            
            logger.info(f"Created Stripe subscription: {subscription.id}")
            
            return {
                "id": subscription.id,
                "customer": subscription.customer,
                "status": subscription.status,
                "current_period_start": subscription.current_period_start,
                "current_period_end": subscription.current_period_end,
                "trial_start": subscription.trial_start,
                "trial_end": subscription.trial_end,
                "metadata": dict(subscription.metadata),
                "latest_invoice": subscription.latest_invoice.id if subscription.latest_invoice else None,
                "payment_intent": (
                    subscription.latest_invoice.payment_intent.id 
                    if subscription.latest_invoice and subscription.latest_invoice.payment_intent 
                    else None
                )
            }
            
        except Exception as e:
            logger.error(f"Error creating Stripe subscription: {e}")
            raise
    
    def create_checkout_session(
        self,
        price_id: str,
        customer_email: str,
        success_url: str,
        cancel_url: str,
        customer_id: Optional[str] = None,
        trial_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout session for subscription
        
        Args:
            price_id: Stripe price ID
            customer_email: Customer email
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect after cancelled payment
            customer_id: Existing Stripe customer ID (optional)
            trial_days: Trial period in days (optional)
            
        Returns:
            Checkout session data dictionary
        """
        if not self.available:
            raise ValueError("Stripe service not available")
        
        try:
            session_data = {
                "mode": "subscription",
                "line_items": [{"price": price_id, "quantity": 1}],
                "success_url": success_url,
                "cancel_url": cancel_url,
                "customer_email": customer_email,
                "metadata": {
                    "created_by": "aegis-fit-backend",
                    "created_at": datetime.utcnow().isoformat()
                }
            }
            
            if customer_id:
                session_data["customer"] = customer_id
            
            if trial_days:
                session_data["subscription_data"] = {
                    "trial_period_days": trial_days
                }
            
            session = stripe.checkout.Session.create(**session_data)
            
            logger.info(f"Created Stripe checkout session: {session.id}")
            
            return {
                "id": session.id,
                "url": session.url,
                "customer": session.customer,
                "customer_email": session.customer_email,
                "payment_status": session.payment_status,
                "status": session.status
            }
            
        except Exception as e:
            logger.error(f"Error creating Stripe checkout session: {e}")
            raise
    
    def get_customer_subscriptions(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Get all subscriptions for a customer
        
        Args:
            customer_id: Stripe customer ID
            
        Returns:
            List of subscription data dictionaries
        """
        if not self.available:
            raise ValueError("Stripe service not available")
        
        try:
            subscriptions = stripe.Subscription.list(
                customer=customer_id,
                expand=["data.default_payment_method"]
            )
            
            result = []
            for sub in subscriptions:
                result.append({
                    "id": sub.id,
                    "status": sub.status,
                    "current_period_start": sub.current_period_start,
                    "current_period_end": sub.current_period_end,
                    "trial_start": sub.trial_start,
                    "trial_end": sub.trial_end,
                    "cancel_at_period_end": sub.cancel_at_period_end,
                    "canceled_at": sub.canceled_at,
                    "metadata": dict(sub.metadata)
                })
            
            logger.info(f"Retrieved {len(result)} subscriptions for customer {customer_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting customer subscriptions: {e}")
            raise
    
    def cancel_subscription(
        self, 
        subscription_id: str, 
        at_period_end: bool = True
    ) -> Dict[str, Any]:
        """
        Cancel a subscription
        
        Args:
            subscription_id: Stripe subscription ID
            at_period_end: Whether to cancel at end of billing period
            
        Returns:
            Updated subscription data dictionary
        """
        if not self.available:
            raise ValueError("Stripe service not available")
        
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True,
                    metadata={
                        "cancelled_by": "aegis-fit-backend",
                        "cancelled_at": datetime.utcnow().isoformat()
                    }
                )
            else:
                subscription = stripe.Subscription.delete(subscription_id)
            
            logger.info(f"Cancelled subscription: {subscription_id}")
            
            return {
                "id": subscription.id,
                "status": subscription.status,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "canceled_at": subscription.canceled_at
            }
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            raise
    
    def update_subscription(
        self,
        subscription_id: str,
        new_price_id: str,
        proration_behavior: str = "create_prorations"
    ) -> Dict[str, Any]:
        """
        Update subscription to new price
        
        Args:
            subscription_id: Stripe subscription ID
            new_price_id: New Stripe price ID
            proration_behavior: How to handle proration
            
        Returns:
            Updated subscription data dictionary
        """
        if not self.available:
            raise ValueError("Stripe service not available")
        
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription.items.data[0].id,
                    "price": new_price_id,
                }],
                proration_behavior=proration_behavior,
                metadata={
                    "updated_by": "aegis-fit-backend",
                    "updated_at": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Updated subscription {subscription_id} to new price")
            
            return {
                "id": updated_subscription.id,
                "status": updated_subscription.status,
                "current_period_start": updated_subscription.current_period_start,
                "current_period_end": updated_subscription.current_period_end,
                "items": [
                    {
                        "id": item.id,
                        "price": item.price.id,
                        "quantity": item.quantity
                    }
                    for item in updated_subscription.items.data
                ]
            }
            
        except Exception as e:
            logger.error(f"Error updating subscription: {e}")
            raise
    
    def get_subscription_invoices(self, subscription_id: str) -> List[Dict[str, Any]]:
        """
        Get all invoices for a subscription
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            List of invoice data dictionaries
        """
        if not self.available:
            raise ValueError("Stripe service not available")
        
        try:
            invoices = stripe.Invoice.list(subscription=subscription_id)
            
            result = []
            for invoice in invoices:
                result.append({
                    "id": invoice.id,
                    "number": invoice.number,
                    "status": invoice.status,
                    "amount_due": invoice.amount_due,
                    "amount_paid": invoice.amount_paid,
                    "currency": invoice.currency,
                    "created": invoice.created,
                    "due_date": invoice.due_date,
                    "paid": invoice.paid,
                    "hosted_invoice_url": invoice.hosted_invoice_url,
                    "invoice_pdf": invoice.invoice_pdf
                })
            
            logger.info(f"Retrieved {len(result)} invoices for subscription {subscription_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting subscription invoices: {e}")
            raise
    
    def construct_webhook_event(
        self, 
        payload: bytes, 
        signature: str, 
        webhook_secret: str
    ) -> Any:
        """
        Construct and verify Stripe webhook event
        
        Args:
            payload: Raw webhook payload
            signature: Stripe signature header
            webhook_secret: Stripe webhook secret
            
        Returns:
            Verified Stripe event object
        """
        if not self.available:
            raise ValueError("Stripe service not available")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            
            logger.info(f"Constructed verified webhook event: {event.type}")
            return event
            
        except Exception as e:
            logger.error(f"Error constructing webhook event: {e}")
            raise