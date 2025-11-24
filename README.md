# AEGIS FIT Backend API

Backend API for AEGIS FIT fitness tracking application built with FastAPI.

## 🚀 Features

- **FastAPI Framework**: High-performance async API framework
- **Subscription Management**: Handle different subscription plans
- **Stripe Integration**: Payment processing and webhook handling
- **Health Monitoring**: Built-in health check endpoints
- **API Documentation**: Auto-generated Swagger/OpenAPI docs
- **CORS Support**: Configurable cross-origin resource sharing
- **Environment Configuration**: Flexible environment variable setup
- **Error Handling**: Comprehensive error handling and logging
- **Data Validation**: Pydantic models for request/response validation

## 📁 Project Structure

```
aegis-fit-backend/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── models/             # Data models
├── routes/             # API route handlers
├── services/           # Business logic services
├── utils/              # Helper utilities
└── README.md           # This documentation
```

## 🔧 Installation

### Prerequisites

- Python 3.8+
- pip or uv package manager

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd aegis-fit-backend
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your actual values
```

4. **Run the application**
```bash
python main.py
```

For production with Gunicorn:
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🌐 API Endpoints

### Core Endpoints

#### Health Check
- **GET** `/` - Root endpoint with service information
- **GET** `/health` - Health check endpoint
- **GET** `/api/info` - API information and configuration

#### Subscription Management
- **GET** `/subscription/plans` - Get all available subscription plans
- **POST** `/subscription/create` - Create a new subscription
- **POST** `/subscription/webhook` - Handle Stripe webhooks

### Response Format

All API responses follow a consistent format:

```json
{
  "status": "healthy",
  "service": "AEGIS FIT Backend",
  "version": "1.0.0",
  "timestamp": "2025-11-24T11:17:26.000Z",
  "stripe_enabled": true
}
```

Error responses:
```json
{
  "error": true,
  "message": "Detailed error message",
  "status_code": 400,
  "timestamp": "2025-11-24T11:17:26.000Z"
}
```

## 💳 Subscription Plans

### Free Plan
- Basic workout tracking
- Limited progress analytics
- Community access
- Mobile app access

### Premium Plan ($9.99/month)
- Unlimited workout tracking
- Advanced progress analytics
- Personalized workout plans
- Nutrition tracking
- Priority support
- Export data
- Multiple device sync

### Professional Plan ($19.99/month)
- Everything in Premium
- Personal trainer consultations
- Custom meal plans
- Advanced body composition analysis
- API access for integrations
- Team/coach dashboard
- White-label options

## 🔐 Environment Variables

### Required

```env
SECRET_KEY=aegis-fit-2024-super-secret-jwt-key
CORS_ORIGINS=http://localhost:3000,https://your-app.vercel.app
DATABASE_URL=sqlite:///./aegis_fit.db
```

### Stripe (Optional)

```env
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
```

### Optional

```env
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=false
```

## 🚀 Deployment

### Render.com Deployment

1. **Connect GitHub repository** to Render
2. **Set build command**: `pip install -r requirements.txt`
3. **Set start command**: `python -m uvicorn main:app --host 0.0.0.0 --port 8000`
4. **Add environment variables** in Render dashboard
5. **Deploy** and wait for successful deployment

### Environment Variables in Render

Add these in Render dashboard > Settings > Environment:

- `SECRET_KEY`: Your secret key
- `CORS_ORIGINS`: Your frontend domains
- `STRIPE_SECRET_KEY`: Your Stripe secret key (optional)
- `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key (optional)
- `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook secret (optional)

## 🧪 Testing

### Health Check
```bash
curl https://your-app.onrender.com/health
```

### Subscription Plans
```bash
curl https://your-app.onrender.com/subscription/plans
```

### API Documentation
Visit: `https://your-app.onrender.com/docs`

### Create Subscription
```bash
curl -X POST https://your-app.onrender.com/subscription/create \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": "premium",
    "user_id": "user_123"
  }'
```

## 🔧 Development

### Running with Auto-reload
```bash
python main.py
```

### Code Formatting
```bash
black .
isort .
```

### Running Tests
```bash
pytest
```

## 📊 Monitoring

### Health Status
The API provides comprehensive health monitoring:

- **Service Status**: Check if the service is running
- **Stripe Integration**: Monitor if Stripe is properly configured
- **Timestamp**: Track when the health check was performed
- **Version Information**: Track API version

### Logging
- Structured logging with configurable levels
- Request/response logging
- Error tracking and monitoring
- Performance metrics

## 🔒 Security Features

- **CORS Configuration**: Configurable cross-origin policies
- **Secret Key Management**: Secure JWT token handling
- **Input Validation**: Pydantic models for all inputs
- **Error Handling**: Secure error messages without sensitive data
- **Rate Limiting**: Configurable rate limiting (optional)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

- **Documentation**: Check `/docs` endpoint for API documentation
- **Health Check**: Use `/health` to verify service status
- **Environment**: Use `/api/info` to check configuration status

## 🔄 Updates

### v1.0.0
- Initial release with basic subscription management
- Stripe integration support
- Health monitoring endpoints
- CORS configuration
- Comprehensive error handling