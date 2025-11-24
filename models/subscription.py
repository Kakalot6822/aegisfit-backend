"""
Subscription-related data models for AEGIS FIT Backend
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, EmailStr, Field, validator


class PaymentStatus(str, Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class SubscriptionStatus(str, Enum):
    """Subscription status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PAST_DUE = "past_due"
    PENDING = "pending"


class SubscriptionPlan(BaseModel):
    """Subscription plan data model"""
    id: str = Field(..., description="Unique identifier for the plan")
    name: str = Field(..., description="Display name of the plan")
    description: str = Field(..., description="Detailed description of the plan")
    price: float = Field(..., ge=0, description="Price in currency")
    currency: str = Field(default="THB", description="Currency code")
    interval: str = Field(default="year", description="Billing interval")
    features: List[str] = Field(..., description="List of plan features")
    stripe_price_id: Optional[str] = Field(None, description="Stripe price ID")
    is_popular: bool = Field(default=False, description="Whether this is a popular plan")
    max_users: Optional[int] = Field(None, description="Maximum users for this plan")
    max_projects: Optional[int] = Field(None, description="Maximum projects for this plan")
    installment_months: Optional[int] = Field(None, description="Number of installment months (0 or None for one-time payment)")
    
    @validator('price')
    def validate_price(cls, v):
        """Ensure price is non-negative"""
        if v < 0:
            raise ValueError('Price must be non-negative')
        return v
    
    @validator('currency')
    def validate_currency(cls, v):
        """Validate currency format"""
        allowed_currencies = ['USD', 'EUR', 'GBP', 'THB']
        if v.upper() not in allowed_currencies:
            raise ValueError(f'Currency must be one of: {allowed_currencies}')
        return v.upper()
    
    @validator('interval')
    def validate_interval(cls, v):
        """Validate billing interval"""
        allowed_intervals = ['month', 'year']
        if v not in allowed_intervals:
            raise ValueError(f'Interval must be one of: {allowed_intervals}')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "premium",
                "name": "Premium Plan",
                "description": "Full fitness tracking with advanced analytics",
                "price": 9.99,
                "currency": "USD",
                "interval": "month",
                "features": [
                    "Unlimited workout tracking",
                    "Advanced progress analytics",
                    "Personalized workout plans"
                ],
                "is_popular": True
            }
        }


class SubscriptionRequest(BaseModel):
    """Request model for creating subscriptions"""
    plan_id: str = Field(..., description="ID of the subscription plan")
    user_id: str = Field(..., min_length=1, description="User ID who wants to subscribe")
    email: Optional[EmailStr] = Field(None, description="User email for billing")
    payment_method_id: Optional[str] = Field(None, description="Stripe payment method ID")
    
    @validator('plan_id')
    def validate_plan_id(cls, v):
        """Ensure plan ID is not empty"""
        if not v or not v.strip():
            raise ValueError('Plan ID is required')
        return v.strip().lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "plan_id": "premium",
                "user_id": "user_123",
                "email": "user@example.com",
                "payment_method_id": "pm_1234567890"
            }
        }


class SubscriptionResponse(BaseModel):
    """Response model for subscription operations"""
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Response message")
    subscription_id: Optional[str] = Field(None, description="Created subscription ID")
    plan_id: Optional[str] = Field(None, description="Associated plan ID")
    user_id: Optional[str] = Field(None, description="User ID")
    status: Optional[SubscriptionStatus] = Field(None, description="Subscription status")
    stripe_customer_id: Optional[str] = Field(None, description="Stripe customer ID")
    stripe_subscription_id: Optional[str] = Field(None, description="Stripe subscription ID")
    checkout_url: Optional[str] = Field(None, description="Payment checkout URL")
    expires_at: Optional[datetime] = Field(None, description="Subscription expiration date")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    # New fields for installment support
    installment_months: Optional[int] = Field(None, description="Number of installment months (0 for one-time payment)")
    installment_amount: Optional[float] = Field(None, description="Amount per installment")
    total_amount: Optional[float] = Field(None, description="Total subscription amount")
    currency: Optional[str] = Field(None, description="Currency code")
    billing_interval: Optional[str] = Field(None, description="Billing interval (month/year)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "สร้างการสมัครสมาชิกสำเร็จ - แบ่งจ่าย 3 งวด งวดละ 996.67 THB",
                "subscription_id": "sub_1234567890",
                "plan_id": "premium",
                "user_id": "user_123",
                "status": "pending",
                "checkout_url": "https://checkout.stripe.com/pay/example",
                "installment_months": 3,
                "installment_amount": 996.67,
                "total_amount": 2990.0,
                "currency": "THB",
                "billing_interval": "year"
            }
        }


