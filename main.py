import os
import json
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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