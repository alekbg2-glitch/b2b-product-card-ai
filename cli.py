import asyncio
import argparse
import json
import sys
from pathlib import Path

# Добавляем путь к корню проекта
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.schemas import ProductInput
from app.generator import CardGeneratorService

async def main():
    parser = argparse.ArgumentParser(description="CLI генератор карточек товаров КИПиА через LLM")
    parser.add_argument("--input", "-i", required=True, help="Путь к входному JSON-файлу с данными прибора")
    parser.add_argument("--output", "-o", default=None, help="Путь для сохранения результата (Markdown или JSON)")
    parser.add_argument("--format", "-f", choices=["markdown", "json", "all"], default="markdown", help="Формат вывода")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Ошибка: Файл {input_path} не найден!")
        sys.exit(1)
        
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    product = ProductInput(**data)
    service = CardGeneratorService()
    
    print(f"[*] Обработка товара: {product.name}...")
    card = await service.generate_card(product)
    
    print("\n" + "="*50)
    print(f"SEO Title ({card.seo_title_length}/70): {card.seo_title}")
    print(f"SEO Desc Length: {card.seo_description_length} символов")
    print(f"Поисковые запросы: {', '.join(card.search_queries)}")
    if card.missing_data_warnings:
        print(f"Предупреждения: {len(card.missing_data_warnings)}")
    print("="*50 + "\n")
    
    out_content = card.raw_markdown if args.format == "markdown" else card.model_dump_json(indent=2)
    
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(out_content)
        print(f"[+] Результат сохранён в: {out_path}")
    else:
        print(out_content)

if __name__ == "__main__":
    asyncio.run(main())
