import os
from pydantic import BaseModel, Field

class Settings(BaseModel):
    app_name: str = "B2B Product Card AI Assistant"
    app_version: str = "1.0.0"
    
    # LLM Settings (OpenAI-compatible)
    llm_api_key: str = Field(default_factory=lambda: os.getenv("LLM_API_KEY", os.getenv("OPENAI_API_KEY", "ipi9yxWTLigbFpQH_AV_Jg")))
    llm_base_url: str = Field(default_factory=lambda: os.getenv("LLM_BASE_URL", "https://agy.vibeees.pro/antigravity/v1"))
    llm_model: str = Field(default_factory=lambda: os.getenv("LLM_MODEL", "gemini-3.8-flash-tiered"))
    
    # Validation constraints
    seo_title_max_len: int = 70
    seo_desc_min_len: int = 800
    seo_desc_max_len: int = 1200
    
    host: str = "0.0.0.0"
    port: int = 8090

settings = Settings()
