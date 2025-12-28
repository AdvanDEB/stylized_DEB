#!/usr/bin/env python3
"""Run Phase 3: Literature Review with RAG + LLM Assessment."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from literature_review.phase3_review.review_pipeline import main

if __name__ == "__main__":
    # Check for test mode flag
    test_mode = "--test" in sys.argv
    main(test_mode=test_mode, test_count=10)
