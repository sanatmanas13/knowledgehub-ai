"""
Centralized application configuration.

Why this exists:
Every module (ingestion, embeddings, FAISS, chat) needs shared values like
file paths and model names. Keeping them in one Settings object means no
module hardcodes a path or model name — they all import `settings` instead.

pydantic-settings is used here (not plain os.environ) because:
- Values are type-validated at startup, not silently wrong at runtime.
- It auto-loads from a `.env` file, so secrets/paths never need to be
  hardcoded or committed.
- FastAPI already depends on Pydantic, so this adds no new dependency
  family to the project (rule: avoid unnecessary libraries).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Single source of truth for application configuration.

    Fields are grouped by the module that will consume them. Some fields
    (embedding/FAISS/Ollama) aren't used yet, but live here now so that when
    those modules are built, they read from this class instead of each
    inventing their own config pattern.
    """

    # --- General app settings ---
    app_name: str = "KnowledgeHub AI"
    debug: bool = True

    # --- CORS (React frontend runs on a different port during development) ---
    cors_allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # --- Database (used by core/database.py) ---
    database_url: str = "sqlite:///./knowledgehub.db"

    # --- Storage paths (used by the future PDF ingestion module) ---
    upload_directory: str = "./data/uploads"
    faiss_index_path: str = "./data/faiss_index"

    # --- Embedding model (used by the future embedding module) ---
    embedding_model_name: str = "all-MiniLM-L6-v2"

    # --- LLM / Ollama (used by the future chat module) ---
    ollama_base_url: str = "http://localhost:11434"
    ollama_model_name: str = "phi3:mini"

    # --- Chunking parameters (used by the future PDF ingestion module) ---
    chunk_size_tokens: int = 512
    chunk_overlap_tokens: int = 64

    # Tells pydantic-settings to load matching values from a .env file
    # if one is present, without requiring it to exist.
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


# Instantiated once and imported everywhere else in the app.
# This avoids re-reading/re-validating environment variables on every use.
settings = Settings()
