"""
Utility helper functions for AEGIS FIT Backend
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal, ROUND_HALF_UP
import calendar

logger = logging.getLogger(__name__)

# Email validation regex
EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

# Subscription feature mappings
SUBSCRIPTION_FEATURES = {
    "free": [
        "Basic workout tracking",
        "Limited progress analytics (7 days)",
        "Community access",
        "Mobile app access",
        "Basic workout templates"
    ],
    "premium": [
        "Unlimited workout tracking",
        "Advanced progress analytics",
        "Personalized workout plans",
        "Nutrition tracking and macros",
        "Priority support",
        "Export data (CSV, PDF)",
        "Multiple device sync",
        "Workout history (full)",
        "Custom exercise library",
        "Progress photos"
    ],
    "pro": [
        "Everything in Premium",
        "Personal trainer consultations (2/month)",
        "Custom meal plans",
        "Advanced body composition analysis",
        "API access for integrations",
        "Team/coach dashboard",
        "White-label options",
        "Advanced reporting",
        "Custom notifications",
        "Priority feature requests"
    ],
    "enterprise": [
        "Everything in Professional",
        "Unlimited users and projects",
        "Custom integrations",
        "Dedicated support manager",
        "SSO integration",
        "Advanced analytics and reporting",
        "Custom reporting dashboard",
        "White-label mobile apps",
        "Custom branding",
        "Training and onboarding",
        "SLA guarantees",
        "Custom feature development"
    ]
}


def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    return bool(EMAIL_REGEX.match(email.strip()))


def format_currency(amount: float, currency: str = "USD", symbol: bool = True) -> str:
    """
    Format currency amount with proper formatting
    
    Args:
        amount: Amount to format
        currency: Currency code (USD, EUR, etc.)
        symbol: Whether to include currency symbol
        
    Returns:
        Formatted currency string
    """
    try:
        # Convert to Decimal for precise formatting
        decimal_amount = Decimal(str(amount))
        
        # Currency symbols mapping
        symbols = {
            "USD": "$",
            "EUR": "€", 
            "GBP": "£",
            "THB": "฿"
        }
        
        currency_symbol = symbols.get(currency.upper(), currency)
        
        if symbol and currency_symbol != currency:
            formatted = f"{currency_symbol}{decimal_amount:.2f}"
        else:
            formatted = f"{decimal_amount:.2f} {currency}"
        
        return formatted
        
    except (ValueError, TypeError) as e:
        logger.error(f"Error formatting currency: {e}")
        return f"${amount:.2f}"  # Fallback


def generate_subscription_id(user_id: str, plan_id: str) -> str:
    """
    Generate a unique subscription ID
    
    Args:
        user_id: User identifier
        plan_id: Plan identifier
        
    Returns:
        Generated subscription ID
    """
    timestamp = int(datetime.utcnow().timestamp())
    # Simple hash of the combination (in production, use proper hashing)
    import hashlib
    combined = f"{user_id}_{plan_id}_{timestamp}"
    hash_obj = hashlib.md5(combined.encode())
    short_hash = hash_obj.hexdigest()[:8]
    
    return f"sub_{short_hash}_{timestamp}"


def calculate_subscription_proration(
    current_subscription: Dict[str, Any],
    new_plan_price: float,
    current_period_end: datetime,
    new_plan_id: str
) -> Dict[str, Any]:
    """
    Calculate subscription proration when changing plans
    
    Args:
        current_subscription: Current subscription data
        new_plan_price: New plan monthly price
        current_period_end: Current billing period end date
        new_plan_id: New plan identifier
        
    Returns:
        Proration calculation results
    """
    try:
        now = datetime.utcnow()
        period_days = (current_period_end - now).days
        remaining_days = (current_period_end - now).total_seconds() / (24 * 3600)
        
        if period_days <= 0:
            return {
                "proration_amount": 0.0,
                "credit_amount": 0.0,
                "immediate_charge": new_plan_price,
                "next_billing_date": current_period_end + timedelta(days=30)
            }
        
        current_plan_price = current_subscription.get("price", 0.0)
        remaining_months = remaining_days / 30.0
        
        # Calculate credit for unused time on current plan
        credit_amount = current_plan_price * remaining_months
        
        # Calculate charge for new plan
        immediate_charge = new_plan_price
        
        # Net proration amount
        proration_amount = immediate_charge - credit_amount
        
        return {
            "proration_amount": round(proration_amount, 2),
            "credit_amount": round(credit_amount, 2),
            "immediate_charge": round(immediate_charge, 2),
            "remaining_days": round(remaining_days),
            "current_period_end": current_period_end.isoformat(),
            "next_billing_date": (current_period_end + timedelta(days=30)).isoformat(),
            "change_effective": "next_period" if proration_amount > 0 else "immediate"
        }
        
    except Exception as e:
        logger.error(f"Error calculating proration: {e}")
        return {
            "proration_amount": 0.0,
            "credit_amount": 0.0,
            "immediate_charge": new_plan_price,
            "error": str(e)
        }


def get_subscription_features(plan_id: str) -> List[str]:
    """
    Get features list for a subscription plan
    
    Args:
        plan_id: Plan identifier
        
    Returns:
        List of plan features
    """
    return SUBSCRIPTION_FEATURES.get(plan_id.lower(), [])


def format_datetime(dt: datetime, format_type: str = "iso") -> str:
    """
    Format datetime in various formats
    
    Args:
        dt: Datetime object to format
        format_type: Format type ('iso', 'human', 'date', 'time')
        
    Returns:
        Formatted datetime string
    """
    if not isinstance(dt, datetime):
        return str(dt)
    
    try:
        if format_type == "iso":
            return dt.isoformat() + "Z"
        elif format_type == "human":
            return dt.strftime("%B %d, %Y at %I:%M %p UTC")
        elif format_type == "date":
            return dt.strftime("%Y-%m-%d")
        elif format_type == "time":
            return dt.strftime("%H:%M:%S")
        elif format_type == "datetime":
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return dt.isoformat() + "Z"
            
    except Exception as e:
        logger.error(f"Error formatting datetime: {e}")
        return str(dt)


def parse_iso_datetime(iso_string: str) -> Optional[datetime]:
    """
    Parse ISO datetime string to datetime object
    
    Args:
        iso_string: ISO formatted datetime string
        
    Returns:
        Parsed datetime object or None if parsing fails
    """
    if not iso_string:
        return None
    
    try:
        # Remove 'Z' suffix if present
        if iso_string.endswith('Z'):
            iso_string = iso_string[:-1]
        
        return datetime.fromisoformat(iso_string)
        
    except ValueError as e:
        logger.error(f"Error parsing datetime '{iso_string}': {e}")
        return None


def calculate_monthly_revenue(active_subscriptions: List[Dict[str, Any]]) -> float:
    """
    Calculate total monthly recurring revenue
    
    Args:
        active_subscriptions: List of active subscription data
        
    Returns:
        Total monthly revenue
    """
    try:
        total_revenue = 0.0
        
        for subscription in active_subscriptions:
            if subscription.get("status") == "active":
                price = subscription.get("price", 0.0)
                # Adjust for different billing periods
                interval = subscription.get("interval", "month")
                
                if interval == "year":
                    price = price / 12.0  # Convert to monthly
                elif interval == "week":
                    price = price * 4.33  # Convert to monthly
                
                total_revenue += price
        
        return round(total_revenue, 2)
        
    except Exception as e:
        logger.error(f"Error calculating monthly revenue: {e}")
        return 0.0


def get_subscription_metrics(subscriptions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate comprehensive subscription metrics
    
    Args:
        subscriptions: List of all subscriptions
        
    Returns:
        Subscription metrics dictionary
    """
    try:
        total = len(subscriptions)
        active = len([s for s in subscriptions if s.get("status") == "active"])
        cancelled = len([s for s in subscriptions if s.get("status") == "cancelled"])
        trial = len([s for s in subscriptions if s.get("trial_end") and s.get("status") == "trialing"])
        
        # Revenue calculations
        active_subscriptions = [s for s in subscriptions if s.get("status") == "active"]
        monthly_revenue = calculate_monthly_revenue(active_subscriptions)
        
        # Average revenue per user
        arpu = monthly_revenue / active if active > 0 else 0.0
        
        # Churn rate calculation (simplified)
        churn_rate = cancelled / total if total > 0 else 0.0
        
        # Plan breakdown
        plan_breakdown = {}
        for subscription in subscriptions:
            plan_id = subscription.get("plan_id", "unknown")
            plan_breakdown[plan_id] = plan_breakdown.get(plan_id, 0) + 1
        
        # Status breakdown
        status_breakdown = {}
        for subscription in subscriptions:
            status = subscription.get("status", "unknown")
            status_breakdown[status] = status_breakdown.get(status, 0) + 1
        
        return {
            "total_subscriptions": total,
            "active_subscriptions": active,
            "cancelled_subscriptions": cancelled,
            "trial_subscriptions": trial,
            "monthly_recurring_revenue": monthly_revenue,
            "average_revenue_per_user": round(arpu, 2),
            "churn_rate": round(churn_rate, 4),
            "plan_breakdown": plan_breakdown,
            "status_breakdown": status_breakdown,
            "calculated_at": datetime.utcnow().isoformat() + "Z"
        }
        
    except Exception as e:
        logger.error(f"Error calculating subscription metrics: {e}")
        return {
            "total_subscriptions": 0,
            "active_subscriptions": 0,
            "cancelled_subscriptions": 0,
            "monthly_recurring_revenue": 0.0,
            "average_revenue_per_user": 0.0,
            "churn_rate": 0.0,
            "error": str(e)
        }


def safe_get_nested(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Safely get nested dictionary value using dot notation
    
    Args:
        data: Dictionary to search
        key_path: Dot-separated key path (e.g., 'user.profile.name')
        default: Default value if key not found
        
    Returns:
        Value at key path or default
    """
    try:
        keys = key_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
        
    except Exception as e:
        logger.error(f"Error getting nested value '{key_path}': {e}")
        return default