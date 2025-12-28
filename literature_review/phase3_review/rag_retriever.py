"""RAG Retriever for finding relevant document chunks."""

import logging
from typing import List, Dict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from literature_review.config import config
from literature_review.utils.mongodb_client import mongodb
from literature_review.phase2_indexing.embedding_generator import EmbeddingGenerator

logger = logging.getLogger(__name__)

class RAGRetriever:
    """Retrieve relevant document chunks using vector similarity."""
    
    def __init__(self):
        self.mongodb = mongodb
        self.mongodb.connect()
        self.embedder = EmbeddingGenerator(
            model=config.EMBEDDING_MODEL,
            base_url=config.OLLAMA_BASE_URL
        )
    
    def retrieve(self, fact_text: str, top_k: int = None) -> List[Dict]:
        """
        Retrieve most relevant chunks for a given fact.
        
        Args:
            fact_text: The stylized fact text
            top_k: Number of chunks to retrieve (default from config)
            
        Returns:
            List of relevant chunks with similarity scores
        """
        if top_k is None:
            top_k = config.TOP_K_RETRIEVAL
        
        # Generate embedding for query
        query_embedding = self.embedder.embed_text(fact_text)
        
        # Vector similarity search using cosine similarity
        # Note: This is a basic implementation. MongoDB Atlas Vector Search would be more efficient
        relevant_chunks = self._cosine_similarity_search(query_embedding, top_k)
        
        logger.info(f"Retrieved {len(relevant_chunks)} chunks for fact")
        
        return relevant_chunks
    
    def _cosine_similarity_search(self, query_embedding: List[float], top_k: int) -> List[Dict]:
        """
        Perform cosine similarity search (basic implementation).
        
        Args:
            query_embedding: Query vector
            top_k: Number of results
            
        Returns:
            List of chunks with similarity scores
        """
        import numpy as np
        
        # Get all chunks with embeddings
        chunks = list(self.mongodb.chunks.find({"embedding": {"$exists": True}}))
        
        if not chunks:
            logger.warning("No chunks with embeddings found!")
            return []
        
        # Calculate cosine similarity
        query_vec = np.array(query_embedding)
        query_norm = np.linalg.norm(query_vec)
        
        similarities = []
        for chunk in chunks:
            chunk_vec = np.array(chunk["embedding"])
            chunk_norm = np.linalg.norm(chunk_vec)
            
            if chunk_norm > 0 and query_norm > 0:
                similarity = np.dot(query_vec, chunk_vec) / (query_norm * chunk_norm)
                similarities.append((chunk, float(similarity)))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top-k
        results = []
        for chunk, score in similarities[:top_k]:
            results.append({
                "doc_id": chunk["doc_id"],
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "metadata": chunk.get("metadata", {}),
                "similarity_score": score
            })
        
        return results
