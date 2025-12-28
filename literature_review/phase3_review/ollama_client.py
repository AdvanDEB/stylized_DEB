"""Ollama client for LLM assessment."""

import logging
import ollama
import json
from typing import Dict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from literature_review.config import config

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with Ollama LLM."""
    
    def __init__(self):
        self.client = ollama.Client(host=config.OLLAMA_BASE_URL)
        self.model = config.LLM_MODEL
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generate response from LLM.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Generated text response
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            response = self.client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": config.LLM_TEMPERATURE,
                    "top_p": config.LLM_TOP_P,
                    "num_ctx": config.LLM_CONTEXT_SIZE,
                    "repeat_penalty": config.LLM_REPEAT_PENALTY
                }
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def generate_json(self, prompt: str, system_prompt: str = None, max_retries: int = 3) -> Dict:
        """
        Generate JSON response from LLM.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_retries: Maximum number of retries for valid JSON
            
        Returns:
            Parsed JSON dictionary
        """
        for attempt in range(max_retries):
            try:
                response_text = self.generate(prompt, system_prompt)
                
                # Try to extract JSON from response
                # Sometimes LLM adds markdown code blocks
                if "```json" in response_text:
                    start = response_text.find("```json") + 7
                    end = response_text.find("```", start)
                    json_text = response_text[start:end].strip()
                elif "```" in response_text:
                    start = response_text.find("```") + 3
                    end = response_text.find("```", start)
                    json_text = response_text[start:end].strip()
                else:
                    json_text = response_text.strip()
                
                # Parse JSON
                result = json.loads(json_text)
                return result
                
            except json.JSONDecodeError as e:
                logger.warning(f"Attempt {attempt + 1}/{max_retries}: Failed to parse JSON: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to get valid JSON after {max_retries} attempts")
                    # Return default structure
                    return {
                        "score": 50,
                        "confidence": "low",
                        "num_supporting_sources": 0,
                        "num_contradicting_sources": 0,
                        "key_evidence": "Failed to parse LLM response",
                        "supporting_papers": [],
                        "contradicting_papers": []
                    }
            except Exception as e:
                logger.error(f"Error in generate_json: {e}")
                raise
        
        return {}
