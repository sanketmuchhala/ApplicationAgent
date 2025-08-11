import os
from typing import Dict, Optional
from pathlib import Path


class PromptManager:
    """Manages AI prompts for different operations"""
    
    def __init__(self, prompts_dir: Optional[str] = None):
        if prompts_dir is None:
            # Default to config/prompts relative to project root
            current_dir = Path(__file__).parent.parent.parent
            self.prompts_dir = current_dir / "config" / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)
        
        self._prompt_cache: Dict[str, str] = {}
    
    def get_form_analysis_prompt(self) -> str:
        """Get the form analysis system prompt"""
        return self._load_prompt("form_analysis.txt")
    
    def get_field_matching_prompt(self) -> str:
        """Get the field matching system prompt"""
        return self._load_prompt("field_matching.txt")
    
    def get_response_generation_prompt(self) -> str:
        """Get the response generation system prompt"""
        return self._load_prompt("response_generation.txt")
    
    def _load_prompt(self, filename: str) -> str:
        """Load prompt from file with caching"""
        if filename in self._prompt_cache:
            return self._prompt_cache[filename]
        
        prompt_path = self.prompts_dir / filename
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt = f.read().strip()
                self._prompt_cache[filename] = prompt
                return prompt
        except FileNotFoundError:
            # Return fallback prompt if file not found
            return self._get_fallback_prompt(filename)
        except Exception as e:
            raise Exception(f"Error loading prompt {filename}: {str(e)}")
    
    def _get_fallback_prompt(self, filename: str) -> str:
        """Get fallback prompts if files are not available"""
        
        if filename == "form_analysis.txt":
            return """SYSTEM: You are an expert at analyzing job application forms. 
Analyze the provided HTML form and extract structured information about form fields, sections, and requirements.

Respond with a JSON object containing:
- form_metadata: Basic information about the form
- sections: Array of form sections with their fields
- fields: Detailed information about each field
- completion_strategy: Recommended approach for completing the form
- potential_issues: Any issues that might prevent completion

Focus on identifying field types, requirements, and optimal completion order."""
        
        elif filename == "field_matching.txt":
            return """SYSTEM: You are an expert at matching job application form fields to user profile data.

Analyze the form fields and user profile to create accurate mappings. For each field, provide:
- profile_mapping: Dot notation path to the profile field
- response_value: Appropriate value from the profile
- confidence_score: How confident you are in this mapping (0-100)
- reasoning: Why this mapping was chosen

Respond with a JSON object containing field_mappings array."""
        
        elif filename == "response_generation.txt":
            return """SYSTEM: You are an expert at generating professional responses for job application fields.

Generate appropriate, tailored responses based on:
- Field requirements and constraints
- User's profile data
- Job/company context

Respond with a JSON object containing:
- response: The generated response text
- confidence_score: Confidence in the response quality
- character_count: Length of response
- fits_constraints: Whether response meets field requirements

Make responses authentic, specific, and professionally appropriate."""
        
        else:
            return "SYSTEM: You are a helpful AI assistant for job applications."
    
    def reload_prompts(self):
        """Clear cache and reload all prompts"""
        self._prompt_cache.clear()
    
    def add_custom_prompt(self, name: str, content: str):
        """Add a custom prompt to the cache"""
        self._prompt_cache[name] = content
    
    def get_custom_prompt(self, name: str) -> Optional[str]:
        """Get a custom prompt by name"""
        return self._prompt_cache.get(name)