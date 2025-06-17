"""Configuration management for Super-Digimon system."""

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Config(BaseSettings):
    """System configuration."""
    
    # Neo4j settings
    neo4j_uri: str = Field(default="bolt://localhost:7687", env="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", env="NEO4J_USER")
    neo4j_password: str = Field(default="password", env="NEO4J_PASSWORD")
    
    # SQLite settings
    sqlite_db_path: Path = Field(default=Path("./data/metadata.db"), env="SQLITE_DB_PATH")
    
    # FAISS settings
    faiss_index_path: Path = Field(default=Path("./data/faiss_index"), env="FAISS_INDEX_PATH")
    
    # Redis settings (optional)
    redis_url: Optional[str] = Field(default=None, env="REDIS_URL")
    
    # MCP settings
    mcp_server_port: int = Field(default=3333, env="MCP_SERVER_PORT")
    disable_mcp: bool = Field(default=False, env="DISABLE_MCP")
    
    # Performance settings
    max_workers: int = Field(default=4, env="MAX_WORKERS")
    batch_size: int = Field(default=100, env="BATCH_SIZE")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # OpenAI settings
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    
    # Paths
    data_dir: Path = Field(default=Path("./data"), env="DATA_DIR")
    cache_dir: Path = Field(default=Path("./data/cache"), env="CACHE_DIR")
    checkpoint_dir: Path = Field(default=Path("./data/checkpoints"), env="CHECKPOINT_DIR")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.sqlite_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.faiss_index_path.parent.mkdir(parents=True, exist_ok=True)