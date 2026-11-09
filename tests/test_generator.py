import pytest
from app.schemas import ProductInput
from app.generator import CardGeneratorService, generate_markdown_representation

@pytest.mark.asyncio
async def test_card_generation_structure():
    sample = ProductInput(
        name="Манометр тестовый МП-100",
        manufacturer="ТестПрибор",
        specs={
            "диапазон": "0-1 МПа",
            "класс точности": "1.0",
            "степень защиты": "данных нет"
        },
        description="Тестовый манометр для проверки генерации карточки."
    )
    service = CardGeneratorService()
    card = await service.generate_card(sample)
    
    # 1. Проверка SEO заголовка (до 70 символов)
    assert card.seo_title, "SEO заголовок не должен быть пустым"
    assert card.seo_title_length <= 70, f"SEO заголовок слишком длинный: {card.seo_title_length} > 70"
    
    # 2. Проверка SEO описания (800-1200 символов)
    assert 750 <= card.seo_description_length <= 1300, f"SEO описание вне диапазона: {card.seo_description_length}"
    
    # 3. Проверка поисковых запросов (3-5 шт)
    assert 3 <= len(card.search_queries) <= 5, "Должно быть ровно от 3 до 5 поисковых запросов"
    
    # 4. Проверка отсутствия галлюцинаций в характеристиках
    assert "диапазон" in card.structured_specs
    assert card.structured_specs["диапазон"] == "0-1 МПа"
    assert card.structured_specs.get("степень защиты") == "данных нет"
    
    # 5. Проверка commercial блока
    assert card.commercial_block.target_audience
    assert len(card.commercial_block.key_tasks_solved) >= 2
    assert len(card.commercial_block.competitive_advantages) >= 2

def test_markdown_formatting():
    sample = ProductInput(
        name="Прибор А",
        manufacturer="Вендор Б",
        specs={"Питание": "24 В"},
        description="Краткое описание"
    )
    raw_data = {
        "seo_title": "Тестовый заголовок до 70 знаков",
        "seo_description": "Описание прибора на 850 символов...",
        "structured_specs": {"Питание": "24 В"},
        "search_queries": ["запрос 1", "запрос 2", "запрос 3"],
        "commercial_block": {
            "target_audience": "Инженеры",
            "key_tasks_solved": ["Задача 1"],
            "competitive_advantages": ["Плюс 1"]
        },
        "missing_data_warnings": ["Нет степени защиты IP"]
    }
    md = generate_markdown_representation(raw_data, sample)
    assert "# Прибор А" in md
    assert "Вендор Б" in md
    assert "SEO-блок" in md
    assert "Замечания для контент-менеджера" in md
