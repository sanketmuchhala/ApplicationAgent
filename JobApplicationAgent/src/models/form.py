from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum

from .application import FormField, FormSection, FieldType


class FormAnalysisType(str, Enum):
    BASIC = "basic"
    DETAILED = "detailed" 
    COMPREHENSIVE = "comprehensive"


class FieldMappingConfidence(str, Enum):
    LOW = "low"          # 0-40%
    MEDIUM = "medium"    # 41-70%
    HIGH = "high"        # 71-90%
    VERY_HIGH = "very_high"  # 91-100%


class MappingSource(str, Enum):
    AI_ANALYSIS = "ai_analysis"
    FUZZY_MATCHING = "fuzzy_matching" 
    EXACT_MATCH = "exact_match"
    USER_CORRECTION = "user_correction"
    LEARNED_PATTERN = "learned_pattern"


class FieldMapping(BaseModel):
    # Mapping Identity
    field_id: str = Field(..., description="Form field identifier")
    profile_path: str = Field(..., description="Dot notation path to profile field")
    
    # Mapping Quality
    confidence_score: float = Field(..., ge=0.0, le=100.0, description="Confidence in mapping")
    confidence_level: FieldMappingConfidence = Field(..., description="Confidence level category")
    mapping_source: MappingSource = Field(..., description="How mapping was determined")
    
    # Context Information
    field_label: str = Field(..., description="Original field label")
    field_type: FieldType = Field(..., description="Field type")
    field_context: List[str] = Field(default_factory=list, description="Context clues")
    
    # Mapping Details
    direct_match: bool = Field(default=False, description="Whether it's a direct value mapping")
    requires_transformation: bool = Field(default=False, description="Needs data transformation")
    transformation_notes: Optional[str] = Field(None, description="Transformation details")
    
    # Alternative Mappings
    alternative_mappings: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Validation
    is_validated: bool = Field(default=False, description="Whether mapping has been validated")
    validation_date: Optional[datetime] = Field(None, description="When mapping was validated")
    validation_source: Optional[str] = Field(None, description="Who/what validated")
    
    # Learning Data
    user_corrections: List[Dict[str, Any]] = Field(default_factory=list)
    success_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    usage_count: int = Field(default=0, description="How many times this mapping was used")
    
    @validator('confidence_level')
    def set_confidence_level(cls, v, values):
        score = values.get('confidence_score', 0)
        if score <= 40:
            return FieldMappingConfidence.LOW
        elif score <= 70:
            return FieldMappingConfidence.MEDIUM
        elif score <= 90:
            return FieldMappingConfidence.HIGH
        else:
            return FieldMappingConfidence.VERY_HIGH


class FieldValidation(BaseModel):
    field_id: str = Field(..., description="Field identifier")
    validation_type: str = Field(..., description="Type of validation")
    
    # Validation Rules
    required: bool = Field(default=False)
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    allowed_values: List[str] = Field(default_factory=list)
    
    # Custom Validation
    custom_validator: Optional[str] = Field(None, description="Custom validation function")
    error_message: Optional[str] = Field(None, description="Custom error message")
    
    # File Upload Validation
    max_file_size: Optional[int] = None
    allowed_file_types: List[str] = Field(default_factory=list)
    
    def validate_value(self, value: Any) -> tuple[bool, Optional[str]]:
        """Validate a value against this field's rules"""
        if self.required and (value is None or value == ""):
            return False, "This field is required"
        
        if value is None or value == "":
            return True, None
            
        # String validations
        if isinstance(value, str):
            if self.min_length and len(value) < self.min_length:
                return False, f"Minimum length is {self.min_length} characters"
            
            if self.max_length and len(value) > self.max_length:
                return False, f"Maximum length is {self.max_length} characters"
            
            if self.pattern:
                import re
                if not re.match(self.pattern, value):
                    return False, self.error_message or "Invalid format"
        
        # Allowed values
        if self.allowed_values and value not in self.allowed_values:
            return False, f"Value must be one of: {', '.join(self.allowed_values)}"
        
        return True, None


