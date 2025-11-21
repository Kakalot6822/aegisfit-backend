"""
AEGIS FIT - Backend API Server
FastAPI + Supabase + AI Integration
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import os
import json
import hashlib
from datetime import datetime, timedelta
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aegis-fit.com",
        "https://www.aegis-fit.com",
        "https://aegis-fit.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

    title="AEGIS FIT API",
    description="AI-Powered Fitness Platform",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment Variables
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ================== Models ==================

class UserCreate(BaseModel):
    email: EmailStr
    age: int
    weight: float
    height: float
    goal: str  # 'healthy', 'toned', 'elite'

class BlueprintRequest(BaseModel):
    user_id: str
    goal: str
    age: int
    weight: float
    height: float
    activity_level: str = "moderate"

class WorkoutLog(BaseModel):
    user_id: str
    workout_type: str
    duration: int
    exercises: List[dict]
    is_personal_record: bool = False

# ================== Helper Functions ==================

async def supabase_request(method: str, endpoint: str, data: dict = None):
    """Make request to Supabase REST API"""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=data)
        elif method == "PATCH":
            response = await client.patch(url, headers=headers, json=data)
        
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        
        # Handle empty response
        if not response.text:
            return {}
        
        try:
            return response.json()
        except:
            return {"raw_response": response.text}

def calculate_bmr_tdee(age: int, weight: float, height: float, gender: str = "male", activity: str = "moderate"):
    """Calculate BMR and TDEE"""
    # Mifflin-St Jeor Equation
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
    
    # Activity multipliers
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    
    tdee = bmr * activity_multipliers.get(activity, 1.55)
    
    return {
        "bmr": round(bmr),
        "tdee": round(tdee)
    }

def generate_cache_key(user_data: dict, goal: str) -> str:
    """Generate cache key for AI responses"""
    data_str = f"{user_data['age']}_{user_data['weight']}_{user_data['height']}_{goal}"
    return hashlib.md5(data_str.encode()).hexdigest()

async def generate_ai_blueprint(user_data: dict, goal: str) -> dict:
    """Generate workout blueprint using AI"""
    
    # Calculate user stats
    stats = calculate_bmr_tdee(
        age=user_data['age'],
        weight=user_data['weight'],
        height=user_data['height']
    )
    
    # AI Prompt
    prompt = f"""คุณเป็นเทรนเนอร์มืออาชีพ สร้างแผนออกกำลังกาย 12 สัปดาห์สำหรับ:

เป้าหมาย: {goal}
อายุ: {user_data['age']} ปี
น้ำหนัก: {user_data['weight']} kg
ส่วนสูง: {user_data['height']} cm
TDEE: {stats['tdee']} kcal/วัน

สร้างแผนใน JSON format:
{{
  "program_name": "ชื่อโปรแกรม",
  "duration_weeks": 12,
  "weekly_schedule": {{
    "monday": [{{"exercise": "ชื่อท่า", "sets": 3, "reps": 10}}],
    "wednesday": [...],
    "friday": [...]
  }},
  "nutrition": {{
    "protein_g": 150,
    "carbs_g": 200,
    "fat_g": 60,
    "calories": {stats['tdee']}
  }},
  "milestones": [
    {{"week": 4, "goal": "เป้าหมายสัปดาห์ที่ 4"}},
    {{"week": 8, "goal": "เป้าหมายสัปดาห์ที่ 8"}},
    {{"week": 12, "goal": "เป้าหมายสุดท้าย"}}
  ]
}}

