# 🚀 AEGIS FIT Backend - Quick Start Guide

## ⚡ 3 ขั้นตอน Deploy

### 1️⃣ Upload to GitHub
```bash
# 1. สร้าง GitHub repository ใหม่
# 2. Upload ไฟล์ทั้งหมดไปยัง repository
# 3. ตรวจสอบโครงสร้างไฟล์ให้ครบ
```

### 2️⃣ Deploy on Render.com
```
🔗 Go to: https://render.com
✅ Connect GitHub repository  
⚙️ Build Command: pip install -r requirements.txt
🚀 Start Command: python -m uvicorn main:app --host 0.0.0.0 --port 8000
🔑 Add Environment Variables:
   - SECRET_KEY=aegis-fit-2024-super-secret-jwt-key
   - CORS_ORIGINS=http://localhost:3000,https://your-frontend-url.vercel.app
   - DATABASE_URL=sqlite:///./aegis_fit.db
   - ENVIRONMENT=production
🎯 Deploy!
```

### 3️⃣ Test Endpoints
```bash
# Health check
curl https://your-app.onrender.com/api/health

# Get subscription plans  
curl https://your-app.onrender.com/subscription/plans

# API documentation
# Visit: https://your-app.onrender.com/docs
```

## 🎯 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Root endpoint with service info |
| `/api/health` | GET | Health check |
| `/api/info` | GET | API information and configuration |
| `/subscription/plans` | GET | Get all subscription plans |
| `/subscription/create` | POST | Create new subscription |
| `/subscription/status/{user_id}` | GET | Get user subscription status |
| `/subscription/webhook` | POST | Stripe webhook handler |
| `/docs` | GET | API documentation (Swagger) |

## 💰 Subscription Plans

| Plan | Price | Features |
|------|-------|----------|
| **Free** | $0/month | Basic tracking, Limited analytics |
| **Premium** | $9.99/month | Unlimited tracking, Advanced analytics |
| **Pro** | $19.99/month | +Personal trainer, Custom meal plans |
| **Enterprise** | $99.99/month | +Unlimited users, Custom integrations |

## 🧪 Quick Test Commands

```bash
# Test 1: Health Check
curl https://aegis-fit.onrender.com/api/health

# Expected Response:
{
  "status": "healthy",
  "service": "AEGIS FIT Backend",
  "version": "1.0.0",
  "timestamp": "2025-11-24T11:17:26.000Z"
}

# Test 2: Get Subscription Plans
curl https://aegis-fit.onrender.com/subscription/plans

# Expected Response:
[
  {
    "id": "free",
    "name": "Free Plan", 
    "description": "Basic fitness tracking...",
    "price": 0.0,
    "features": [...]
  }
]

# Test 3: Create Subscription
curl -X POST https://aegis-fit.onrender.com/subscription/create \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "free", "user_id": "test_user_123"}'

# Expected Response:
{
  "success": true,
  "message": "Free subscription activated successfully",
  "subscription_id": "free_test_user_123_...",
  "plan_id": "free",
  "user_id": "test_user_123",
  "status": "active"
}
```

## 🔧 Environment Variables

### Minimum Required:
```env
SECRET_KEY=aegis-fit-2024-super-secret-jwt-key
CORS_ORIGINS=http://localhost:3000,https://your-frontend-url.vercel.app
DATABASE_URL=sqlite:///./aegis_fit.db
ENVIRONMENT=production
```

### Optional (for Stripe payments):
```env
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
```

## 🎯 Success Indicators

✅ **Service Running:** Health check returns 200 OK
✅ **API Working:** `/subscription/plans` returns plan list
✅ **Docs Available:** `/docs` shows interactive API docs
✅ **CORS Working:** Frontend can call API without errors

## 🚨 Troubleshooting

### ❌ "Service Unavailable" (503)
**Solution:** Check Render logs, verify start command

### ❌ "CORS Error" 
**Solution:** Add frontend URL to CORS_ORIGINS

### ❌ "Module Not Found"
**Solution:** Verify requirements.txt is in repository root

### ❌ "Environment Variable Not Set"
**Solution:** Add all required env vars in Render dashboard

## 📞 Support

- **API Documentation:** Visit `/docs` endpoint
- **Health Check:** Use `/api/health` endpoint  
- **Detailed Status:** Use `/api/status` endpoint
- **Logs:** Check Render dashboard → Logs section

## 🎉 You're Ready!

Your AEGIS FIT Backend is now deployed and ready to handle:
- ✅ Subscription management
- ✅ User registration
- ✅ Payment processing (with Stripe)
- ✅ Health monitoring
- ✅ API documentation

**Next Steps:**
1. Connect your frontend application
2. Configure Stripe for payments (optional)
3. Set up monitoring and alerts
4. Scale as needed!

🚀 **Happy Building! 🚀**