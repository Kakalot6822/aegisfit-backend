"""
API route handlers for AEGIS FIT Backend
"""

from .health import health_router
from .subscription import subscription_router

__all__ = ["health_router", "subscription_router"]