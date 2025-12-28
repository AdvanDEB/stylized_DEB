#!/usr/bin/env python3
"""Run Phase 1: PDF Extraction to MongoDB."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from literature_review.phase1_extraction.extraction_pipeline import main

if __name__ == "__main__":
    main()