ตอบเป็น JSON เท่านั้น ไม่ต้องมีคำอธิบายเพิ่มเติม"""

    # Call OpenAI API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "คุณเป็นเทรนเนอร์มืออาชีพที่ตอบเป็น JSON เท่านั้น"},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="AI service error")
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Parse JSON from response
            try:
                blueprint = json.loads(content)
            except json.JSONDecodeError:
                # If not valid JSON, create fallback
                blueprint = create_fallback_blueprint(goal, stats)
            
            return blueprint
            
    except Exception as e:
        # Fallback to template-based blueprint
        return create_fallback_blueprint(goal, stats)

def create_fallback_blueprint(goal: str, stats: dict) -> dict:
    """Create fallback blueprint when AI fails"""
    
    templates = {
        "healthy": {
            "program_name": "Healthy Start - 12 สัปดาห์",
            "weekly_schedule": {
                "monday": [
                    {"exercise": "Walking", "duration": "30 min", "intensity": "moderate"},
                    {"exercise": "Bodyweight Squat", "sets": 3, "reps": 12},
                    {"exercise": "Push-up", "sets": 3, "reps": 10}
                ],
                "wednesday": [
                    {"exercise": "Cycling", "duration": "30 min", "intensity": "moderate"},
                    {"exercise": "Plank", "sets": 3, "duration": "30 sec"},
                    {"exercise": "Lunges", "sets": 3, "reps": 10}
                ],
                "friday": [
                    {"exercise": "Swimming", "duration": "30 min", "intensity": "light"},
                    {"exercise": "Mountain Climbers", "sets": 3, "reps": 15},
                    {"exercise": "Stretching", "duration": "10 min"}
                ]
            }
        },
        "toned": {
            "program_name": "Toned & Fit - 12 สัปดาห์",
            "weekly_schedule": {
                "monday": [
                    {"exercise": "Bench Press", "sets": 3, "reps": 10},
                    {"exercise": "Dumbbell Row", "sets": 3, "reps": 10},
                    {"exercise": "Shoulder Press", "sets": 3, "reps": 10}
                ],
                "wednesday": [
                    {"exercise": "Squat", "sets": 4, "reps": 10},
                    {"exercise": "Leg Press", "sets": 3, "reps": 12},
                    {"exercise": "Leg Curl", "sets": 3, "reps": 12}
                ],
                "friday": [
                    {"exercise": "Deadlift", "sets": 3, "reps": 8},
                    {"exercise": "Pull-up", "sets": 3, "reps": "AMRAP"},
                    {"exercise": "Bicep Curl", "sets": 3, "reps": 12}
                ]
            }
        },
        "elite": {
            "program_name": "Aesthetic Elite - 12 สัปดาห์",
            "weekly_schedule": {
                "monday": [
                    {"exercise": "Bench Press", "sets": 4, "reps": 8},
                    {"exercise": "Incline Dumbbell Press", "sets": 4, "reps": 10},
                    {"exercise": "Cable Fly", "sets": 3, "reps": 12},
                    {"exercise": "Tricep Dips", "sets": 3, "reps": 12}
                ],
                "tuesday": [
                    {"exercise": "Squat", "sets": 5, "reps": 5},
                    {"exercise": "Romanian Deadlift", "sets": 4, "reps": 8},
                    {"exercise": "Leg Extension", "sets": 3, "reps": 15},
                    {"exercise": "Calf Raise", "sets": 4, "reps": 20}
                ],
                "thursday": [
                    {"exercise": "Deadlift", "sets": 4, "reps": 6},
                    {"exercise": "Barbell Row", "sets": 4, "reps": 8},
                    {"exercise": "Lat Pulldown", "sets": 3, "reps": 12},
                    {"exercise": "Barbell Curl", "sets": 3, "reps": 10}
                ],
                "friday": [
                    {"exercise": "Overhead Press", "sets": 4, "reps": 8},
                    {"exercise": "Lateral Raise", "sets": 4, "reps": 12},
                    {"exercise": "Face Pull", "sets": 3, "reps": 15},
                    {"exercise": "Abs Circuit", "sets": 3, "duration": "5 min"}
                ]
            }
        }
    }
    
    template = templates.get(goal, templates["toned"])
    
    return {
        "program_name": template["program_name"],
        "duration_weeks": 12,
        "weekly_schedule": template["weekly_schedule"],
        "nutrition": {
            "protein_g": int(stats['tdee'] * 0.3 / 4),
            "carbs_g": int(stats['tdee'] * 0.4 / 4),
            "fat_g": int(stats['tdee'] * 0.3 / 9),
            "calories": stats['tdee']
        },
        "milestones": [
            {"week": 4, "goal": "สร้างนิสัยการออกกำลังกาย"},
            {"week": 8, "goal": "เห็นการเปลี่ยนแปลงของร่างกาย"},
            {"week": 12, "goal": "บรรลุเป้าหมายที่ตั้งไว้"}
        ]
    }

# ================== API Endpoints ==================

@app.get("/")
async def root():
    return {
        "name": "AEGIS FIT API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "supabase": "connected" if SUPABASE_URL else "not_configured",
            "openai": "configured" if OPENAI_API_KEY else "not_configured"
        }
    }

@app.post("/api/v1/users")
async def create_user(user: UserCreate):
    """Create new user"""
    
    user_data = {
        "email": user.email,
        "age": user.age,
        "weight": user.weight,
        "height": user.height,
        "goal": user.goal,
        "total_vp": 0,
        "streak_days": 0
    }
    
    try:
        result = await supabase_request("POST", "users", user_data)
        return {
            "status": "success",
            "data": result
        }
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise e
    except Exception as e:
        # Log other exceptions
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.post("/api/v1/blueprint")
async def create_blueprint(request: BlueprintRequest):
    """Generate AI workout blueprint"""
    
    # Check cache first (in production, use Redis)
    cache_key = generate_cache_key(
        {"age": request.age, "weight": request.weight, "height": request.height},
        request.goal
    )
    
    # Generate blueprint
    blueprint = await generate_ai_blueprint(
        {
            "age": request.age,
            "weight": request.weight,
            "height": request.height,
            "activity_level": request.activity_level
        },
        request.goal
    )
    
    # Save to database
    plan_data = {
        "user_id": request.user_id,
        "blueprint": blueprint,
        "generated_at": datetime.now().isoformat()
    }
    
    try:
        await supabase_request("POST", "workout_plans", plan_data)
    except:
        pass  # Continue even if save fails
    
    return {
        "status": "success",
        "data": blueprint,
        "cache_key": cache_key,
        "generated_at": datetime.now().isoformat()
    }

@app.post("/api/v1/workouts")
async def log_workout(workout: WorkoutLog):
    """Log workout and calculate VP"""
    
    # Calculate VP
    base_vp = 10
    bonus_vp = 0
    
    if workout.is_personal_record:
        bonus_vp += 50
    
    if workout.duration >= 60:
        bonus_vp += 25
    
    total_vp = base_vp + bonus_vp
    
    # Save workout log
    workout_data = {
        "user_id": workout.user_id,
        "workout_type": workout.workout_type,
        "duration": workout.duration,
        "exercises": workout.exercises,
        "vp_earned": total_vp,
        "created_at": datetime.now().isoformat()
    }
    
    # Update user VP (in production, use database function)
    try:
        # This would call Supabase RPC function
        return {
            "status": "success",
            "vp_earned": total_vp,
            "message": f"ยอดเยี่ยม! คุณได้รับ {total_vp} VP"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/leaderboard")
async def get_leaderboard(limit: int = 100):
    """Get leaderboard"""
    
    try:
        result = await supabase_request(
            "GET",
            f"users?select=email,total_vp,streak_days&order=total_vp.desc&limit={limit}"
        )
        
        # Add rankings
        leaderboard = []
        for idx, user in enumerate(result, 1):
            leaderboard.append({
                "rank": idx,
                "email": user["email"],
                "total_vp": user["total_vp"],
                "streak_days": user["streak_days"]
            })
        
        return {
            "status": "success",
            "data": leaderboard
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/users/{user_id}/stats")
async def get_user_stats(user_id: str):
    """Get user statistics"""
    
    try:
        # Get user data
        user = await supabase_request("GET", f"users?id=eq.{user_id}&select=*")
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user[0]
        
        # Calculate tier
        total_vp = user_data.get("total_vp", 0)
        streak_days = user_data.get("streak_days", 0)
        
        if total_vp >= 10000 and streak_days >= 60:
            tier = "ELITE"
        elif total_vp >= 5000 and streak_days >= 30:
            tier = "ADVANCED"
        elif total_vp >= 1000 and streak_days >= 7:
            tier = "INTERMEDIATE"
        else:
            tier = "ROOKIE"
        
        return {
            "status": "success",
            "data": {
                "user": user_data,
                "tier": tier,
                "next_tier_vp": {
                    "ROOKIE": 1000,
                    "INTERMEDIATE": 5000,
                    "ADVANCED": 10000,
                    "ELITE": None
                }.get(tier)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
