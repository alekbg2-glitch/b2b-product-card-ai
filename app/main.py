import os
import json
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from app.config import settings
from app.schemas import ProductInput, GeneratedCard
from app.generator import CardGeneratorService

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-помощник для генерации карточек товаров КИПиА"
)

# Подключение статических файлов (CSS / JS)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Шаблоны Jinja2
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

# Инициализация сервиса
generator_service = CardGeneratorService()

@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    """Главная страница веб-интерфейса"""
    return templates.TemplateResponse("index.html", {"request": request, "app_name": settings.app_name})

@app.get("/api/samples/{product_id}")
async def get_sample_product(product_id: str):
    """Получение образцов входных данных (Товар 1 или Товар 2)"""
    sample_file = BASE_DIR / "samples" / f"{product_id}_oven.json" if product_id == "product_1" else BASE_DIR / "samples" / f"{product_id}_manotom.json"
    
    if not sample_file.exists():
        raise HTTPException(status_code=404, detail="Образец товара не найден")
    
    try:
        with open(sample_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка чтения образца: {str(e)}")

@app.post("/api/generate", response_model=GeneratedCard)
async def generate_product_card(product: ProductInput):
    """API-эндпоинт генерации карточки товара через LLM"""
    if not product.name or not product.name.strip():
        raise HTTPException(status_code=400, detail="Поле 'name' (название прибора) обязательно для заполнения")
    
    try:
        card = await generator_service.generate_card(product)
        return card
    except ValueError as val_err:
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as err:
        logger.error(f"Error during card generation: {str(err)}")
        raise HTTPException(status_code=500, detail=f"Ошибка генерации карточки: {str(err)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
