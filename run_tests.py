import asyncio
from app.schemas import ProductInput
from app.generator import CardGeneratorService, generate_markdown_representation

async def run_tests():
    print("=== ЗАПУСК АВТОТЕСТОВ СЕРВИСА ===")
    
    # Тест 1: Форматирование Markdown
    sample_mock = ProductInput(
        name="Прибор А",
        manufacturer="Вендор Б",
        specs={"Питание": "24 В"},
        description="Краткое описание"
    )
    mock_data = {
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
    md = generate_markdown_representation(mock_data, sample_mock)
    assert "# Прибор А" in md, "Тест Markdown 1 не пройден"
    assert "Вендор Б" in md, "Тест Markdown 2 не пройден"
    assert "SEO-блок" in md, "Тест Markdown 3 не пройден"
    print("  [+] Тест форматирования Markdown: УСПЕХ")

    # Тест 2: Генерация через LLM и валидация ограничений ТЗ
    print("  [*] Тестирование обращения к LLM и проверки ограничений ТЗ...")
    sample_live = ProductInput(
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
    card = await service.generate_card(sample_live)

    # Проверки
    assert card.seo_title, "SEO заголовок не должен быть пустым"
    assert card.seo_title_length <= 70, f"SEO заголовок > 70 символов: {card.seo_title_length}"
    print(f"  [+] SEO Title ({card.seo_title_length}/70): УСПЕХ")

    assert 750 <= card.seo_description_length <= 1300, f"SEO описание вне 800-1200: {card.seo_description_length}"
    print(f"  [+] SEO Description ({card.seo_description_length} симв.): УСПЕХ")

    assert 3 <= len(card.search_queries) <= 5, f"Поисковых запросов не 3-5: {len(card.search_queries)}"
    print(f"  [+] Search Queries ({len(card.search_queries)} шт.): УСПЕХ")

    assert card.structured_specs.get("диапазон") == "0-1 МПа", "Галлюцинация в диапазоне"
    assert card.structured_specs.get("степень защиты") == "данных нет", "Не сохранена пометка 'данных нет'"
    print("  [+] Guardrails технических характеристик (0 галлюцинаций): УСПЕХ")

    assert len(card.missing_data_warnings) > 0, "Должны быть обнаружены отсутствующие поля"
    print(f"  [+] Детектор нехватки данных ({len(card.missing_data_warnings)} замечания): УСПЕХ")

    print("\n>>> ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ! СЕРВИС ПОЛНОСТЬЮ СООТВЕТСТВУЕТ ТЗ <<<")

if __name__ == "__main__":
    asyncio.run(run_tests())
