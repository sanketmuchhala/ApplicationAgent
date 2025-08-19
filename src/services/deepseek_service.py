import json
import time
import asyncio
from typing import Dict, List, Optional, Any
import httpx
import tiktoken
from openai import AsyncOpenAI

from .ai_service import AIService
from models.ai_config import AIResponse
from models.form import FormField
from models.profile import UserProfile
from utils.prompts import PromptManager


class DeepSeekService(AIService):
    """DeepSeek AI provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("deepseek", config)
        
        # Initialize OpenAI client for DeepSeek API
        self.client = AsyncOpenAI(
            api_key=config.get('api_key'),
            base_url=config.get('api_base', 'https://api.deepseek.com/v1')
        )
        
        self.model = config.get('model', 'deepseek-chat')
        self.max_tokens = config.get('max_tokens', 4000)
        self.temperature = config.get('temperature', 0.1)
        self.timeout = config.get('timeout_seconds', 30)
        
        # Initialize tokenizer for accurate token counting
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")  # Use GPT tokenizer as approximation
        except KeyError:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # Load prompts
        self.prompt_manager = PromptManager()
        
        # Rate limiting
        self.rate_limit = config.get('rate_limit', {})
        self.request_timestamps = []
        
    async def analyze_form_fields(
        self, 
        html_content: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """Analyze HTML form content using DeepSeek"""
        start_time = time.time()
        operation_type = "form_analysis"
        
        try:
            # Check rate limits
            await self._check_rate_limits()
            
            # Prepare the prompt
            system_prompt = self.prompt_manager.get_form_analysis_prompt()
            
            user_message = f"Analyze this job application form:\n\nHTML Content:\n{html_content}"
            
            if context:
                user_message += f"\n\nAdditional Context:\n{json.dumps(context, indent=2)}"
            
            # Count tokens
            input_tokens = self._count_tokens_accurate(system_prompt + user_message)
            
            # Make API call
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result_text = response.choices[0].message.content
            output_tokens = response.usage.completion_tokens if response.usage else self._count_tokens_accurate(result_text)
            
            try:
                result_data = json.loads(result_text)
            except json.JSONDecodeError:
                # Fallback: try to extract JSON from response
                result_data = self._extract_json_from_text(result_text)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # Record usage
            self.record_usage(
                operation_type=operation_type,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                response_time_ms=processing_time,
                success=True,
                form_complexity_score=result_data.get('form_complexity', {}).get('score'),
                field_count=result_data.get('form_metadata', {}).get('total_fields', 0)
            )
            
            # Determine confidence based on completeness of analysis
            confidence = self._calculate_analysis_confidence(result_data)
            
            return self._create_success_response(
                operation_type=operation_type,
                data=result_data,
                confidence_score=confidence,
                processing_time_ms=processing_time,
                tokens_used=input_tokens + output_tokens,
                estimated_cost=self.estimate_cost(input_tokens, output_tokens)
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            error_message = f"DeepSeek form analysis failed: {str(e)}"
            
            # Record failed usage
            self.record_usage(
                operation_type=operation_type,
                response_time_ms=processing_time,
                success=False,
                error_message=error_message
            )
            
            return self._create_error_response(
                operation_type=operation_type,
                error_message=error_message,
                processing_time_ms=processing_time
            )
    
    async def match_fields_to_profile(
        self, 
        form_fields: List[FormField], 
        profile: UserProfile,
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """Match form fields to profile data using DeepSeek"""
        start_time = time.time()
        operation_type = "field_matching"
        
        try:
            await self._check_rate_limits()
            
            # Prepare field information
            fields_info = []
            for field in form_fields:
                field_info = {
                    "field_id": field.field_id,
                    "label": field.label,
                    "type": field.field_type.value,
                    "required": field.required,
                    "options": field.options,
                    "context_clues": field.context_clues,
                    "section": field.section
                }
                fields_info.append(field_info)
            
            # Prepare profile summary
            profile_summary = self._create_profile_summary(profile)
            
            system_prompt = self.prompt_manager.get_field_matching_prompt()
            
            user_message = f"""Match these form fields to the user's profile:

Form Fields:
{json.dumps(fields_info, indent=2)}

