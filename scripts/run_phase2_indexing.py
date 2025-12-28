#!/usr/bin/env python3
"""Run Phase 2: RAG Indexing - Chunk documents and generate embeddings."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from literature_review.phase2_indexing.indexing_pipeline import main

if __name__ == "__main__":
    main()