class FormMetadata(BaseModel):
    # Form Identity
    form_url: Optional[str] = Field(None, description="Source URL of form")
    form_title: Optional[str] = Field(None, description="Form title")
    company_name: Optional[str] = Field(None, description="Detected company name")
    position_title: Optional[str] = Field(None, description="Detected position")
    
    # Form Characteristics
    form_type: str = Field(default="standard", description="Type of application form")
    is_multi_step: bool = Field(default=False, description="Multi-step form")
    total_steps: Optional[int] = Field(None, description="Number of steps if multi-step")
    
    # Complexity Analysis
    complexity_score: float = Field(default=0.0, ge=0.0, le=10.0)
    complexity_factors: List[str] = Field(default_factory=list)
    
    # Completion Estimates
    estimated_completion_time: Optional[str] = Field(None)
    total_fields: int = Field(default=0)
    required_fields: int = Field(default=0)
    optional_fields: int = Field(default=0)
    
    # File Requirements
    files_required: List[str] = Field(default_factory=list)
    files_optional: List[str] = Field(default_factory=list)
    
    # Analysis Metadata
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    analysis_type: FormAnalysisType = Field(default=FormAnalysisType.BASIC)
    ai_processed: bool = Field(default=False)
    processing_time_ms: Optional[int] = None


class CompletionStrategy(BaseModel):
    # Field Ordering
    recommended_order: List[str] = Field(default_factory=list, description="Recommended completion order")
    section_priorities: Dict[str, str] = Field(default_factory=dict)
    
    # Critical Fields
    critical_fields: List[str] = Field(default_factory=list)
    optional_skip_fields: List[str] = Field(default_factory=list)
    
    # Time Management
    time_sensitive_fields: List[str] = Field(default_factory=list)
    fields_requiring_customization: List[str] = Field(default_factory=list)
    
    # Dependencies
    field_dependencies: Dict[str, List[str]] = Field(default_factory=dict)
    conditional_fields: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class FormIssue(BaseModel):
    issue_type: str = Field(..., description="Type of issue")
    field_id: Optional[str] = Field(None, description="Related field ID")
    severity: str = Field(..., description="Issue severity: low, medium, high, critical")
    
    message: str = Field(..., description="Issue description")
    suggestion: Optional[str] = Field(None, description="Suggested resolution")
    
    # Technical Details
    technical_details: Optional[Dict[str, Any]] = Field(None)
    
    def is_blocking(self) -> bool:
        """Check if this issue prevents form completion"""
        return self.severity in ["high", "critical"]


