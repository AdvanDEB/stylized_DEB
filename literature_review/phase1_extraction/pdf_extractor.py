"""PDF text extraction using PyMuPDF."""

import fitz  # PyMuPDF
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PDFExtractor:
    """Extract text from PDF files using PyMuPDF."""
    
    def __init__(self):
        self.logger = logger
    
    def extract_text(self, pdf_path: Path) -> Dict:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        result = {
            "filepath": str(pdf_path),
            "filename": pdf_path.name,
            "doc_id": pdf_path.parent.name,  # Directory name as doc ID
            "extracted_text": "",
            "page_count": 0,
            "extraction_status": "pending",
            "error_message": None,
            "created_at": datetime.now()
        }
        
        try:
            # Open PDF
            doc = fitz.open(pdf_path)
            result["page_count"] = len(doc)
            
            # Extract text from all pages
            text_parts = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    text_parts.append(f"[Page {page_num + 1}]\n{text}")
            
            result["extracted_text"] = "\n\n".join(text_parts)
            result["extraction_status"] = "success"
            
            doc.close()
            
            self.logger.info(f"✓ Extracted {pdf_path.name}: {result['page_count']} pages, "
                           f"{len(result['extracted_text'])} chars")
            
        except Exception as e:
            result["extraction_status"] = "failed"
            result["error_message"] = str(e)
            self.logger.error(f"✗ Failed to extract {pdf_path.name}: {e}")
        
        return result
    
    def extract_batch(self, pdf_paths: list[Path]) -> list[Dict]:
        """
        Extract text from multiple PDF files.
        
        Args:
            pdf_paths: List of PDF file paths
            
        Returns:
            List of extraction results
        """
        results = []
        total = len(pdf_paths)
        
        for i, pdf_path in enumerate(pdf_paths, 1):
            self.logger.info(f"Processing [{i}/{total}]: {pdf_path.name}")
            result = self.extract_text(pdf_path)
            results.append(result)
        
        # Summary
        success = sum(1 for r in results if r["extraction_status"] == "success")
        failed = total - success
        
        self.logger.info(f"\nExtraction complete: {success} success, {failed} failed out of {total}")
        
        return results
