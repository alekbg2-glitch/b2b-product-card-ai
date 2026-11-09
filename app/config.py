import os
from pydantic import BaseModel, Field

class Settings(BaseModel):
    app_name: str = "B2B Product Card AI Assistant"
    app_version: str = "1.0.0"
    
    # LLM Settings (OpenAI-compatible)
    llm_api_key: str = Field(default_factory=lambda: os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", "")))
    llm_base_url: str = Field(default_factory=lambda: os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"))
    llm_model: str = Field(default_factory=lambda: os.getenv("LLM_MODEL", "gpt-4o-mini"))
    
    # Validation constraints
    seo_title_max_len: int = 70
    seo_desc_min_len: int = 800
    seo_desc_max_len: int = 1200
    
    host: str = "0.0.0.0"
    port: int = 8090

settings = Settings()
