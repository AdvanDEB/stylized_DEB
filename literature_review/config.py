"""Configuration settings for DEB Literature Review System."""

from pathlib import Path
from typing import Dict

class Config:
    """Main configuration class."""
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    FILES_DIR: Path = BASE_DIR / "files"
    CSV_DIR: Path = BASE_DIR / "csv_files"
    DATA_DIR: Path = BASE_DIR / "data"
    LOG_DIR: Path = DATA_DIR / "logs"
    CHECKPOINT_DIR: Path = DATA_DIR / "checkpoints"
    
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "deb_literature_review"
    MONGODB_COLLECTIONS: Dict[str, str] = {
        "documents": "documents",
        "chunks": "document_chunks",
        "facts": "stylized_facts",
        "assessments": "assessments",
        "checkpoints": "checkpoints"
    }
    
    # Vector Search
    VECTOR_INDEX_NAME: str = "vector_index"
    EMBEDDING_DIMENSIONS: int = 768
    SIMILARITY_METRIC: str = "cosine"
    
    # PDF Extraction
    MAX_WORKERS_EXTRACTION: int = 4
    
    # RAG Settings
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RETRIEVAL: int = 20
    NUM_CANDIDATES: int = 100
    ENABLE_HYBRID_SEARCH: bool = True
    ENABLE_RERANKING: bool = True
    
    # Embedding Model
    EMBEDDING_MODEL: str = "nomic-embed-text"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # LLM Settings
    LLM_MODEL: str = "gpt-oss:120b"
    LLM_TEMPERATURE: float = 0.1
    LLM_TOP_P: float = 0.9
    LLM_CONTEXT_SIZE: int = 32000
    LLM_REPEAT_PENALTY: float = 1.1
    
    # Scoring Scale
    SCORE_RANGES: Dict[str, tuple] = {
        "no_support": (1, 20),
        "weak": (21, 40),
        "moderate": (41, 60),
        "strong": (61, 80),
        "very_strong": (81, 100)
    }
    
    # Web Dashboard
    DASHBOARD_HOST: str = "0.0.0.0"
    DASHBOARD_PORT: int = 5000
    
    # Logging
    LOG_LEVEL: str = "INFO"

# Global config instance
config = Config()

# Ensure directories exist
config.DATA_DIR.mkdir(exist_ok=True)
config.LOG_DIR.mkdir(exist_ok=True)
config.CHECKPOINT_DIR.mkdir(exist_ok=True)
