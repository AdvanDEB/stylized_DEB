"""Phase 2: RAG Indexing Pipeline - Chunk documents, generate embeddings, store in MongoDB."""

import logging
from pathlib import Path
from tqdm import tqdm
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from literature_review.config import config
from literature_review.utils.mongodb_client import mongodb
from literature_review.utils.fact_loader import FactLoader
from literature_review.phase2_indexing.document_processor import DocumentChunker
from literature_review.phase2_indexing.embedding_generator import EmbeddingGenerator

logger = logging.getLogger(__name__)

class IndexingPipeline:
    """Pipeline for chunking documents and generating embeddings."""
    
    def __init__(self):
        self.mongodb = mongodb
        self.mongodb.connect()
        self.chunker = DocumentChunker(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP
        )
        self.embedder = EmbeddingGenerator(
            model=config.EMBEDDING_MODEL,
            base_url=config.OLLAMA_BASE_URL
        )
        self.fact_loader = FactLoader()
    
    def chunk_documents(self):
        """Chunk all documents in MongoDB."""
        logger.info("Starting document chunking...")
        
        # Get all documents
        documents = list(self.mongodb.documents.find({"extraction_status": "success"}))
        logger.info(f"Found {len(documents)} documents to chunk")
        
        total_chunks = 0
        
        with tqdm(total=len(documents), desc="Chunking documents") as pbar:
            for doc in documents:
                # Check if already chunked
                existing_chunks = self.mongodb.chunks.count_documents({"doc_id": doc["doc_id"]})
                if existing_chunks > 0:
                    logger.debug(f"Skipping already chunked: {doc['filename']}")
                    pbar.update(1)
                    continue
                
                # Chunk document
                chunks = self.chunker.chunk_document(doc)
                
                if chunks:
                    # Store chunks without embeddings first
                    self.mongodb.chunks.insert_many(chunks)
                    total_chunks += len(chunks)
                    logger.info(f"  {doc['filename']}: {len(chunks)} chunks")
                
                pbar.update(1)
        
        logger.info(f"Chunking complete: {total_chunks} total chunks created")
    
    def generate_chunk_embeddings(self, batch_size: int = 50):
        """Generate embeddings for all chunks."""
        logger.info("Generating embeddings for chunks...")
        
        # Get chunks without embeddings
        chunks_without_embeddings = list(self.mongodb.chunks.find({"embedding": {"$exists": False}}))
        
        if not chunks_without_embeddings:
            logger.info("All chunks already have embeddings")
            return
        
        logger.info(f"Found {len(chunks_without_embeddings)} chunks needing embeddings")
        
        with tqdm(total=len(chunks_without_embeddings), desc="Embedding chunks") as pbar:
            for i in range(0, len(chunks_without_embeddings), batch_size):
                batch = chunks_without_embeddings[i:i + batch_size]
                texts = [chunk["text"] for chunk in batch]
                
                # Generate embeddings
                embeddings = self.embedder.embed_batch(texts, batch_size=10)
                
                # Update chunks in MongoDB
                for chunk, embedding in zip(batch, embeddings):
                    self.mongodb.chunks.update_one(
                        {"_id": chunk["_id"]},
                        {"$set": {"embedding": embedding}}
                    )
                
                pbar.update(len(batch))
        
        logger.info("Chunk embeddings complete")
    
    def index_facts(self):
        """Load facts and generate embeddings."""
        logger.info("Indexing stylized facts...")
        
        # Load facts
        facts = self.fact_loader.load_all_facts()
        
        logger.info(f"Generating embeddings for {len(facts)} facts...")
        
        with tqdm(total=len(facts), desc="Embedding facts") as pbar:
            for fact in facts:
                # Check if already indexed
                existing = self.mongodb.facts.find_one({"fact_number": fact["fact_number"]})
                if existing and "embedding" in existing:
                    pbar.update(1)
                    continue
                
                # Generate embedding
                embedding = self.embedder.embed_text(fact["fact_text"])
                fact["embedding"] = embedding
                
                # Upsert to MongoDB
                self.mongodb.facts.update_one(
                    {"fact_number": fact["fact_number"]},
                    {"$set": fact},
                    upsert=True
                )
                
                pbar.update(1)
        
        logger.info("Fact indexing complete")
    
    def run(self):
        """Run the complete indexing pipeline."""
        # Step 1: Chunk documents
        self.chunk_documents()
        
        # Step 2: Generate chunk embeddings
        self.generate_chunk_embeddings()
        
        # Step 3: Index facts
        self.index_facts()
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("INDEXING COMPLETE")
        logger.info(f"  Documents: {self.mongodb.documents.count_documents({})}")
        logger.info(f"  Chunks: {self.mongodb.chunks.count_documents({})}")
        logger.info(f"  Facts: {self.mongodb.facts.count_documents({})}")
        logger.info("="*60)

def main():
    """Main entry point for Phase 2."""
    from literature_review.utils.logging_config import setup_logging
    
    setup_logging(config.LOG_DIR, config.LOG_LEVEL)
    logger.info("="*60)
    logger.info("PHASE 2: RAG INDEXING")
    logger.info("="*60)
    
    pipeline = IndexingPipeline()
    pipeline.run()
    
    logger.info("\nPhase 2 complete!")

if __name__ == "__main__":
    main()
