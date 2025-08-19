from typing import Dict, List, Optional, Any, Tuple
from fuzzywuzzy import fuzz
import re

from .ai_service import AIService
from models.form import FormField, FieldMapping, MappingSource, FieldMappingConfidence
from models.profile import UserProfile
from models.ai_config import AIResponse


class SemanticMatcher:
    """Matches form fields to profile data using AI and fallback methods"""
    
    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service
        
        # Predefined field patterns for fallback matching
        self.field_patterns = {
            "personal.first_name": [
                r"first\s*name", r"firstname", r"given\s*name", r"forename"
            ],
            "personal.last_name": [
                r"last\s*name", r"lastname", r"surname", r"family\s*name"
            ],
            "personal.full_name": [
                r"full\s*name", r"complete\s*name", r"name", r"your\s*name"
            ],
            "contact.email": [
                r"email", r"e-mail", r"mail", r"email\s*address"
            ],
            "contact.phone": [
                r"phone", r"telephone", r"mobile", r"cell", r"contact\s*number"
            ],
            "personal.address_line1": [
                r"address", r"street", r"address\s*line\s*1"
            ],
            "personal.city": [
                r"city", r"town"
            ],
            "personal.state": [
                r"state", r"province", r"region"
            ],
            "personal.postal_code": [
                r"zip", r"postal", r"postcode", r"zip\s*code"
            ],
            "personal.country": [
                r"country", r"nation"
            ],
            "contact.linkedin_url": [
                r"linkedin", r"linked\s*in"
            ],
            "contact.github_url": [
                r"github", r"git\s*hub"
            ],
            "contact.portfolio_url": [
                r"portfolio", r"website", r"personal\s*site"
            ],
            "experience.total_years": [
                r"years?\s*of\s*experience", r"experience\s*years?", r"total\s*experience"
            ],
            "compensation.current_salary": [
                r"current\s*salary", r"present\s*salary", r"salary"
            ],
            "compensation.desired_salary_min": [
                r"desired\s*salary", r"expected\s*salary", r"salary\s*expectation"
            ]
        }
    
    async def match_fields_to_profile(
        self, 
        form_fields: List[FormField], 
        profile: UserProfile,
        context: Optional[Dict[str, Any]] = None
    ) -> List[FieldMapping]:
        """Match form fields to profile data using AI and fallback methods"""
        
        field_mappings = []
        
        # Try AI matching first if available
        if self.ai_service:
            try:
                ai_result = await self.ai_service.match_fields_to_profile(
                    form_fields, profile, context
                )
                
                if ai_result.success and ai_result.data:
                    ai_mappings = self._parse_ai_mappings(ai_result.data, form_fields)
                    field_mappings.extend(ai_mappings)
                    
                    # Fill in any missed fields with fallback matching
                    matched_field_ids = {mapping.field_id for mapping in ai_mappings}
                    unmatched_fields = [f for f in form_fields if f.field_id not in matched_field_ids]
                    
                    if unmatched_fields:
                        fallback_mappings = await self._fallback_field_matching(unmatched_fields, profile)
                        field_mappings.extend(fallback_mappings)
                    
                    return field_mappings
                    
            except Exception as e:
                print(f"AI field matching failed, using fallback: {str(e)}")
        
        # Use fallback matching if AI is not available or failed
        fallback_mappings = await self._fallback_field_matching(form_fields, profile)
        field_mappings.extend(fallback_mappings)
        
        return field_mappings
    
    def _parse_ai_mappings(self, ai_data: Dict[str, Any], form_fields: List[FormField]) -> List[FieldMapping]:
        """Parse AI response into FieldMapping objects"""
        mappings = []
        
        ai_mappings = ai_data.get('field_mappings', [])
        
        for mapping_data in ai_mappings:
            try:
                # Find the corresponding form field
                field_id = mapping_data.get('field_id')
                field = next((f for f in form_fields if f.field_id == field_id), None)
                
                if not field:
                    continue
                
                mapping = FieldMapping(
                    field_id=field_id,
                    profile_path=mapping_data.get('profile_mapping', ''),
                    confidence_score=mapping_data.get('confidence_score', 0.0),
                    mapping_source=MappingSource.AI_ANALYSIS,
                    field_label=field.label,
                    field_type=field.field_type,
                    field_context=field.context_clues,
                    direct_match=mapping_data.get('direct_match', True),
                    requires_transformation=mapping_data.get('requires_transformation', False),
                    transformation_notes=mapping_data.get('transformation_notes'),
                    alternative_mappings=mapping_data.get('alternative_mappings', [])
                )
                
                mappings.append(mapping)
                
            except Exception as e:
                print(f"Error parsing AI mapping: {str(e)}")
                continue
        
        return mappings
    
    async def _fallback_field_matching(
        self, 
        form_fields: List[FormField], 
        profile: UserProfile
    ) -> List[FieldMapping]:
        """Fallback field matching using pattern matching and fuzzy text similarity"""
        mappings = []
        
        for field in form_fields:
            # Try pattern matching first
            pattern_mapping = self._pattern_match_field(field, profile)
            if pattern_mapping:
                mappings.append(pattern_mapping)
                continue
            
            # Try fuzzy text matching
            fuzzy_mapping = self._fuzzy_match_field(field, profile)
            if fuzzy_mapping:
                mappings.append(fuzzy_mapping)
        
        return mappings
    
    def _pattern_match_field(self, field: FormField, profile: UserProfile) -> Optional[FieldMapping]:
        """Match field using regex patterns"""
        field_text = f"{field.label} {' '.join(field.context_clues)}".lower()
        
        best_match = None
        best_score = 0
        
        print(f"DEBUG Pattern Match: field_text='{field_text}'")
        
        for profile_path, patterns in self.field_patterns.items():
            for pattern in patterns:
                if re.search(pattern, field_text, re.IGNORECASE):
                    # Calculate confidence based on pattern specificity
                    confidence = self._calculate_pattern_confidence(pattern, field_text)
                    print(f"DEBUG: Pattern '{pattern}' matches '{field_text}' -> confidence={confidence}, profile_path={profile_path}")
                    
                    if confidence > best_score:
                        best_score = confidence
                        best_match = profile_path
                        print(f"DEBUG: New best pattern match: {profile_path} with confidence {confidence}")
        
        if best_match and best_score > 50:  # Lower confidence threshold for better matching
            return FieldMapping(
                field_id=field.field_id,
                profile_path=best_match,
                confidence_score=best_score,
                mapping_source=MappingSource.EXACT_MATCH if best_score > 90 else MappingSource.FUZZY_MATCHING,
                field_label=field.label,
                field_type=field.field_type,
                field_context=field.context_clues,
                direct_match=True
            )
        
        return None
    
    def _fuzzy_match_field(self, field: FormField, profile: UserProfile) -> Optional[FieldMapping]:
        """Match field using fuzzy text similarity"""
        field_text = field.label.lower()
        
        # Common field label variations to match against
        profile_field_labels = {
            "personal.first_name": ["first name", "given name", "forename"],
            "personal.last_name": ["last name", "surname", "family name"],
            "personal.full_name": ["full name", "complete name", "name"],
            "contact.email": ["email address", "email", "e-mail"],
            "contact.phone": ["phone number", "telephone", "mobile number"],
            "personal.city": ["city", "town"],
            "personal.state": ["state", "province"],
            "personal.country": ["country"],
            "experience.total_years": ["years of experience", "experience"],
            "compensation.current_salary": ["current salary", "salary"]
        }
        
        best_match = None
        best_score = 0
        
        for profile_path, label_variants in profile_field_labels.items():
            for label_variant in label_variants:
                # Use fuzzy string matching
                similarity = fuzz.partial_ratio(field_text, label_variant)
                
                if similarity > best_score and similarity > 60:  # Lower similarity threshold for better matching
                    best_score = similarity
                    best_match = profile_path
        
        if best_match:
            return FieldMapping(
                field_id=field.field_id,
                profile_path=best_match,
                confidence_score=best_score,
                mapping_source=MappingSource.FUZZY_MATCHING,
                field_label=field.label,
                field_type=field.field_type,
                field_context=field.context_clues,
                direct_match=False
            )
        
        return None
    
    def _calculate_pattern_confidence(self, pattern: str, field_text: str) -> float:
        """Calculate confidence score for pattern match"""
        # Exact matches get higher confidence
        if pattern in field_text:
            return 95.0
        
        # Partial matches get medium confidence
        if re.search(pattern, field_text, re.IGNORECASE):
            return 80.0
        
        return 0.0
    
    async def get_profile_value(self, profile: UserProfile, profile_path: str) -> Any:
        """Extract value from profile using dot notation path"""
        try:
            # Split the path and navigate through the profile object
            path_parts = profile_path.split('.')
            current_value = profile
            
            for part in path_parts:
                if hasattr(current_value, part):
                    current_value = getattr(current_value, part)
                elif isinstance(current_value, dict):
                    current_value = current_value.get(part)
                else:
                    return None
            
            # Handle special cases for computed properties
            if profile_path == "experience.total_years":
                return profile.total_experience_years
            elif profile_path == "personal.full_name":
                return profile.personal.full_name
            elif profile_path == "personal.display_name":
                return profile.personal.display_name
            
            return current_value
            
        except Exception as e:
            print(f"Error getting profile value for path {profile_path}: {str(e)}")
            return None
    
    async def validate_field_mapping(
        self, 
        mapping: FieldMapping, 
        profile: UserProfile,
        field: FormField
    ) -> Tuple[bool, Optional[str]]:
        """Validate that a field mapping is appropriate"""
        
        # Get the profile value
        profile_value = await self.get_profile_value(profile, mapping.profile_path)
        
        if profile_value is None:
            return False, f"No value found at profile path: {mapping.profile_path}"
        
        # Type compatibility checks
        if field.field_type.value == 'email':
            if '@' not in str(profile_value):
                return False, "Profile value is not a valid email format"
        
        elif field.field_type.value == 'tel':
            # Basic phone number validation
            phone_str = str(profile_value).replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            if not phone_str.isdigit() or len(phone_str) < 10:
                return False, "Profile value is not a valid phone number format"
        
        elif field.field_type.value == 'number':
            try:
                float(profile_value)
            except (ValueError, TypeError):
                return False, "Profile value is not numeric"
        
        elif field.field_type.value == 'select' and field.options:
            # Check if profile value matches one of the options
            profile_str = str(profile_value).lower()
            option_match = any(option.lower() in profile_str or profile_str in option.lower() 
                             for option in field.options)
            if not option_match:
                return False, f"Profile value '{profile_value}' doesn't match any field options"
        
        # Length constraints
        if field.max_length and len(str(profile_value)) > field.max_length:
            return False, f"Profile value exceeds field max length ({field.max_length})"
        
        return True, None
    
    async def improve_mapping_from_feedback(
        self, 
        field_id: str, 
        original_mapping: str, 
        corrected_mapping: str,
        context: Dict[str, Any]
    ) -> bool:
        """Learn from user corrections to improve future mappings"""
        
        # Store the correction for future learning
        correction_data = {
            "field_id": field_id,
            "original_mapping": original_mapping,
            "corrected_mapping": corrected_mapping,
            "context": context,
            "timestamp": str(datetime.now())
        }
        
        # If AI service is available, pass the feedback to it
        if self.ai_service:
            try:
                await self.ai_service.improve_from_feedback(
                    original_mapping, corrected_mapping, context
                )
            except Exception as e:
                print(f"Error passing feedback to AI service: {str(e)}")
        
        # TODO: Store correction in local learning database
        print(f"Recorded mapping correction: {field_id} -> {corrected_mapping}")
        
        return True