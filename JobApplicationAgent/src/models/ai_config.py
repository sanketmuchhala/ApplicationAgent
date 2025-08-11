from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class AIProviderType(str, Enum):
    DEEPSEEK = "deepseek"
    LOCAL = "local"
    BASIC_MATCHING = "basic_matching"


class RateLimit(BaseModel):
    requests_per_minute: int = Field(default=100, description="Max requests per minute")
    tokens_per_minute: int = Field(default=500000, description="Max tokens per minute")


class ProviderFeatures(BaseModel):
    field_matching: bool = Field(default=False, description="Can match form fields to profile")
    response_generation: bool = Field(default=False, description="Can generate contextual responses")
    form_analysis: bool = Field(default=False, description="Can analyze HTML forms")
    context_understanding: bool = Field(default=False, description="Can understand job/company context")


class AIProviderConfig(BaseModel):
    name: str = Field(..., description="Human-readable provider name")
    provider_type: AIProviderType = Field(..., description="Type of AI provider")
    enabled: bool = Field(default=True, description="Whether provider is enabled")
    
    # API Configuration
    api_base: Optional[str] = Field(None, description="API base URL")
    api_key: Optional[str] = Field(None, description="API key for authentication")
    model: str = Field(..., description="Model name/identifier")
    
    # Model Parameters
    max_tokens: int = Field(default=4000, description="Maximum tokens per request")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="Sampling temperature")
    
    # Cost Configuration
    cost_per_1k_input: float = Field(default=0.0, ge=0.0, description="Cost per 1k input tokens")
    cost_per_1k_output: float = Field(default=0.0, ge=0.0, description="Cost per 1k output tokens")
    
    # Rate Limiting
    rate_limit: RateLimit = Field(default_factory=RateLimit, description="Rate limiting settings")
    
    # Features
    features: ProviderFeatures = Field(default_factory=ProviderFeatures, description="Supported features")
    
    # Additional Settings
    timeout_seconds: int = Field(default=30, gt=0, description="Request timeout in seconds")
    retry_attempts: int = Field(default=3, ge=0, description="Number of retry attempts")
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v


class CostTracking(BaseModel):
    enabled: bool = Field(default=True, description="Whether cost tracking is enabled")
    monthly_budget: float = Field(default=10.0, gt=0, description="Monthly budget in USD")
    alert_threshold: float = Field(default=0.8, ge=0.0, le=1.0, description="Budget alert threshold (0-1)")
    currency: str = Field(default="USD", description="Currency for cost tracking")
    
    # Current Period Tracking
    current_month: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m"))
    month_to_date_cost: float = Field(default=0.0, ge=0.0, description="Cost for current month")
    month_to_date_tokens_input: int = Field(default=0, ge=0, description="Input tokens used this month")
    month_to_date_tokens_output: int = Field(default=0, ge=0, description="Output tokens used this month")
    
    @validator('alert_threshold')
    def validate_alert_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Alert threshold must be between 0.0 and 1.0')
        return v


class PerformanceSettings(BaseModel):
    cache_enabled: bool = Field(default=True, description="Whether response caching is enabled")
    cache_ttl_hours: int = Field(default=24, gt=0, description="Cache time-to-live in hours")
    batch_processing: bool = Field(default=True, description="Whether batch processing is enabled")
    max_batch_size: int = Field(default=10, gt=0, description="Maximum batch size for processing")
    parallel_requests: int = Field(default=3, gt=0, le=10, description="Max parallel requests")


class AIConfiguration(BaseModel):
    """Complete AI configuration for the application"""
    providers: Dict[str, AIProviderConfig] = Field(..., description="Available AI providers")
    default_provider: str = Field(..., description="Default provider to use")
    fallback_provider: str = Field(..., description="Fallback provider if default fails")
    
    cost_tracking: CostTracking = Field(default_factory=CostTracking)
    performance: PerformanceSettings = Field(default_factory=PerformanceSettings)
    
    @validator('default_provider')
    def validate_default_provider(cls, v, values):
        providers = values.get('providers', {})
        if v not in providers:
            raise ValueError(f'Default provider "{v}" not found in providers')
        return v
    
    @validator('fallback_provider')
    def validate_fallback_provider(cls, v, values):
        providers = values.get('providers', {})
        if v not in providers:
            raise ValueError(f'Fallback provider "{v}" not found in providers')
        return v


class UsageMetrics(BaseModel):
    """Tracks usage statistics for AI providers"""
    provider: str
    timestamp: datetime = Field(default_factory=datetime.now)
    operation_type: str  # 'field_matching', 'response_generation', 'form_analysis'
    
    # Token Usage
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(default=0, ge=0)
    
    # Cost Information
    input_cost: float = Field(default=0.0, ge=0.0)
    output_cost: float = Field(default=0.0, ge=0.0)
    total_cost: float = Field(default=0.0, ge=0.0)
    
    # Performance Metrics
    response_time_ms: int = Field(default=0, ge=0)
    success: bool = Field(default=True)
    error_message: Optional[str] = None
    
    # Context Information
    form_complexity_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    field_count: Optional[int] = Field(None, ge=0)
    
    @validator('total_tokens')
    def calculate_total_tokens(cls, v, values):
        input_tokens = values.get('input_tokens', 0)
        output_tokens = values.get('output_tokens', 0)
        return input_tokens + output_tokens
    
    @validator('total_cost')
    def calculate_total_cost(cls, v, values):
        input_cost = values.get('input_cost', 0.0)
        output_cost = values.get('output_cost', 0.0)
        return input_cost + output_cost


class AIResponse(BaseModel):
    """Standardized response format from AI providers"""
    success: bool
    provider: str
    operation_type: str
    
    # Response Data
    data: Optional[Dict[str, Any]] = None
    
    # Metadata
    confidence_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    processing_time_ms: int = Field(default=0, ge=0)
    
    # Token Usage
    tokens_used: Optional[int] = None
    estimated_cost: Optional[float] = None
    
    # Error Information
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    
    # Additional Context
    requires_human_review: bool = Field(default=False)
    alternative_suggestions: Optional[List[Dict[str, Any]]] = None