User Profile Summary:
{json.dumps(profile_summary, indent=2)}"""
            
            if context:
                user_message += f"\n\nJob/Company Context:\n{json.dumps(context, indent=2)}"
            
            input_tokens = self._count_tokens_accurate(system_prompt + user_message)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            output_tokens = response.usage.completion_tokens if response.usage else self._count_tokens_accurate(result_text)
            
            try:
                result_data = json.loads(result_text)
            except json.JSONDecodeError:
                result_data = self._extract_json_from_text(result_text)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # Record usage
            self.record_usage(
                operation_type=operation_type,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                response_time_ms=processing_time,
                success=True,
                field_count=len(form_fields)
            )
            
            # Calculate average confidence
            mappings = result_data.get('field_mappings', [])
            avg_confidence = sum(m.get('confidence_score', 0) for m in mappings) / len(mappings) if mappings else 0
            
            return self._create_success_response(
                operation_type=operation_type,
                data=result_data,
                confidence_score=avg_confidence,
                processing_time_ms=processing_time,
                tokens_used=input_tokens + output_tokens,
                estimated_cost=self.estimate_cost(input_tokens, output_tokens)
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            error_message = f"DeepSeek field matching failed: {str(e)}"
            
            self.record_usage(
                operation_type=operation_type,
                response_time_ms=processing_time,
                success=False,
                error_message=error_message
            )
            
            return self._create_error_response(
                operation_type=operation_type,
                error_message=error_message,
                processing_time_ms=processing_time
            )
    
    async def generate_field_response(
        self, 
        field_info: FormField, 
        profile_data: Any,
        job_context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """Generate response for a form field using DeepSeek"""
        start_time = time.time()
        operation_type = "response_generation"
        
        try:
            await self._check_rate_limits()
            
            system_prompt = self.prompt_manager.get_response_generation_prompt()
            
            field_details = {
                "label": field_info.label,
                "type": field_info.field_type.value,
                "required": field_info.required,
                "max_length": field_info.max_length,
                "options": field_info.options,
                "context": field_info.context_clues
            }
            
            user_message = f"""Generate a response for this field:

Field Information:
{json.dumps(field_details, indent=2)}