class Form(BaseModel):
    # Identity
    form_id: str = Field(..., description="Unique form identifier") 
    source_url: Optional[str] = Field(None, description="Form source URL")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_analyzed: Optional[datetime] = None
    
    # Structure
    sections: List[FormSection] = Field(default_factory=list)
    metadata: FormMetadata = Field(default_factory=FormMetadata)
    
    # Analysis Results
    field_mappings: List[FieldMapping] = Field(default_factory=list)
    validations: List[FieldValidation] = Field(default_factory=list)
    completion_strategy: CompletionStrategy = Field(default_factory=CompletionStrategy)
    
    # Issues and Warnings
    issues: List[FormIssue] = Field(default_factory=list)
    
    # AI Processing
    ai_analysis_complete: bool = Field(default=False)
    ai_confidence_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    
    # Learning Data
    successful_submissions: int = Field(default=0)
    failed_submissions: int = Field(default=0)
    user_feedback: List[Dict[str, Any]] = Field(default_factory=list)
    
    def add_field_mapping(self, mapping: FieldMapping):
        """Add or update field mapping"""
        # Remove existing mapping for same field
        self.field_mappings = [m for m in self.field_mappings if m.field_id != mapping.field_id]
        self.field_mappings.append(mapping)
        self.updated_at = datetime.now()
    
    def get_mapping_for_field(self, field_id: str) -> Optional[FieldMapping]:
        """Get mapping for specific field"""
        for mapping in self.field_mappings:
            if mapping.field_id == field_id:
                return mapping
        return None
    
    def get_high_confidence_mappings(self) -> List[FieldMapping]:
        """Get mappings with high confidence"""
        return [m for m in self.field_mappings 
                if m.confidence_level in [FieldMappingConfidence.HIGH, FieldMappingConfidence.VERY_HIGH]]
    
    def add_validation(self, validation: FieldValidation):
        """Add field validation rule"""
        # Remove existing validation for same field
        self.validations = [v for v in self.validations if v.field_id != validation.field_id]
        self.validations.append(validation)
        self.updated_at = datetime.now()
    
    def get_validation_for_field(self, field_id: str) -> Optional[FieldValidation]:
        """Get validation rules for field"""
        for validation in self.validations:
            if validation.field_id == field_id:
                return validation
        return None
    
    def add_issue(self, issue: FormIssue):
        """Add form issue"""
        self.issues.append(issue)
        self.updated_at = datetime.now()
    
    def get_blocking_issues(self) -> List[FormIssue]:
        """Get issues that block form completion"""
        return [issue for issue in self.issues if issue.is_blocking()]
    
    def calculate_complexity_score(self) -> float:
        """Calculate form complexity score (0-10)"""
        score = 0.0
        factors = []
        
        # Base complexity from field count
        total_fields = sum(len(section.fields) for section in self.sections)
        score += min(total_fields * 0.1, 3.0)
        
        if total_fields > 20:
            factors.append("High field count")
        
        # File upload complexity
        file_fields = 0
        for section in self.sections:
            for field in section.fields:
                if field.field_type == FieldType.FILE:
                    file_fields += 1
        
        if file_fields > 0:
            score += file_fields * 0.5
            factors.append(f"{file_fields} file upload(s)")
        
        # Text area complexity (essays, descriptions)
        textarea_fields = 0
        for section in self.sections:
            for field in section.fields:
                if field.field_type == FieldType.TEXTAREA:
                    textarea_fields += 1
        
        if textarea_fields > 2:
            score += 1.0
            factors.append("Multiple essay questions")
        
        # Multi-step complexity
        if self.metadata.is_multi_step:
            score += 1.0
            factors.append("Multi-step form")
        
        # Required fields ratio
        required_count = self.metadata.required_fields
        if total_fields > 0:
            required_ratio = required_count / total_fields
            if required_ratio > 0.7:
                score += 0.5
                factors.append("High required field ratio")
        
        self.metadata.complexity_score = min(score, 10.0)
        self.metadata.complexity_factors = factors
        
        return self.metadata.complexity_score
    
    def get_field_by_id(self, field_id: str) -> Optional[FormField]:
        """Get field by ID"""
        for section in self.sections:
            for field in section.fields:
                if field.field_id == field_id:
                    return field
        return None
    
    def update_from_analysis(self, analysis_result: Dict[str, Any]):
        """Update form from AI analysis result"""
        if "metadata" in analysis_result:
            # Update metadata
            meta = analysis_result["metadata"]
            self.metadata.form_title = meta.get("title")
            self.metadata.company_name = meta.get("company")
            self.metadata.position_title = meta.get("position")
            
        if "sections" in analysis_result:
            # Update sections and fields
            for section_data in analysis_result["sections"]:
                section = FormSection(
                    section_id=section_data.get("section_id", f"section_{len(self.sections)}"),
                    section_name=section_data["section_name"],
                    section_order=section_data["section_order"]
                )
                self.sections.append(section)
        
        if "issues" in analysis_result:
            # Add identified issues
            for issue_data in analysis_result["issues"]:
                issue = FormIssue(
                    issue_type=issue_data["issue_type"],
                    field_id=issue_data.get("field_id"),
                    severity=issue_data["severity"],
                    message=issue_data["message"],
                    suggestion=issue_data.get("suggestion")
                )
                self.add_issue(issue)
        
        self.last_analyzed = datetime.now()
        self.ai_analysis_complete = True