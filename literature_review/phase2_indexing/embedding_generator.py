"""Embedding generation using Ollama."""

import logging
import ollama
from typing import List
import numpy as np

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """Generate embeddings using Ollama."""
    
    def __init__(self, model: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        """
        Initialize embedding generator.
        
        Args:
            model: Ollama model to use for embeddings
            base_url: Ollama server URL
        """
        self.model = model
        self.base_url = base_url
        self.client = ollama.Client(host=base_url)
        
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding
        """
        try:
            response = self.client.embeddings(
                model=self.model,
                prompt=text
            )
            return response['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def embed_batch(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            batch_size: Number of texts to process at once
            
        Returns:
            List of embeddings
        """
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            for text in batch:
                try:
                    embedding = self.embed_text(text)
                    embeddings.append(embedding)
                except Exception as e:
                    logger.error(f"Failed to embed text: {e}")
                    # Add zero vector as placeholder
                    embeddings.append([0.0] * 768)
        
        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings from this model."""
        test_embedding = self.embed_text("test")
        return len(test_embedding)
