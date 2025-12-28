"""Load stylized facts from CSV files."""

import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from literature_review.config import config

logger = logging.getLogger(__name__)

class FactLoader:
    """Load stylized facts from CSV files."""
    
    def __init__(self, csv_dir: Path = None):
        """
        Initialize fact loader.
        
        Args:
            csv_dir: Directory containing CSV files
        """
        self.csv_dir = csv_dir or config.CSV_DIR
    
    def load_all_facts(self) -> List[Dict]:
        """
        Load all stylized facts from all CSV files.
        
        Returns:
            List of fact dictionaries
        """
        facts = []
        csv_files = sorted(self.csv_dir.glob("*.csv"))
        
        logger.info(f"Loading facts from {len(csv_files)} CSV files...")
        
        for csv_file in csv_files:
            if csv_file.name == "README.md":
                continue
            
            try:
                df = pd.read_csv(csv_file)
                
                for _, row in df.iterrows():
                    fact = {
                        "fact_number": int(row["Number"]),
                        "fact_text": str(row["DEB Stylized Fact"]),
                        "section": self._get_section_name(csv_file.stem),
                        "csv_file": csv_file.name
                    }
                    facts.append(fact)
                
                logger.info(f"  Loaded {len(df)} facts from {csv_file.name}")
                
            except Exception as e:
                logger.error(f"  Failed to load {csv_file.name}: {e}")
        
        logger.info(f"Total facts loaded: {len(facts)}")
        return facts
    
    def load_sample_facts(self, n: int = 10) -> List[Dict]:
        """
        Load a sample of facts for testing.
        
        Args:
            n: Number of facts to sample
            
        Returns:
            List of sampled fact dictionaries
        """
        all_facts = self.load_all_facts()
        
        # Sample evenly across sections
        import random
        random.seed(42)  # For reproducibility
        
        if len(all_facts) <= n:
            return all_facts
        
        # Sample evenly
        step = len(all_facts) // n
        sampled = [all_facts[i * step] for i in range(n)]
        
        logger.info(f"Sampled {len(sampled)} facts for testing")
        return sampled
    
    def _get_section_name(self, stem: str) -> str:
        """Convert filename stem to readable section name."""
        return stem.replace("_", " ").title()
