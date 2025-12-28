"""Checkpoint manager for resumable processing."""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from literature_review.config import config

logger = logging.getLogger(__name__)

class CheckpointManager:
    """Manage checkpoints for resumable fact processing."""
    
    def __init__(self, checkpoint_path: Path = None):
        self.checkpoint_path = checkpoint_path or config.CHECKPOINT_DIR / "review_checkpoint.json"
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load_checkpoint(self) -> Optional[Dict]:
        """Load checkpoint from file."""
        if not self.checkpoint_path.exists():
            logger.info("No checkpoint found, starting from beginning")
            return None
        
        try:
            with open(self.checkpoint_path, 'r') as f:
                checkpoint = json.load(f)
            logger.info(f"Loaded checkpoint: last completed fact #{checkpoint.get('last_completed_fact', 0)}")
            return checkpoint
        except Exception as e:
            logger.error(f"Error loading checkpoint: {e}")
            return None
    
    def save_checkpoint(self, checkpoint: Dict):
        """Save checkpoint to file."""
        checkpoint["last_updated"] = datetime.now().isoformat()
        
        try:
            with open(self.checkpoint_path, 'w') as f:
                json.dump(checkpoint, f, indent=2)
            logger.debug(f"Checkpoint saved: fact #{checkpoint.get('last_completed_fact', 0)}")
        except Exception as e:
            logger.error(f"Error saving checkpoint: {e}")
    
    def create_initial_checkpoint(self, total_facts: int) -> Dict:
        """Create initial checkpoint."""
        return {
            "last_completed_fact": 0,
            "total_facts": total_facts,
            "facts_processed": 0,
            "failed_facts": [],
            "started_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    def update_checkpoint(self, checkpoint: Dict, fact_number: int, success: bool = True):
        """Update checkpoint after processing a fact."""
        checkpoint["last_completed_fact"] = fact_number
        checkpoint["facts_processed"] += 1
        
        if not success:
            if "failed_facts" not in checkpoint:
                checkpoint["failed_facts"] = []
            checkpoint["failed_facts"].append(fact_number)
        
        self.save_checkpoint(checkpoint)
