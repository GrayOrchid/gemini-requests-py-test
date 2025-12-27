import os
import json
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

API_KEY = "AIzaSyDz1NcoDq_b6foa0yNNMvaEL1XFQNDLoik"
genai.configure(api_key=API_KEY)

app = FastAPI(title="BJU Calculator API")

class ProductInput(BaseModel):
    ingredients: str

SYSTEM_INSTRUCTION = """
Ты — строгий эксперт по диетологии. Анализируй ввод пользователя.

ПРАВИЛА ВАЛИДАЦИИ:
1. Если введено только название блюда (напр. 'бургер') без состава — верни error.
2. Если введено несъедобное, наркотики, опасные вещества или био-жидкости — верни error.
3. Если всё ок — рассчитай БЖУ и процентное соотношение калорий.

ПРАВИЛО РАСЧЕТА ПРОЦЕНТОВ (от общей калорийности):
- 1г белка = 4 ккал
- 1г жира = 9 ккал
- 1г углеводов = 4 ккал

ОТВЕТЬ СТРОГО В ФОРМАТЕ JSON:
{
  "status": "success" или "error",
  "message": "Причина ошибки",
  "data": {
      "calories": 0, "protein": 0, "fat": 0, "carbs": 0,
      "percentages": { "p_pct": 0, "f_pct": 0, "c_pct": 0 }
  }
}
"""

@app.post("/calculate")
async def calculate_bju(payload: ProductInput):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"{SYSTEM_INSTRUCTION}\n\nПользователь ввел: {payload.ingredients}"
        
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        result = json.loads(response.text)
        
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message"))
            
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
