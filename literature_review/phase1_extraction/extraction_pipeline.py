"""Phase 1: PDF Extraction Pipeline - Extract PDFs and store in MongoDB."""

import logging
from pathlib import Path
from typing import List
from tqdm import tqdm
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from literature_review.config import config
from literature_review.utils.mongodb_client import mongodb
from literature_review.phase1_extraction.pdf_extractor import PDFExtractor

logger = logging.getLogger(__name__)

class ExtractionPipeline:
    """Pipeline for extracting PDFs and storing in MongoDB."""
    
    def __init__(self):
        self.extractor = PDFExtractor()
        self.mongodb = mongodb
        self.mongodb.connect()
    
    def find_all_pdfs(self) -> List[Path]:
        """Find all PDF files in the files directory."""
        logger.info(f"Scanning for PDFs in: {config.FILES_DIR}")
        pdf_files = list(config.FILES_DIR.rglob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")
        return pdf_files
    
    def extract_and_store(self, pdf_paths: List[Path], batch_size: int = 10):
        """
        Extract PDFs and store in MongoDB.
        
        Args:
            pdf_paths: List of PDF file paths
            batch_size: Number of PDFs to process before bulk insert
        """
        total = len(pdf_paths)
        logger.info(f"Starting extraction of {total} PDFs...")
        
        batch = []
        processed = 0
        errors = 0
        
        with tqdm(total=total, desc="Extracting PDFs") as pbar:
            for pdf_path in pdf_paths:
                # Check if already processed
                existing = self.mongodb.documents.find_one({"filepath": str(pdf_path)})
                if existing:
                    logger.debug(f"Skipping already processed: {pdf_path.name}")
                    pbar.update(1)
                    continue
                
                # Extract
                result = self.extractor.extract_text(pdf_path)
                
                if result["extraction_status"] == "success":
                    batch.append(result)
                    processed += 1
                else:
                    errors += 1
                
                # Bulk insert batch
                if len(batch) >= batch_size:
                    self.mongodb.documents.insert_many(batch)
                    logger.info(f"Inserted batch of {len(batch)} documents")
                    batch = []
                
                pbar.update(1)
        
        # Insert remaining
        if batch:
            self.mongodb.documents.insert_many(batch)
            logger.info(f"Inserted final batch of {len(batch)} documents")
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Extraction Complete!")
        logger.info(f"  Total PDFs: {total}")
        logger.info(f"  Successfully extracted: {processed}")
        logger.info(f"  Errors: {errors}")
        logger.info(f"  Documents in DB: {self.mongodb.documents.count_documents({})}")
        logger.info(f"{'='*60}")
    
    def run(self):
        """Run the complete extraction pipeline."""
        # Find PDFs
        pdf_files = self.find_all_pdfs()
        
        if not pdf_files:
            logger.warning("No PDF files found!")
            return
        
        # Extract and store
        self.extract_and_store(pdf_files)
        
        # Setup indexes
        self.mongodb.setup_indexes()

def main():
    """Main entry point for Phase 1."""
    from literature_review.utils.logging_config import setup_logging
    
    setup_logging(config.LOG_DIR, config.LOG_LEVEL)
    logger.info("="*60)
    logger.info("PHASE 1: PDF EXTRACTION")
    logger.info("="*60)
    
    pipeline = ExtractionPipeline()
    pipeline.run()
    
    logger.info("\nPhase 1 complete!")

if __name__ == "__main__":
    main()
