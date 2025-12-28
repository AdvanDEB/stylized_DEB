"""CSV updater to add assessment results to CSV files."""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from literature_review.config import config

logger = logging.getLogger(__name__)

class CSVUpdater:
    """Update CSV files with assessment results."""
    
    def __init__(self, csv_dir: Path = None):
        self.csv_dir = csv_dir or config.CSV_DIR
    
    def update_fact(self, fact_number: int, assessment: Dict):
        """
        Update CSV with assessment results for a fact.
        
        Args:
            fact_number: Fact number
            assessment: Assessment results dictionary
        """
        # Find which CSV file contains this fact
        csv_file = self._find_csv_for_fact(fact_number)
        
        if not csv_file:
            logger.error(f"Could not find CSV file for fact #{fact_number}")
            return
        
        try:
            # Read CSV
            df = pd.read_csv(csv_file)
            
            # Ensure assessment columns exist
            self._ensure_columns(df)
            
            # Find fact row
            fact_idx = df[df["Number"] == fact_number].index
            
            if len(fact_idx) == 0:
                logger.error(f"Fact #{fact_number} not found in {csv_file.name}")
                return
            
            idx = fact_idx[0]
            
            # Update columns
            df.at[idx, "Literature Support Score (1-100)"] = assessment.get("score", 0)
            df.at[idx, "Number of Papers Reviewed"] = assessment.get("retrieved_chunks_count", 0)
            df.at[idx, "Supporting Papers"] = ", ".join(assessment.get("supporting_papers", []))
            df.at[idx, "Key Evidence Summary"] = assessment.get("key_evidence", "")
            df.at[idx, "Assessment Confidence"] = assessment.get("confidence", "low")
            df.at[idx, "Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save CSV
            df.to_csv(csv_file, index=False)
            logger.debug(f"Updated {csv_file.name} with fact #{fact_number} results")
            
        except Exception as e:
            logger.error(f"Error updating CSV for fact #{fact_number}: {e}")
    
    def _find_csv_for_fact(self, fact_number: int) -> Path:
        """Find which CSV file contains a fact number."""
        # Fact number ranges for each CSV (100 facts per file)
        csv_files = sorted(self.csv_dir.glob("*.csv"))
        
        for csv_file in csv_files:
            if csv_file.name == "README.md":
                continue
            
            try:
                df = pd.read_csv(csv_file)
                if fact_number in df["Number"].values:
                    return csv_file
            except Exception as e:
                logger.debug(f"Error reading {csv_file.name}: {e}")
        
        return None
    
    def _ensure_columns(self, df: pd.DataFrame):
        """Ensure required assessment columns exist."""
        required_columns = [
            "Literature Support Score (1-100)",
            "Number of Papers Reviewed",
            "Supporting Papers",
            "Key Evidence Summary",
            "Assessment Confidence",
            "Last Updated"
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = ""
