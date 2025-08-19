from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from models.ai_config import AIResponse, UsageMetrics
from models.form import FormField
from models.profile import UserProfile


class AIService(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, provider_name: str, config: Dict[str, Any]):
        self.provider_name = provider_name
        self.config = config
        self.usage_metrics: List[UsageMetrics] = []
        self._total_cost = 0.0
        self._total_tokens = 0
    
    @abstractmethod
    async def analyze_form_fields(
        self, 
        html_content: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """
        Analyze HTML form content to extract and understand form fields
        
        Args:
            html_content: Raw HTML of the form
            context: Additional context (job description, company info, etc.)
            
        Returns:
            AIResponse with form analysis results
        """
        pass
    
    @abstractmethod
    async def match_fields_to_profile(
        self, 
        form_fields: List[FormField], 
        profile: UserProfile,
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """
        Match form fields to user profile data
        
        Args:
            form_fields: List of form fields to match
            profile: User profile with data to match against
            context: Additional context for matching
            
        Returns:
            AIResponse with field mappings and confidence scores
        """
        pass
    
    @abstractmethod
    async def generate_field_response(
        self, 
        field_info: FormField, 
        profile_data: Any,
        job_context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """
        Generate appropriate response for a specific form field
        
        Args:
            field_info: Information about the form field
            profile_data: Relevant data from user profile
            job_context: Job/company context for tailoring response
            
        Returns:
            AIResponse with generated response and metadata
        """
        pass
    
    @abstractmethod
    async def improve_from_feedback(
        self, 
        original_response: str, 
        corrected_response: str, 
        context: Dict[str, Any]
    ) -> AIResponse:
        """
        Learn from user corrections to improve future responses
        
        Args:
            original_response: The AI's original response
            corrected_response: User's corrected response
            context: Context about the field, job, etc.
            
        Returns:
            AIResponse indicating if learning was successful
        """
        pass
    
    # Cost and Usage Tracking
    
    def record_usage(
        self, 
        operation_type: str, 
        input_tokens: int = 0, 
        output_tokens: int = 0,
        response_time_ms: int = 0,
        success: bool = True,
        error_message: Optional[str] = None,
        **kwargs
    ) -> UsageMetrics:
        """Record usage metrics for an operation"""
        
        # Calculate costs based on config
        input_cost = input_tokens * self.config.get('cost_per_1k_input', 0.0) / 1000
        output_cost = output_tokens * self.config.get('cost_per_1k_output', 0.0) / 1000
        
        metrics = UsageMetrics(
            provider=self.provider_name,
            operation_type=operation_type,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            response_time_ms=response_time_ms,
            success=success,
            error_message=error_message,
            **kwargs
        )
        
        self.usage_metrics.append(metrics)
        self._total_cost += metrics.total_cost
        self._total_tokens += metrics.total_tokens
        
        return metrics
    
    def get_usage_stats(self, timeframe: str = "all") -> Dict[str, Any]:
        """Get usage statistics"""
        if timeframe == "all":
            metrics = self.usage_metrics
        elif timeframe == "today":
            today = datetime.now().date()
            metrics = [m for m in self.usage_metrics if m.timestamp.date() == today]
        elif timeframe == "month":
            this_month = datetime.now().strftime("%Y-%m")
            metrics = [m for m in self.usage_metrics 
                      if m.timestamp.strftime("%Y-%m") == this_month]
        else:
            metrics = self.usage_metrics
        
        if not metrics:
            return {
                "total_requests": 0,
                "total_cost": 0.0,
                "total_tokens": 0,
                "success_rate": 0.0,
                "average_response_time": 0
            }
        
        total_requests = len(metrics)
        successful_requests = sum(1 for m in metrics if m.success)
        total_cost = sum(m.total_cost for m in metrics)
        total_tokens = sum(m.total_tokens for m in metrics)
        avg_response_time = sum(m.response_time_ms for m in metrics) / len(metrics)
        
        # Operation breakdown
        operations = {}
        for metric in metrics:
            op = metric.operation_type
            if op not in operations:
                operations[op] = {
                    "count": 0,
                    "cost": 0.0,
                    "tokens": 0,
                    "avg_time": 0
                }
            operations[op]["count"] += 1
            operations[op]["cost"] += metric.total_cost
            operations[op]["tokens"] += metric.total_tokens
        
        # Calculate averages for operations
        for op_stats in operations.values():
            if op_stats["count"] > 0:
                op_stats["avg_time"] = sum(
                    m.response_time_ms for m in metrics 
                    if m.operation_type in operations.keys()
                ) / op_stats["count"]
        
        return {
            "provider": self.provider_name,
            "timeframe": timeframe,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": (successful_requests / total_requests) * 100,
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "average_response_time_ms": round(avg_response_time, 2),
            "operations": operations,
            "cost_per_request": round(total_cost / total_requests, 4) if total_requests > 0 else 0.0
        }
    
    def estimate_cost(
        self, 
        estimated_input_tokens: int, 
        estimated_output_tokens: int
    ) -> float:
        """Estimate cost for a request"""
        input_cost = estimated_input_tokens * self.config.get('cost_per_1k_input', 0.0) / 1000
        output_cost = estimated_output_tokens * self.config.get('cost_per_1k_output', 0.0) / 1000
        return input_cost + output_cost
    
    def get_monthly_cost(self, month: Optional[str] = None) -> float:
        """Get total cost for a specific month"""
        if month is None:
            month = datetime.now().strftime("%Y-%m")
        
        monthly_metrics = [
            m for m in self.usage_metrics 
            if m.timestamp.strftime("%Y-%m") == month
        ]
        
        return sum(m.total_cost for m in monthly_metrics)
    
    def is_within_budget(self, monthly_budget: float) -> Tuple[bool, float, float]:
        """Check if current usage is within monthly budget"""
        current_cost = self.get_monthly_cost()
        percentage_used = (current_cost / monthly_budget) * 100 if monthly_budget > 0 else 0.0
        
        return current_cost <= monthly_budget, current_cost, percentage_used
    
    # Abstract helper methods
    
    @abstractmethod
    async def test_connection(self) -> bool:
        """Test connection to AI provider"""
        pass
    
    @abstractmethod
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the AI model"""
        pass
    
    @property
    @abstractmethod
    def supports_streaming(self) -> bool:
        """Whether provider supports streaming responses"""
        pass
    
    @property
    @abstractmethod
    def max_context_length(self) -> int:
        """Maximum context length supported by the model"""
        pass
    
    # Utility methods for all providers
    
    def _count_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        Basic implementation - should be overridden by providers with better tokenization
        """
        # Rough estimation: ~4 characters per token for English text
        return len(text) // 4
    
    def _create_success_response(
        self, 
        operation_type: str, 
        data: Dict[str, Any],
        confidence_score: Optional[float] = None,
        processing_time_ms: int = 0,
        tokens_used: Optional[int] = None,
        estimated_cost: Optional[float] = None
    ) -> AIResponse:
        """Create successful AI response"""
        return AIResponse(
            success=True,
            provider=self.provider_name,
            operation_type=operation_type,
            data=data,
            confidence_score=confidence_score,
            processing_time_ms=processing_time_ms,
            tokens_used=tokens_used,
            estimated_cost=estimated_cost
        )
    
    def _create_error_response(
        self, 
        operation_type: str, 
        error_message: str,
        error_code: Optional[str] = None,
        processing_time_ms: int = 0
    ) -> AIResponse:
        """Create error AI response"""
        return AIResponse(
            success=False,
            provider=self.provider_name,
            operation_type=operation_type,
            error_message=error_message,
            error_code=error_code,
            processing_time_ms=processing_time_ms
        )
    
    async def cleanup(self):
        """Cleanup resources (override if needed)"""
        pass