from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class ProductInput(BaseModel):
    name: str = Field(..., description="Название контрольно-измерительного прибора или оборудования")
    manufacturer: Optional[str] = Field(None, description="Производитель или бренд")
    specs: Dict[str, str] = Field(default_factory=dict, description="Словарь технических характеристик")
    description: Optional[str] = Field(None, description="Текстовое описание или фрагмент технического паспорта")

class CommercialBlock(BaseModel):
    target_audience: str = Field(..., description="Кому подходит прибор (отрасли, типы специалистов, объекты)")
    key_tasks_solved: List[str] = Field(..., description="Какие практические задачи решает прибор")
    competitive_advantages: List[str] = Field(..., description="Ключевые преимущества для внедрения и эксплуатации")

class GeneratedCard(BaseModel):
    seo_title: str = Field(..., description="SEO-заголовок карточки товара (строго до 70 символов)")
    seo_title_length: int = Field(..., description="Фактическая длина SEO-заголовка")
    seo_description: str = Field(..., description="SEO-описание для интернет-магазина (800-1200 символов)")
    seo_description_length: int = Field(..., description="Фактическая длина SEO-описания")
    structured_specs: Dict[str, str] = Field(..., description="Структурированный список ключевых характеристик (без выдумок)")
    search_queries: List[str] = Field(..., description="3-5 поисковых запросов для поисковой оптимизации")
    commercial_block: CommercialBlock = Field(..., description="Коммерческий блок для менеджера по продажам")
    missing_data_warnings: List[str] = Field(default_factory=list, description="Предупреждения о недостающих или требующих уточнения полях")
    raw_markdown: str = Field(..., description="Готовый к копированию Markdown карточки товара")
