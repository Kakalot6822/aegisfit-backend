# AEGIS FIT Backend API

AI-powered fitness application backend built with FastAPI, Supabase, and OpenAI.

## 🚀 Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

## 📋 Environment Variables

Required environment variables:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-role-key
OPENAI_API_KEY=your-openai-api-key
```

## 🛠️ Local Development

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your credentials
nano .env

# Run server
python3 main.py
```

Server will run at `http://localhost:8000`

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔗 API Endpoints

### Health Check
```
GET /health
```

### Users
```
POST /api/v1/users
GET /api/v1/users/{user_id}
```

### Blueprint
```
POST /api/v1/blueprint
```

### Workouts
```
POST /api/v1/workouts
GET /api/v1/workouts/{user_id}
```

### Leaderboard
```
GET /api/v1/leaderboard?limit=10
```

## 🏗️ Tech Stack

- **Framework**: FastAPI
- **Database**: Supabase (PostgreSQL)
- **AI**: OpenAI GPT-3.5/4
- **Deployment**: Railway

## 📄 License

MIT License
