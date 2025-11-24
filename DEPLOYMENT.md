# AEGIS FIT Backend - Deployment Guide

## 🚀 Quick Deployment on Render.com

### Step 1: Prepare Your Repository

1. **Create GitHub Repository**
   - Go to GitHub and create a new repository
   - Name: `aegis-fit-backend`
   - Upload all files from this project to the repository

2. **Verify File Structure**
```
aegis-fit-backend/
├── main.py
├── config.py
├── requirements.txt
├── .env.example
├── README.md
├── models/
├── routes/
├── services/
├── utils/
├── test-api.sh
├── Dockerfile
├── docker-compose.yml
└── .gitignore
```

### Step 2: Deploy on Render.com

1. **Login to Render**
   - Go to https://render.com
   - Sign in with your GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `aegis-fit-backend` repository

3. **Configure Web Service**
   
   **Basic Settings:**
   - Name: `aegis-fit-backend`
   - Region: Choose closest to your users
   - Branch: `main`
   - Root Directory: Leave empty
   
   **Build and Deploy:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python -m uvicorn main:app --host 0.0.0.0 --port 8000`
   
   **Environment Variables:**
   Add these in the Environment section:
   ```
   SECRET_KEY=aegis-fit-2024-super-secret-jwt-key
   CORS_ORIGINS=http://localhost:3000,https://your-frontend-url.vercel.app
   DATABASE_URL=sqlite:///./aegis_fit.db
   ENVIRONMENT=production
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete (3-5 minutes)
   - Get your service URL: `https://aegis-fit-backend.onrender.com`

### Step 3: Verify Deployment

1. **Test Endpoints**
   ```bash
   # Health check
   curl https://your-app.onrender.com/api/health
   
   # Get subscription plans
   curl https://your-app.onrender.com/subscription/plans
   
   # API info
   curl https://your-app.onrender.com/api/info
   ```

2. **Check API Documentation**
   - Visit: `https://your-app.onrender.com/docs`
   - Should see interactive API documentation

## 🔧 Environment Variables

### Required
- `SECRET_KEY`: Secret key for JWT tokens (generate a secure one)
- `CORS_ORIGINS`: Comma-separated list of allowed origins
- `DATABASE_URL`: Database connection string
- `ENVIRONMENT`: Set to `production`

### Optional (Stripe Integration)
- `STRIPE_SECRET_KEY`: Stripe secret key (sk_test_... or sk_live_...)
- `STRIPE_PUBLISHABLE_KEY`: Stripe publishable key (pk_test_... or pk_live_...)
- `STRIPE_WEBHOOK_SECRET`: Stripe webhook secret (whsec_...)

### Optional (Email)
- `SMTP_HOST`: SMTP server hostname
- `SMTP_PORT`: SMTP port (usually 587)
- `SMTP_USERNAME`: Email username
- `SMTP_PASSWORD`: Email password or app password

## 🧪 Testing Your Deployment

### Automated Testing
```bash
# Update API_BASE_URL in test-api.sh to your deployed URL
chmod +x test-api.sh
./test-api.sh
```

### Manual Testing
```bash
# Test all endpoints
curl https://your-app.onrender.com/
curl https://your-app.onrender.com/api/health
curl https://your-app.onrender.com/api/info
curl https://your-app.onrender.com/subscription/plans
curl -X POST https://your-app.onrender.com/subscription/create \
  -H "Content-Type: application/json" \
  -d '{"plan_id": "free", "user_id": "test_user_123"}'
```

### Browser Testing
- API Documentation: `https://your-app.onrender.com/docs`
- Health Check: `https://your-app.onrender.com/api/health`
- Subscription Plans: `https://your-app.onrender.com/subscription/plans`

## 📊 Monitoring

### Health Checks
- **Primary Health Check**: `/api/health`
- **Kubernetes Ready**: `/api/ready`
- **Kubernetes Live**: `/api/live`
- **Metrics**: `/api/metrics`
- **Detailed Status**: `/api/status`

### Logs
Check Render dashboard → Logs section for:
- Application startup messages
- Request/response logs
- Error logs
- Performance metrics

## 🔐 Security

### Production Security Checklist
- [ ] Change default `SECRET_KEY` to a secure random string
- [ ] Configure proper `CORS_ORIGINS` for your domain
- [ ] Set `ENVIRONMENT=production`
- [ ] Disable debug mode
- [ ] Use HTTPS (Render provides this automatically)
- [ ] Set up proper rate limiting if needed
- [ ] Configure Stripe webhook endpoints if using payments

### Stripe Webhook Setup
1. In Stripe Dashboard → Webhooks
2. Add endpoint: `https://your-app.onrender.com/subscription/webhook`
3. Select events to listen for:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

## 🐳 Alternative: Docker Deployment

### Build and Run Locally
```bash
# Build image
docker build -t aegis-fit-backend .

# Run container
docker run -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e CORS_ORIGINS=http://localhost:3000 \
  aegis-fit-backend
```

### Docker Compose
```bash
docker-compose up -d
```

## 🔄 Continuous Deployment

### Auto-Deploy on Git Push
1. Configure webhook in GitHub repository settings
2. Render will automatically deploy on `main` branch pushes
3. Check deployment status in Render dashboard

### Manual Deploy
1. Make code changes
2. Push to `main` branch
3. Render will automatically rebuild and deploy

## 📝 Troubleshooting

### Common Issues

**1. Service Not Starting**
- Check logs in Render dashboard
- Verify `start command` is correct
- Ensure all dependencies are in `requirements.txt`

**2. CORS Errors**
- Check `CORS_ORIGINS` environment variable
- Verify your frontend URL is included
- No trailing commas in the list

**3. Database Issues**
- Use SQLite for simple setup: `sqlite:///./aegis_fit.db`
- For production, consider PostgreSQL

**4. Stripe Integration**
- Verify all Stripe environment variables are set
- Check Stripe webhook configuration
- Test with test keys first

**5. Port Issues**
- Ensure app listens on `0.0.0.0:8000`
- Render provides `PORT` environment variable

### Getting Help
- Check `/api/info` endpoint for configuration status
- Review application logs in Render dashboard
- Test endpoints with provided test script
- Check API documentation at `/docs`

## 📈 Performance

### Optimization Tips
- Use connection pooling for database
- Implement caching for subscription plans
- Set up CDN for static assets
- Monitor response times in logs
- Consider Redis for session storage

### Monitoring Setup
- Render provides basic metrics
- Consider adding external monitoring (DataDog, New Relic)
- Set up alerts for high error rates
- Monitor API response times