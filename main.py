import os
import json
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="BJU Calculator API")

# --- НАСТРОЙКА CORS ---
# Это позволяет твоему фронтенду делать запросы к этому API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # В продакшене лучше заменить на конкретный домен твоего фронтенда
    allow_credentials=True,
    allow_methods=["*"], # Разрешить все методы (GET, POST и т.д.)
    allow_headers=["*"], # Разрешить все заголовки
)

# Берем ключ из переменных окружения Render
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-3-flash-preview') 


class ProductRequest(BaseModel):
    ingredients: str

@app.post("/calculate")
async def calculate_bju(request: ProductRequest):
    system_instruction = """
    Ты — эксперт по диетологии. Анализируй ввод.
    ОТВЕТЬ СТРОГО В ФОРМАТЕ JSON:
    {
      "status": "success" или "error",
      "message": "сообщение",
      "data": {
          "calories": 0, "protein": 0, "fat": 0, "carbs": 0,
          "percentages": { "p_pct": 0, "f_pct": 0, "c_pct": 0 }
      }
    }
    """
    
    try:
        # Проверяем наличие ключа
        if not API_KEY:
             return {"status": "error", "message": "API Key is missing on server"}

        prompt = f"{system_instruction}\n\nПользователь ввел: {request.ingredients}"
        response = model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "application/json",
                "temperature": 0.0  
            }
        )
        
        return json.loads(response.text)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))