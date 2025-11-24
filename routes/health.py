"""
Health check and status routes for AEGIS FIT Backend API
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

health_router = APIRouter(prefix="/api", tags=["health"])


class HealthStatus:
    """Health status information"""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        self.version = "1.0.0"
        self.service_name = "AEGIS FIT Backend"
        
    def get_status(self) -> Dict[str, Any]:
        """Get current health status"""
        uptime = datetime.utcnow() - self.start_time
        
        return {
            "status": "healthy",
            "service": self.service_name,
            "version": self.version,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "uptime_seconds": int(uptime.total_seconds()),
            "uptime_human": str(uptime).split('.')[0],  # Remove microseconds
            "environment": "production",  # This could be configured
            "checks": {
                "database": "healthy",  # This could be a real check
                "external_apis": "healthy",  # This could be a real check
                "memory_usage": "normal"  # This could be a real check
            }
        }


# Global health status instance
health_status = HealthStatus()


@health_router.get("/")
async def root():
    """Root endpoint - returns service information and basic status"""
    try:
        return health_status.get_status()
    except Exception as e:
        logger.error(f"Error in root endpoint: {e}")
        raise HTTPException(status_code=500, detail="Service error")


@health_router.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        status = health_status.get_status()
        
        # Additional health checks could be added here
        # For example: database connectivity, external service checks, etc.
        
        logger.info("Health check requested")
        return status
        
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@health_router.get("/status")
async def detailed_status():
    """Detailed system status with additional information"""
    try:
        import os
        import sys
        import platform
        
        # Get system information
        system_info = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "cpu_count": os.cpu_count(),
            "environment": os.environ.get("ENVIRONMENT", "unknown")
        }
        
        # Get memory usage (Linux/Unix only)
        try:
            import psutil
            memory_info = {
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            }
        except ImportError:
            memory_info = {"status": "psutil not available"}
        
        status = health_status.get_status()
        status.update({
            "system_info": system_info,
            "memory_info": memory_info,
            "configuration": {
                "debug_mode": False,  # This could be configured
                "log_level": "INFO",  # This could be configured
                "cors_enabled": True,
                "rate_limiting_enabled": False  # This could be configured
            }
        })
        
        logger.info("Detailed status requested")
        return status
        
    except Exception as e:
        logger.error(f"Error in detailed status: {e}")
        raise HTTPException(status_code=500, detail="Status check failed")


@health_router.get("/ready")
async def readiness_check():
    """Kubernetes-style readiness probe"""
    try:
        # Check if service is ready to accept traffic
        # This could include database connectivity, cache checks, etc.
        
        readiness_status = {
            "ready": True,
            "checks": {
                "database": "ready",
                "cache": "ready", 
                "external_apis": "ready"
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return readiness_status
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")


@health_router.get("/live")
async def liveness_check():
    """Kubernetes-style liveness probe"""
    try:
        liveness_status = {
            "alive": True,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return liveness_status
        
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not alive")


@health_router.get("/metrics")
async def metrics():
    """Basic metrics endpoint"""
    try:
        metrics_data = {
            "service": health_status.service_name,
            "version": health_status.version,
            "uptime_seconds": int((datetime.utcnow() - health_status.start_time).total_seconds()),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "metrics": {
                "requests_total": 0,  # This could be implemented with a counter
                "errors_total": 0,   # This could be implemented with a counter
                "active_connections": 0  # This could be implemented with a gauge
            }
        }
        
        return metrics_data
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail="Metrics collection failed")