Profile Data:
{json.dumps(profile_data, indent=2, default=str)}"""
            
            if job_context:
                user_message += f"\n\nJob Context:\n{json.dumps(job_context, indent=2)}"
            
            input_tokens = self._count_tokens_accurate(system_prompt + user_message)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=min(self.max_tokens, 2000),  # Shorter for response generation
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            output_tokens = response.usage.completion_tokens if response.usage else self._count_tokens_accurate(result_text)
            
            try:
                result_data = json.loads(result_text)
            except json.JSONDecodeError:
                result_data = self._extract_json_from_text(result_text)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            # Validate response meets field constraints
            generated_response = result_data.get('response', '')
            if field_info.max_length and len(generated_response) > field_info.max_length:
                result_data['response'] = generated_response[:field_info.max_length].rsplit(' ', 1)[0] + '...'
                result_data['truncated'] = True
            
            self.record_usage(
                operation_type=operation_type,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                response_time_ms=processing_time,
                success=True
            )
            
            return self._create_success_response(
                operation_type=operation_type,
                data=result_data,
                confidence_score=result_data.get('confidence_score'),
                processing_time_ms=processing_time,
                tokens_used=input_tokens + output_tokens,
                estimated_cost=self.estimate_cost(input_tokens, output_tokens)
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            error_message = f"DeepSeek response generation failed: {str(e)}"
            
            self.record_usage(
                operation_type=operation_type,
                response_time_ms=processing_time,
                success=False,
                error_message=error_message
            )
            
            return self._create_error_response(
                operation_type=operation_type,
                error_message=error_message,
                processing_time_ms=processing_time
            )
    
    async def improve_from_feedback(
        self, 
        original_response: str, 
        corrected_response: str, 
        context: Dict[str, Any]
    ) -> AIResponse:
        """Learn from user feedback (for now, just record the feedback)"""
        start_time = time.time()
        operation_type = "feedback_learning"
        
        # For now, we'll store the feedback for future model fine-tuning
        # In a production system, this would be sent to a training pipeline
        
        feedback_data = {
            "original_response": original_response,
            "corrected_response": corrected_response,
            "context": context,
            "timestamp": time.time(),
            "improvement_type": self._categorize_improvement(original_response, corrected_response)
        }
        
        processing_time = int((time.time() - start_time) * 1000)
        
        self.record_usage(
            operation_type=operation_type,
            input_tokens=self._count_tokens_accurate(original_response + corrected_response),
            output_tokens=0,
            response_time_ms=processing_time,
            success=True
        )
        
        return self._create_success_response(
            operation_type=operation_type,
            data={
                "feedback_recorded": True,
                "feedback_id": f"feedback_{int(time.time())}",
                "improvement_detected": len(corrected_response) != len(original_response)
            },
            processing_time_ms=processing_time
        )
    
    async def test_connection(self) -> bool:
        """Test connection to DeepSeek API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hello, this is a connection test."}],
                max_tokens=10,
                temperature=0.1
            )
            return response.choices[0].message.content is not None
        except Exception:
            return False
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get DeepSeek model information"""
        return {
            "provider": self.provider_name,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "context_length": self.max_context_length,
            "cost_per_1k_input": self.config.get('cost_per_1k_input', 0.0),
            "cost_per_1k_output": self.config.get('cost_per_1k_output', 0.0),
            "supports_json_mode": True,
            "supports_function_calling": False
        }
    
    @property
    def supports_streaming(self) -> bool:
        return True
    
    @property
    def max_context_length(self) -> int:
        # DeepSeek V3 supports large context windows
        return 64000
    
    # Helper methods
    
    def _count_tokens_accurate(self, text: str) -> int:
        """Count tokens using tiktoken for accuracy"""
        try:
            return len(self.tokenizer.encode(text))
        except Exception:
            # Fallback to basic estimation
            return super()._count_tokens(text)
    
    async def _check_rate_limits(self):
        """Check and enforce rate limits"""
        current_time = time.time()
        
        # Clean old timestamps (older than 1 minute)
        self.request_timestamps = [
            ts for ts in self.request_timestamps 
            if current_time - ts < 60
        ]
        
        # Check requests per minute limit
        requests_per_minute = self.rate_limit.get('requests_per_minute', 100)
        if len(self.request_timestamps) >= requests_per_minute:
            sleep_time = 60 - (current_time - self.request_timestamps[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
        
        # Record this request
        self.request_timestamps.append(current_time)
    
    def _create_profile_summary(self, profile: UserProfile) -> Dict[str, Any]:
        """Create a summary of user profile for AI processing"""
        return {
            "personal": {
                "name": profile.personal.full_name,
                "location": f"{profile.personal.city}, {profile.personal.state}" if profile.personal.city else None,
                "work_authorization": profile.personal.work_authorization.value
            },
            "contact": {
                "email": str(profile.contact.email),
                "phone": profile.contact.phone,
                "linkedin": profile.contact.linkedin_url,
                "portfolio": profile.contact.portfolio_url
            },
            "experience": {
                "total_years": profile.total_experience_years,
                "current_position": profile.current_position.position if profile.current_position else None,
                "current_company": profile.current_position.company if profile.current_position else None,
                "key_skills": profile.technical_skills[:10],  # Top 10 skills
                "recent_achievements": [exp.key_achievements[:3] for exp in profile.experience[:3]]  # Recent achievements
            },
            "education": {
                "latest_degree": profile.latest_education.degree if profile.latest_education else None,
                "latest_field": profile.latest_education.field_of_study if profile.latest_education else None,
                "institution": profile.latest_education.institution if profile.latest_education else None
            },
            "preferences": {
                "desired_salary_range": f"${profile.compensation.desired_salary_min}-${profile.compensation.desired_salary_max}" if profile.compensation.desired_salary_min else None,
                "remote_preference": profile.job_preferences.remote_preference.value,
                "preferred_roles": profile.job_preferences.desired_roles[:5],
                "preferred_industries": profile.job_preferences.industries[:5]
            }
        }
    
    def _calculate_analysis_confidence(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate confidence score for form analysis"""
        confidence = 50.0  # Base confidence
        
        # Increase confidence based on completeness
        if analysis_result.get('form_metadata'):
            confidence += 15.0
        if analysis_result.get('sections'):
            confidence += 15.0
        if analysis_result.get('fields'):
            confidence += 10.0
        if analysis_result.get('completion_strategy'):
            confidence += 10.0
        
        return min(confidence, 95.0)  # Cap at 95%
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract JSON from text if direct parsing fails"""
        try:
            # Try to find JSON within the text
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
        except Exception:
            pass
        
        # Return error format if extraction fails
        return {
            "error": "Failed to parse AI response",
            "raw_response": text[:500]  # First 500 chars for debugging
        }
    
    def _categorize_improvement(self, original: str, corrected: str) -> str:
        """Categorize the type of improvement made by user"""
        if len(corrected) > len(original) * 1.5:
            return "expansion"
        elif len(corrected) < len(original) * 0.7:
            return "condensation"
        elif original.lower() != corrected.lower():
            return "rephrasing"
        else:
            return "minor_correction"