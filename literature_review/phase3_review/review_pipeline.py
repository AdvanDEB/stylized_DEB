"""Phase 3: Literature Review Pipeline - Assess facts with RAG + LLM."""

import logging
from pathlib import Path
from tqdm import tqdm
import sys
from datetime import datetime
import time

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from literature_review.config import config
from literature_review.utils.mongodb_client import mongodb
from literature_review.utils.fact_loader import FactLoader
from literature_review.phase3_review.assessment_agent import AssessmentAgent
from literature_review.phase3_review.checkpoint_manager import CheckpointManager
from literature_review.phase3_review.csv_updater import CSVUpdater

logger = logging.getLogger(__name__)

class ReviewPipeline:
    """Pipeline for reviewing facts with RAG + LLM assessment."""
    
    def __init__(self):
        self.mongodb = mongodb
        self.mongodb.connect()
        self.fact_loader = FactLoader()
        self.agent = AssessmentAgent()
        self.checkpoint_mgr = CheckpointManager()
        self.csv_updater = CSVUpdater()
    
    def run(self, test_mode: bool = False, test_count: int = 10):
        """
        Run the complete review pipeline.
        
        Args:
            test_mode: If True, only process a sample of facts
            test_count: Number of facts to process in test mode
        """
        # Load facts
        if test_mode:
            logger.info(f"TEST MODE: Processing {test_count} sample facts")
            facts = self.fact_loader.load_sample_facts(test_count)
        else:
            facts = self.fact_loader.load_all_facts()
        
        # Load or create checkpoint
        checkpoint = self.checkpoint_mgr.load_checkpoint()
        if checkpoint is None:
            checkpoint = self.checkpoint_mgr.create_initial_checkpoint(len(facts))
        
        # Filter facts to process
        last_completed = checkpoint.get("last_completed_fact", 0)
        facts_to_process = [f for f in facts if f["fact_number"] > last_completed]
        
        logger.info(f"Processing {len(facts_to_process)} facts (starting from #{last_completed + 1})")
        
        # Process each fact
        start_time = time.time()
        
        with tqdm(total=len(facts_to_process), desc="Reviewing facts") as pbar:
            for fact in facts_to_process:
                fact_number = fact["fact_number"]
                
                try:
                    # Assess fact
                    fact_start = time.time()
                    assessment = self.agent.assess_fact(fact)
                    fact_time = time.time() - fact_start
                    
                    # Store in MongoDB
                    self.mongodb.assessments.update_one(
                        {"fact_number": fact_number},
                        {"$set": {
                            "fact_number": fact_number,
                            "assessment_result": assessment,
                            "processing_time_seconds": fact_time,
                            "llm_model": config.LLM_MODEL,
                            "created_at": datetime.now()
                        }},
                        upsert=True
                    )
                    
                    # Update CSV
                    self.csv_updater.update_fact(fact_number, assessment)
                    
                    # Update checkpoint
                    self.checkpoint_mgr.update_checkpoint(checkpoint, fact_number, success=True)
                    
                    pbar.update(1)
                    pbar.set_postfix({"score": assessment.get("score", "N/A"), "time": f"{fact_time:.1f}s"})
                    
                except Exception as e:
                    logger.error(f"Failed to process fact #{fact_number}: {e}")
                    self.checkpoint_mgr.update_checkpoint(checkpoint, fact_number, success=False)
                    pbar.update(1)
        
        # Final summary
        total_time = time.time() - start_time
        avg_time = total_time / len(facts_to_process) if facts_to_process else 0
        
        logger.info("\n" + "="*60)
        logger.info("REVIEW COMPLETE")
        logger.info(f"  Facts processed: {len(facts_to_process)}")
        logger.info(f"  Total time: {total_time/60:.1f} minutes")
        logger.info(f"  Average time per fact: {avg_time:.1f} seconds")
        logger.info(f"  Failed facts: {len(checkpoint.get('failed_facts', []))}")
        logger.info(f"  Assessments in DB: {self.mongodb.assessments.count_documents({})}")
        logger.info("="*60)

def main(test_mode: bool = False, test_count: int = 10):
    """Main entry point for Phase 3."""
    from literature_review.utils.logging_config import setup_logging
    
    setup_logging(config.LOG_DIR, config.LOG_LEVEL)
    logger.info("="*60)
    logger.info("PHASE 3: LITERATURE REVIEW")
    if test_mode:
        logger.info(f"TEST MODE - Processing {test_count} facts")
    logger.info("="*60)
    
    pipeline = ReviewPipeline()
    pipeline.run(test_mode=test_mode, test_count=test_count)
    
    logger.info("\nPhase 3 complete!")

if __name__ == "__main__":
    import sys
    test_mode = "--test" in sys.argv
    main(test_mode=test_mode)
