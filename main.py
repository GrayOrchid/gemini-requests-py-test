import os
import json
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="BJU Calculator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

class ProductRequest(BaseModel):
    ingredients: str

@app.post("/calculate")
async def calculate_bju(request: ProductRequest):
    system_instruction = """
    Ты — эксперт по диетологии. 
    ОТВЕТЬ СТРОГО В JSON:
    {
      "ingredients": [
        {"name": "название", "calories": 0, "protein": 0, "fat": 0, "carbs": 0}
      ],
      "total": {"calories": 0, "protein": 0, "fat": 0, "carbs": 0},
      "health_assessment": 0,
      "reason": "краткое объяснение полезности"
    }
    """
    
    try:
        if not API_KEY:
            raise HTTPException(status_code=500, detail="API Key missing")

        prompt = f"{system_instruction}\n\nПользователь: {request.ingredients}"
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json", "temperature": 0.1}
        )
        
        data = json.loads(response.text)
        
        # Извлекаем оценку и считаем цвет
        score = data.get("health_assessment", 0)
        
        if score < 4:
            color = "red"
        elif score < 7:
            color = "yellow"
        else:
            color = "green"
            
        # Добавляем цвет в корень ответа для удобства
        data["color"] = color
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))