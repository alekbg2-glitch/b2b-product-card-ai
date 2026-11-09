import json
import logging
from typing import Dict, Any, List
import httpx
from app.config import settings
from app.schemas import ProductInput, GeneratedCard, CommercialBlock

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Ты — ведущий эксперт по техническому копирайтингу, B2B-маркетингу и контенту контрольно-измерительных приборов и промышленной автоматики.
Твоя задача — на основе предоставленных входных данных составить профессиональный черновик карточки товара для B2B-интернет-магазина промышленного оборудования.

СТРОГИЕ ТРЕБОВАНИЯ И GUARDRAILS:
1. НИКАКИХ ГАЛЛЮЦИНАЦИЙ И ВЫДУМАННЫХ ПАРАМЕТРОВ! Все технические характеристики, диапазоны, классы точности, напряжения и резьбы должны браться ТОЛЬКО из входных данных.
2. Если в характеристиках параметр отсутствует или имеет значение 'данных нет', явно укажи 'данных нет' или сформулируй предупреждение.
3. SEO-заголовок (seo_title): емкий, продающий, релевантный, строго ДО 70 символов включительно!
4. SEO-описание (seo_description): профессиональный B2B-текст объёмом СТРОГО от 800 до 1200 символов (без лишней воды, с акцентом на надежность, сферы применения и совместимость).
5. Поисковые запросы (search_queries): ровно 3-5 высококонверсионных B2B-запросов (например, с моделью, производителем и типом прибора).
6. Commercial-блок:
   - target_audience: четко указать, кому подходит прибор (отрасли, инженеры КИПиА, технологи, проектировщики, котельные и т.д.).
   - key_tasks_solved: 3-4 конкретные задачи, которые прибор решает на объекте.
   - competitive_advantages: 2-4 сильные стороны (надежность, интерфейсы, гибкость монтажа).
7. Список предупреждений (missing_data_warnings): проанализируй входные данные. Если для полноценного паспорта товара не хватает важных для инженера полей (например: степень защиты IP, диапазон температур, сертификация/поверка, присоединительная резьба, вес/габариты), обязательно перечисли их!

ФОРМАТ ОТВЕТА:
Отвечай СТРОГО в формате валидного JSON без markdown-оберток (```json ... ``` не нужны, только сырой JSON).
Структура JSON:
{
  "seo_title": "Строка до 70 символов",
  "seo_description": "Текст описания от 800 до 1200 символов",
  "structured_specs": {
    "название характеристики": "значение строго из входа или 'данных нет'"
  },
  "search_queries": [
    "запрос 1", "запрос 2", "запрос 3", "запрос 4"
  ],
  "commercial_block": {
    "target_audience": "Кому подходит...",
    "key_tasks_solved": ["задача 1", "задача 2", "задача 3"],
    "competitive_advantages": ["преимущество 1", "преимущество 2"]
  },
  "missing_data_warnings": [
    "предупреждение 1 (если есть)"
  ]
}
"""

def generate_markdown_representation(data: Dict[str, Any], raw_input: ProductInput) -> str:
    """Генерация готового для контент-менеджера Markdown документа."""
    specs_lines = "\n".join([f"- **{k}:** {v}" for k, v in data.get("structured_specs", {}).items()])
    queries_lines = "\n".join([f"- `{q}`" for q in data.get("search_queries", [])])
    
    comm = data.get("commercial_block", {})
    tasks_lines = "\n".join([f"  * {t}" for t in comm.get("key_tasks_solved", [])])
    adv_lines = "\n".join([f"  * {a}" for a in comm.get("competitive_advantages", [])])
    
    warnings = data.get("missing_data_warnings", [])
    warnings_block = ""
    if warnings:
        w_items = "\n".join([f"> ⚠️ **Требует уточнения:** {w}" for w in warnings])
        warnings_block = f"\n### ⚠️ Замечания для контент-менеджера\n{w_items}\n"

    desc = data.get("seo_description", "")
    title = data.get("seo_title", "")
    
    md = f"""# {raw_input.name}
**Производитель:** {raw_input.manufacturer or "данных нет"}

---

### 🔍 SEO-блок
- **SEO Title ({len(title)}/70 символов):** `{title}`
- **Поисковые запросы:**
{queries_lines}

---

### 📝 Описание товара ({len(desc)} знаков)
{desc}

---

### ⚙️ Ключевые технические характеристики
{specs_lines}

---

### 💼 Коммерческий блок для отдела продаж
- **Целевая аудитория и сферы применения:** {comm.get('target_audience', 'данных нет')}
- **Решаемые задачи:**
{tasks_lines}
- **Ключевые преимущества оборудования:**
{adv_lines}
{warnings_block}
"""
    return md

class CardGeneratorService:
    def __init__(self):
        self.api_key = settings.llm_api_key
        self.base_url = settings.llm_base_url.rstrip("/")
        self.model = settings.llm_model

    async def generate_card(self, product: ProductInput) -> GeneratedCard:
        prompt_input = {
            "name": product.name,
            "manufacturer": product.manufacturer,
            "specs": product.specs,
            "raw_description": product.description
        }
        
        user_message = f"Входные данные по товару КИПиА:\n```json\n{json.dumps(prompt_input, ensure_ascii=False, indent=2)}\n```\nСформируй черновик карточки товара согласно системным требованиям."
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.2
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                result_json = response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error from LLM API: {e.response.status_code} - {e.response.text}")
                raise RuntimeError(f"Ошибка API языковой модели ({e.response.status_code}): {e.response.text}")
            except Exception as e:
                logger.error(f"Failed to connect to LLM API: {str(e)}")
                raise RuntimeError(f"Не удалось связаться с API LLM: {str(e)}")

        try:
            content = result_json["choices"][0]["message"]["content"].strip()
            # Очистка возможных markdown-тегов ```json
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            parsed = json.loads(content)
        except Exception as e:
            logger.error(f"Failed to parse LLM response as JSON: {content}")
            raise ValueError(f"Модель вернула некорректный JSON: {str(e)}")

        # Валидация длин
        seo_title = parsed.get("seo_title", "").strip()
        seo_desc = parsed.get("seo_description", "").strip()
        
        comm_data = parsed.get("commercial_block", {})
        comm_block = CommercialBlock(
            target_audience=comm_data.get("target_audience", "Промышленные предприятия и инженеры КИПиА"),
            key_tasks_solved=comm_data.get("key_tasks_solved", []),
            competitive_advantages=comm_data.get("competitive_advantages", [])
        )
        
        raw_md = generate_markdown_representation(parsed, product)
        
        return GeneratedCard(
            seo_title=seo_title,
            seo_title_length=len(seo_title),
            seo_description=seo_desc,
            seo_description_length=len(seo_desc),
            structured_specs=parsed.get("structured_specs", {}),
            search_queries=parsed.get("search_queries", []),
            commercial_block=comm_block,
            missing_data_warnings=parsed.get("missing_data_warnings", []),
            raw_markdown=raw_md
        )
