import time
from typing import Dict, List, Optional, Any
from fuzzywuzzy import fuzz

from .ai_service import AIService
from models.ai_config import AIResponse
from models.form import FormField
from models.profile import UserProfile


class BasicMatchingService(AIService):
    """Basic text matching service using fuzzy matching and patterns"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("basic_matching", config)
        
        # Predefined field patterns for matching
        self.field_patterns = {
            "personal.first_name": [
                "first name", "firstname", "given name", "forename"
            ],
            "personal.last_name": [
                "last name", "lastname", "surname", "family name"
            ],
            "personal.full_name": [
                "full name", "complete name", "name", "your name"
            ],
            "contact.email": [
                "email", "e-mail", "mail", "email address"
            ],
            "contact.phone": [
                "phone", "telephone", "mobile", "cell", "contact number"
            ],
            "personal.address_line1": [
                "address", "street", "address line 1"
            ],
            "personal.city": [
                "city", "town"
            ],
            "personal.state": [
                "state", "province", "region"
            ],
            "personal.postal_code": [
                "zip", "postal", "postcode", "zip code"
            ],
            "personal.country": [
                "country", "nation"
            ],
            "contact.linkedin_url": [
                "linkedin", "linked in"
            ],
            "contact.github_url": [
                "github", "git hub"
            ],
            "contact.portfolio_url": [
                "portfolio", "website", "personal site"
            ],
            "experience.total_years": [
                "years of experience", "experience years", "total experience"
            ],
            "compensation.current_salary": [
                "current salary", "present salary", "salary"
            ],
            "compensation.desired_salary_min": [
                "desired salary", "expected salary", "salary expectation"
            ]
        }
    
    async def analyze_form_fields(
        self, 
        html_content: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """Basic form analysis using pattern matching"""
        start_time = time.time()
        
        try:
            # Simple HTML parsing to find form fields
            fields = self._extract_fields_from_html(html_content)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return AIResponse(
                success=True,
                data=fields,
                processing_time_ms=processing_time,
                tokens_used=0,
                estimated_cost=0.0
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            return AIResponse(
                success=False,
                error_message=str(e),
                processing_time_ms=processing_time,
                tokens_used=0,
                estimated_cost=0.0
            )
    
    async def match_fields_to_profile(
        self, 
        form_fields: List[FormField], 
        profile: UserProfile,
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """Match form fields to profile using pattern matching"""
        start_time = time.time()
        
        try:
            mappings = []
            
            for field in form_fields:
                mapping = self._match_single_field(field, profile)
                if mapping:
                    mappings.append(mapping)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return AIResponse(
                success=True,
                data=mappings,
                processing_time_ms=processing_time,
                tokens_used=0,
                estimated_cost=0.0
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            return AIResponse(
                success=False,
                error_message=str(e),
                processing_time_ms=processing_time,
                tokens_used=0,
                estimated_cost=0.0
            )
    
    async def generate_field_response(
        self, 
        field_info: FormField, 
        profile_data: Any,
        job_context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """Generate basic responses for fields"""
        start_time = time.time()
        
        try:
            response = self._generate_basic_response(field_info, profile_data)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            return AIResponse(
                success=True,
                data={"response": response},
                processing_time_ms=processing_time,
                tokens_used=0,
                estimated_cost=0.0
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            return AIResponse(
                success=False,
                error_message=str(e),
                processing_time_ms=processing_time,
                tokens_used=0,
                estimated_cost=0.0
            )
    
    async def improve_from_feedback(
        self, 
        original_response: str, 
        corrected_response: str, 
        context: Dict[str, Any]
    ) -> AIResponse:
        """Basic feedback learning (placeholder)"""
        start_time = time.time()
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return AIResponse(
            success=True,
            data={"message": "Feedback recorded for future improvement"},
            processing_time_ms=processing_time,
            tokens_used=0,
            estimated_cost=0.0
        )
    
    async def test_connection(self) -> bool:
        """Test if basic matching service is available"""
        return True  # Always available
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get basic matching service information"""
        return {
            "provider": self.provider_name,
            "model": "basic_pattern_matching",
            "max_tokens": 0,
            "temperature": 0.0,
            "context_length": 0,
            "cost_per_1k_input": 0.0,
            "cost_per_1k_output": 0.0,
            "supports_json_mode": False,
            "supports_function_calling": False
        }
    
    @property
    def supports_streaming(self) -> bool:
        return False
    
    @property
    def max_context_length(self) -> int:
        return 0  # Not applicable for basic matching
    
    def _extract_fields_from_html(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract form fields from HTML content"""
        # Simple field extraction - in a real implementation, this would use BeautifulSoup
        fields = []
        
        # Look for common form field patterns
        if "first name" in html_content.lower() or "firstname" in html_content.lower():
            fields.append({
                "field_id": "first_name",
                "label": "First Name",
                "field_type": "text",
                "required": True
            })
        
        if "last name" in html_content.lower() or "lastname" in html_content.lower():
            fields.append({
                "field_id": "last_name",
                "label": "Last Name",
                "field_type": "text",
                "required": True
            })
        
        if "email" in html_content.lower():
            fields.append({
                "field_id": "email",
                "label": "Email",
                "field_type": "email",
                "required": True
            })
        
        if "phone" in html_content.lower():
            fields.append({
                "field_id": "phone",
                "label": "Phone",
                "field_type": "tel",
                "required": False
            })
        
        return fields
    
    def _match_single_field(self, field: FormField, profile: UserProfile) -> Optional[Dict[str, Any]]:
        """Match a single field to profile data"""
        label_lower = field.label.lower()
        
        # Find best matching pattern
        best_match = None
        best_score = 0
        
        for profile_path, patterns in self.field_patterns.items():
            for pattern in patterns:
                score = fuzz.ratio(label_lower, pattern.lower())
                if score > best_score and score > 70:  # Minimum threshold
                    best_score = score
                    best_match = profile_path
        
        if best_match:
            # Extract value from profile
            value = self._extract_profile_value(profile, best_match)
            
            return {
                "field_id": field.field_id,
                "profile_mapping": best_match,
                "confidence_score": best_score,
                "response_value": value,
                "mapping_source": "pattern_match"
            }
        
        return None
    
    def _extract_profile_value(self, profile: UserProfile, profile_path: str) -> Any:
        """Extract value from profile using dot notation path"""
        try:
            parts = profile_path.split('.')
            current = profile
            
            for part in parts:
                if hasattr(current, part):
                    current = getattr(current, part)
                else:
                    return None
            
            return current
        except Exception:
            return None
    
    def _generate_basic_response(self, field_info: FormField, profile_data: Any) -> str:
        """Generate basic responses for fields"""
        if field_info.field_type.value == 'textarea':
            if 'cover letter' in field_info.label.lower():
                return "I am excited to apply for this position and believe my experience makes me a strong candidate."
            elif 'why' in field_info.label.lower():
                return "I am passionate about this role and believe my skills align well with your requirements."
        
        # Return profile data if available
        if profile_data:
            return str(profile_data)
        
        return ""
