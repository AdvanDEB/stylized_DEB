#!/usr/bin/env python3
"""Master script to run all phases of the literature review pipeline."""

import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    parser = argparse.ArgumentParser(description="DEB Literature Review Pipeline")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3], help="Run specific phase (1, 2, or 3)")
    parser.add_argument("--all", action="store_true", help="Run all phases sequentially")
    parser.add_argument("--test", action="store_true", help="Run in test mode (Phase 3 only)")
    
    args = parser.parse_args()
    
    if args.all:
        print("Running all phases sequentially...")
        run_phase_1()
        run_phase_2()
        run_phase_3(test_mode=args.test)
    elif args.phase == 1:
        run_phase_1()
    elif args.phase == 2:
        run_phase_2()
    elif args.phase == 3:
        run_phase_3(test_mode=args.test)
    else:
        parser.print_help()

def run_phase_1():
    """Run Phase 1: PDF Extraction."""
    print("\n" + "="*60)
    print("STARTING PHASE 1: PDF EXTRACTION")
    print("="*60 + "\n")
    from literature_review.phase1_extraction.extraction_pipeline import main as phase1_main
    phase1_main()

def run_phase_2():
    """Run Phase 2: RAG Indexing."""
    print("\n" + "="*60)
    print("STARTING PHASE 2: RAG INDEXING")
    print("="*60 + "\n")
    from literature_review.phase2_indexing.indexing_pipeline import main as phase2_main
    phase2_main()

def run_phase_3(test_mode: bool = False):
    """Run Phase 3: Literature Review."""
    print("\n" + "="*60)
    print("STARTING PHASE 3: LITERATURE REVIEW")
    if test_mode:
        print("TEST MODE - Processing 10 sample facts")
    print("="*60 + "\n")
    from literature_review.phase3_review.review_pipeline import main as phase3_main
    phase3_main(test_mode=test_mode)

if __name__ == "__main__":
    main()
