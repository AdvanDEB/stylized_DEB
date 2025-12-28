"""Document chunking and processing utilities."""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class DocumentChunker:
    """Chunk documents into smaller pieces for embedding."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Chunk text into overlapping segments.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries
        """
        if not text or len(text) == 0:
            return []
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence end markers
                for marker in ['. ', '.\n', '! ', '? ']:
                    pos = text.rfind(marker, start, end)
                    if pos > start:
                        end = pos + 1
                        break
            
            # Extract chunk
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunk = {
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "char_start": start,
                    "char_end": end,
                }
                
                if metadata:
                    chunk["metadata"] = metadata
                
                chunks.append(chunk)
                chunk_id += 1
            
            # Move start position (with overlap)
            start = end - self.chunk_overlap if end < len(text) else end
        
        return chunks
    
    def chunk_document(self, document: Dict) -> List[Dict]:
        """
        Chunk a document from MongoDB.
        
        Args:
            document: Document dictionary from MongoDB
            
        Returns:
            List of chunk dictionaries ready for embedding
        """
        text = document.get("extracted_text", "")
        
        if not text:
            logger.warning(f"Document {document.get('filename')} has no text")
            return []
        
        metadata = {
            "doc_id": document.get("doc_id"),
            "filename": document.get("filename"),
            "filepath": document.get("filepath"),
            "page_count": document.get("page_count", 0)
        }
        
        chunks = self.chunk_text(text, metadata)
        
        # Add document reference to each chunk
        for chunk in chunks:
            chunk["doc_id"] = document.get("doc_id")
        
        logger.debug(f"Chunked {document.get('filename')}: {len(chunks)} chunks")
        
        return chunks