class StripeWebhookEvent(BaseModel):
    """Model for Stripe webhook events"""
    type: str = Field(..., description="Event type from Stripe")
    id: str = Field(..., description="Event ID from Stripe")
    object: str = Field(default="event", description="Stripe object type")
    api_version: str = Field(default="2020-08-27", description="Stripe API version")
    created: int = Field(..., description="Event creation timestamp")
    data: Dict[str, Any] = Field(..., description="Event data object")
    livemode: bool = Field(..., description="Whether the event is from live mode")
    pending_webhooks: int = Field(default=1, description="Number of pending webhooks")
    request: Dict[str, Any] = Field(..., description="Request information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "customer.subscription.created",
                "id": "evt_1234567890",
                "object": "event",
                "created": 1640995200,
                "data": {
                    "object": {
                        "id": "sub_1234567890",
                        "customer": "cus_1234567890",
                        "status": "active"
                    }
                },
                "livemode": False,
                "pending_webhooks": 1,
                "request": {
                    "id": "req_1234567890",
                    "idempotency_key": None
                }
            }
        }


class UserSubscription(BaseModel):
    """User subscription data model"""
    user_id: str = Field(..., description="User ID")
    subscription_id: str = Field(..., description="Subscription ID")
    plan_id: str = Field(..., description="Associated plan ID")
    status: SubscriptionStatus = Field(..., description="Current subscription status")
    payment_status: PaymentStatus = Field(..., description="Payment status")
    current_period_start: datetime = Field(..., description="Current period start")
    current_period_end: datetime = Field(..., description="Current period end")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    cancelled_at: Optional[datetime] = Field(None, description="Cancellation timestamp")
    trial_start: Optional[datetime] = Field(None, description="Trial period start")
    trial_end: Optional[datetime] = Field(None, description="Trial period end")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "subscription_id": "sub_1234567890",
                "plan_id": "premium",
                "status": "active",
                "payment_status": "paid",
                "current_period_start": "2025-11-24T00:00:00Z",
                "current_period_end": "2025-12-24T00:00:00Z"
            }
        }


class SubscriptionUpdateRequest(BaseModel):
    """Request model for updating subscriptions"""
    subscription_id: str = Field(..., description="Subscription ID to update")
    new_plan_id: Optional[str] = Field(None, description="New plan ID (for plan changes)")
    cancel_at_period_end: bool = Field(default=False, description="Cancel at end of current period")
    resume: Optional[bool] = Field(None, description="Resume a cancelled subscription")
    
    @validator('subscription_id')
    def validate_subscription_id(cls, v):
        """Ensure subscription ID is not empty"""
        if not v or not v.strip():
            raise ValueError('Subscription ID is required')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "subscription_id": "sub_1234567890",
                "new_plan_id": "pro",
                "cancel_at_period_end": False
            }
        }


class SubscriptionMetrics(BaseModel):
    """Subscription metrics and statistics"""
    total_subscriptions: int = Field(..., description="Total number of subscriptions")
    active_subscriptions: int = Field(..., description="Number of active subscriptions")
    cancelled_subscriptions: int = Field(..., description="Number of cancelled subscriptions")
    monthly_recurring_revenue: float = Field(..., description="Monthly recurring revenue")
    churn_rate: float = Field(..., description="Monthly churn rate")
    average_revenue_per_user: float = Field(..., description="Average revenue per user")
    plan_breakdown: Dict[str, int] = Field(..., description="Breakdown by plan")
    status_breakdown: Dict[str, int] = Field(..., description="Breakdown by status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_subscriptions": 150,
                "active_subscriptions": 120,
                "cancelled_subscriptions": 30,
                "monthly_recurring_revenue": 1198.80,
                "churn_rate": 0.15,
                "average_revenue_per_user": 9.99,
                "plan_breakdown": {
                    "free": 80,
                    "premium": 50,
                    "pro": 20
                },
                "status_breakdown": {
                    "active": 120,
                    "cancelled": 30
                }
            }
        }