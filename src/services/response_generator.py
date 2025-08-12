from typing import Dict, List, Optional, Any, Union
import re
from datetime import datetime

from .ai_service import AIService
from ..models.form import FormField, FieldType
from ..models.profile import UserProfile
from ..models.ai_config import AIResponse


class ResponseGenerator:
    """Generates appropriate responses for form fields"""
    
    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service
        
        # Response templates for common field types
        self.response_templates = {
            "cover_letter": {
                "opening": "I am excited to apply for the {position} position at {company}. With {years} years of experience in {field}, I believe I would be a valuable addition to your team.",
                "body": "In my current role as {current_position} at {current_company}, I have {achievement}. My experience with {skills} and passion for {industry} make me well-suited for this opportunity.",
                "closing": "I would welcome the opportunity to discuss how my experience and enthusiasm can contribute to {company}'s continued success. Thank you for your consideration."
            },
            "why_interested": [
                "I am drawn to {company} because of your reputation for {company_value} and commitment to {mission}.",
                "This role aligns perfectly with my career goals and expertise in {relevant_skills}.",
                "I am excited about the opportunity to contribute to {company}'s innovative work in {industry}."
            ],
            "strengths": [
                "Strong problem-solving abilities and attention to detail",
                "Excellent communication and collaboration skills", 
                "Adaptability and eagerness to learn new technologies",
                "Leadership experience and mentoring capabilities"
            ]
        }
    
    async def generate_field_response(
        self,
        field: FormField,
        profile: UserProfile,
        profile_value: Any,
        job_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate appropriate response for a form field"""
        
        # Try AI generation first if available
        if self.ai_service and self._should_use_ai(field):
            try:
                ai_result = await self.ai_service.generate_field_response(
                    field, profile_value, job_context
                )
                
                if ai_result.success and ai_result.data:
                    return self._enhance_ai_response(ai_result.data, field, profile_value)
                    
            except Exception as e:
                print(f"AI response generation failed, using fallback: {str(e)}")
        
        # Use template-based generation as fallback
        return await self._template_based_generation(field, profile, profile_value, job_context)
    
    def _should_use_ai(self, field: FormField) -> bool:
        """Determine if AI should be used for this field type"""
        # Use AI for complex text fields that require customization
        ai_suitable_types = [FieldType.TEXTAREA]
        
        if field.field_type in ai_suitable_types:
            return True
        
        # Use AI for fields that likely need contextual responses
        ai_keywords = [
            'why', 'describe', 'tell us', 'explain', 'cover letter', 
            'motivation', 'interest', 'experience', 'achievement'
        ]
        
        label_lower = field.label.lower()
        return any(keyword in label_lower for keyword in ai_keywords)
    
    def _enhance_ai_response(
        self, 
        ai_data: Dict[str, Any], 
        field: FormField, 
        profile_value: Any
    ) -> Dict[str, Any]:
        """Enhance AI response with additional validation and formatting"""
        
        response = ai_data.get('response', '')
        
        # Validate response meets field constraints
        if field.max_length and len(response) > field.max_length:
            # Truncate response intelligently
            truncated = self._intelligent_truncate(response, field.max_length)
            ai_data['response'] = truncated
            ai_data['truncated'] = True
            ai_data['original_length'] = len(response)
        
        # Validate required field has content
        if field.required and not response.strip():
            ai_data['response'] = str(profile_value) if profile_value else "Please see resume for details"
            ai_data['fallback_used'] = True
        
        # Add formatting validation
        ai_data['formatting_valid'] = self._validate_response_format(response, field)
        
        return ai_data
    
    async def _template_based_generation(
        self,
        field: FormField,
        profile: UserProfile, 
        profile_value: Any,
        job_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate response using templates and profile data"""
        
        # Handle different field types
        if field.field_type == FieldType.TEXTAREA:
            return await self._generate_textarea_response(field, profile, job_context)
        
        elif field.field_type == FieldType.SELECT:
            return self._generate_select_response(field, profile_value)
        
        elif field.field_type == FieldType.RADIO:
            return self._generate_radio_response(field, profile_value)
        
        elif field.field_type == FieldType.CHECKBOX:
            return self._generate_checkbox_response(field, profile_value)
        
        else:
            # Direct value fields (text, email, phone, etc.)
            return self._generate_direct_response(field, profile_value)
    
    async def _generate_textarea_response(
        self,
        field: FormField,
        profile: UserProfile,
        job_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate response for textarea fields"""
        
        label_lower = field.label.lower()
        
        # Cover letter responses
        if any(keyword in label_lower for keyword in ['cover letter', 'cover', 'letter']):
            response = self._generate_cover_letter(profile, job_context, field.max_length)
            
        # Why interested responses  
        elif any(keyword in label_lower for keyword in ['why', 'interest', 'motivation']):
            response = self._generate_interest_response(profile, job_context)
            
        # Experience descriptions
        elif any(keyword in label_lower for keyword in ['experience', 'background', 'describe']):
            response = self._generate_experience_description(profile)
            
        # Strengths/skills responses
        elif any(keyword in label_lower for keyword in ['strength', 'skill', 'qualification']):
            response = self._generate_strengths_response(profile)
            
        # Goals/career objective
        elif any(keyword in label_lower for keyword in ['goal', 'objective', 'career']):
            response = self._generate_goals_response(profile, job_context)
            
        # Generic professional response
        else:
            response = self._generate_generic_professional_response(profile, field.label)
        
        # Ensure response meets constraints
        if field.max_length and len(response) > field.max_length:
            response = self._intelligent_truncate(response, field.max_length)
        
        return {
            "response": response,
            "character_count": len(response),
            "fits_constraints": True,
            "confidence_score": 75.0,
            "personalization_level": "medium",
            "generation_method": "template_based"
        }
    
    def _generate_cover_letter(
        self,
        profile: UserProfile,
        job_context: Optional[Dict[str, Any]],
        max_length: Optional[int] = None
    ) -> str:
        """Generate cover letter content"""
        
        # Get context information
        company = job_context.get('company_name', '[Company Name]') if job_context else '[Company Name]'
        position = job_context.get('job_title', '[Position]') if job_context else '[Position]'
        
        # Build cover letter from profile
        opening = self.response_templates["cover_letter"]["opening"].format(
            position=position,
            company=company,
            years=profile.total_experience_years,
            field=profile.technical_skills[0] if profile.technical_skills else "technology"
        )
        
        # Body paragraph
        current_position = profile.current_position
        body = ""
        if current_position:
            achievement = current_position.key_achievements[0] if current_position.key_achievements else "developed innovative solutions"
            skills = ", ".join(profile.technical_skills[:3]) if profile.technical_skills else "various technologies"
            industry = job_context.get('industry', 'this field') if job_context else 'this field'
            
            body = self.response_templates["cover_letter"]["body"].format(
                current_position=current_position.position,
                current_company=current_position.company,
                achievement=achievement,
                skills=skills,
                industry=industry
            )
        
        # Closing paragraph
        closing = self.response_templates["cover_letter"]["closing"].format(company=company)
        
        # Combine sections
        full_response = f"{opening}\n\n{body}\n\n{closing}"
        
        # Adjust length if needed
        if max_length and len(full_response) > max_length:
            # Try shorter version
            short_response = f"{opening}\n\n{closing}"
            if len(short_response) <= max_length:
                return short_response
            else:
                # Truncate intelligently
                return self._intelligent_truncate(full_response, max_length)
        
        return full_response
    
    def _generate_interest_response(
        self,
        profile: UserProfile,
        job_context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate why interested response"""
        
        company = job_context.get('company_name', 'this company') if job_context else 'this company'
        
        # Use relevant skills from profile
        relevant_skills = ", ".join(profile.technical_skills[:3]) if profile.technical_skills else "my technical expertise"
        
        responses = [
            f"I am excited about the opportunity to contribute to {company}'s innovative work and apply my experience with {relevant_skills}.",
            f"This role aligns perfectly with my career goals and passion for {profile.job_preferences.industries[0] if profile.job_preferences.industries else 'technology'}.",
            f"I am drawn to {company} because of your reputation for excellence and the opportunity to work with cutting-edge technologies."
        ]
        
        return " ".join(responses[:2])  # Use first two responses
    
    def _generate_experience_description(self, profile: UserProfile) -> str:
        """Generate experience description"""
        
        if not profile.experience:
            return "Please see my attached resume for detailed work experience."
        
        # Get most recent experience
        recent_exp = profile.experience[0]
        
        description = f"I have {profile.total_experience_years} years of professional experience"
        
        if recent_exp:
            description += f", most recently as {recent_exp.position} at {recent_exp.company}"
            
            if recent_exp.key_achievements:
                description += f". Key achievements include {recent_exp.key_achievements[0]}"
        
        if profile.technical_skills:
            skills_text = ", ".join(profile.technical_skills[:5])
            description += f". My technical expertise includes {skills_text}."
        
        return description
    
    def _generate_strengths_response(self, profile: UserProfile) -> str:
        """Generate strengths/skills response"""
        
        strengths = []
        
        # Technical skills
        if profile.technical_skills:
            skills_text = ", ".join(profile.technical_skills[:4])
            strengths.append(f"Strong technical expertise in {skills_text}")
        
        # Soft skills
        if profile.soft_skills:
            soft_skills_text = ", ".join(profile.soft_skills[:3])
            strengths.append(soft_skills_text)
        else:
            # Default soft skills
            strengths.extend(self.response_templates["strengths"][:2])
        
        # Experience-based strengths
        if profile.experience:
            years = profile.total_experience_years
            strengths.append(f"{years} years of hands-on industry experience")
        
        return ". ".join(strengths) + "."
    
    def _generate_goals_response(
        self,
        profile: UserProfile,
        job_context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate career goals response"""
        
        desired_roles = profile.job_preferences.desired_roles
        industries = profile.job_preferences.industries
        
        response = "My career goal is to continue growing as a"
        
        if desired_roles:
            response += f" {desired_roles[0]}"
        else:
            response += " professional"
        
        if industries:
            response += f" in the {industries[0]} industry"
        
        response += ", taking on increasing responsibility and contributing to innovative projects that make a meaningful impact."
        
        if job_context and job_context.get('company_name'):
            response += f" I see this role at {job_context['company_name']} as an excellent step toward achieving these goals."
        
        return response
    
    def _generate_generic_professional_response(self, profile: UserProfile, field_label: str) -> str:
        """Generate generic professional response"""
        
        if profile.summary_statement:
            return profile.summary_statement
        
        # Create basic professional summary
        response = f"I am a dedicated professional with {profile.total_experience_years} years of experience"
        
        if profile.technical_skills:
            skills = ", ".join(profile.technical_skills[:3])
            response += f" in {skills}"
        
        response += ". I am passionate about delivering high-quality results and contributing to team success."
        
        return response
    
    def _generate_select_response(self, field: FormField, profile_value: Any) -> Dict[str, Any]:
        """Generate response for select field"""
        
        if not field.options:
            return {
                "response": str(profile_value) if profile_value else "",
                "confidence_score": 60.0,
                "fits_constraints": True
            }
        
        # Try to find best matching option
        profile_str = str(profile_value).lower() if profile_value else ""
        
        best_match = None
        best_score = 0
        
        for option in field.options:
            option_lower = option.lower()
            
            # Exact match
            if profile_str == option_lower:
                best_match = option
                best_score = 100
                break
            
            # Substring matches
            if profile_str in option_lower or option_lower in profile_str:
                score = 80
                if score > best_score:
                    best_match = option
                    best_score = score
        
        # If no good match found, use first option or profile value
        if not best_match:
            best_match = field.options[0] if field.options else str(profile_value)
            best_score = 30
        
        return {
            "response": best_match,
            "confidence_score": best_score,
            "fits_constraints": True,
            "original_value": profile_value,
            "matched_option": best_match != str(profile_value)
        }
    
    def _generate_radio_response(self, field: FormField, profile_value: Any) -> Dict[str, Any]:
        """Generate response for radio field"""
        # Same logic as select field
        return self._generate_select_response(field, profile_value)
    
    def _generate_checkbox_response(self, field: FormField, profile_value: Any) -> Dict[str, Any]:
        """Generate response for checkbox field"""
        
        # For checkbox, profile_value should be boolean or list
        if isinstance(profile_value, bool):
            response = profile_value
        elif isinstance(profile_value, list):
            response = len(profile_value) > 0
        elif profile_value:
            response = True
        else:
            response = False
        
        return {
            "response": response,
            "confidence_score": 90.0,
            "fits_constraints": True
        }
    
    def _generate_direct_response(self, field: FormField, profile_value: Any) -> Dict[str, Any]:
        """Generate response for direct value fields"""
        
        if profile_value is None:
            return {
                "response": "",
                "confidence_score": 0.0,
                "fits_constraints": field.required == False,
                "error": "No profile value available"
            }
        
        response = str(profile_value)
        
        # Format response based on field type
        if field.field_type == FieldType.EMAIL:
            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            is_valid_email = re.match(email_pattern, response) is not None
            
            return {
                "response": response,
                "confidence_score": 95.0 if is_valid_email else 50.0,
                "fits_constraints": is_valid_email,
                "format_valid": is_valid_email
            }
        
        elif field.field_type == FieldType.PHONE:
            # Clean phone number format
            cleaned_phone = re.sub(r'[^\d]', '', response)
            if len(cleaned_phone) == 10:
                formatted_phone = f"({cleaned_phone[:3]}) {cleaned_phone[3:6]}-{cleaned_phone[6:]}"
            else:
                formatted_phone = response
            
            return {
                "response": formatted_phone,
                "confidence_score": 90.0,
                "fits_constraints": True
            }
        
        # Default direct response
        return {
            "response": response,
            "confidence_score": 85.0,
            "fits_constraints": True
        }
    
    def _intelligent_truncate(self, text: str, max_length: int) -> str:
        """Intelligently truncate text while preserving meaning"""
        
        if len(text) <= max_length:
            return text
        
        # Try to truncate at sentence boundaries
        sentences = text.split('. ')
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence + '. ') <= max_length:
                truncated += sentence + '. '
            else:
                break
        
        if truncated:
            return truncated.strip()
        
        # If no full sentences fit, truncate at word boundaries
        words = text.split()
        truncated = ""
        
        for word in words:
            if len(truncated + word + ' ') <= max_length - 3:  # Leave space for '...'
                truncated += word + ' '
            else:
                break
        
        return truncated.strip() + '...'
    
    def _validate_response_format(self, response: str, field: FormField) -> bool:
        """Validate response format against field requirements"""
        
        if field.field_type == FieldType.EMAIL:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return re.match(email_pattern, response) is not None
        
        elif field.field_type == FieldType.PHONE:
            # Allow various phone formats
            phone_pattern = r'^[\d\s\-\(\)\.]{10,}$'
            return re.match(phone_pattern, response) is not None
        
        elif field.field_type == FieldType.NUMBER:
            try:
                float(response)
                return True
            except (ValueError, TypeError):
                return False
        
        elif field.field_type == FieldType.URL:
            url_pattern = r'^https?://'
            return re.match(url_pattern, response.lower()) is not None
        
        # For other field types, basic validation
        if field.max_length and len(response) > field.max_length:
            return False
        
        if field.required and not response.strip():
            return False
        
        return True