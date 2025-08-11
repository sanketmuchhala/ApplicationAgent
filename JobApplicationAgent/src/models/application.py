from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum


class ApplicationStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    REJECTED = "rejected"
    ACCEPTED = "accepted"
    WITHDRAWN = "withdrawn"


class FieldType(str, Enum):
    TEXT = "text"
    EMAIL = "email"
    PHONE = "tel"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"
    RADIO = "radio"
    CHECKBOX = "checkbox"
    TEXTAREA = "textarea"
    FILE = "file"
    HIDDEN = "hidden"
    URL = "url"
    PASSWORD = "password"


class ValidationRule(BaseModel):
    rule_type: str = Field(..., description="Type of validation rule")
    value: Any = Field(..., description="Validation value/pattern")
    message: str = Field(..., description="Error message if validation fails")


class FormField(BaseModel):
    # Field Identity
    field_id: str = Field(..., description="Unique field identifier")
    field_name: str = Field(..., description="HTML name attribute")
    label: str = Field(..., description="Field label/question text")
    
    # Field Properties
    field_type: FieldType = Field(..., description="Type of form field")
    input_type: Optional[str] = Field(None, description="HTML input type attribute")
    
    # Requirements
    required: bool = Field(default=False, description="Whether field is required")
    placeholder: Optional[str] = Field(None, description="Placeholder text")
    max_length: Optional[int] = Field(None, description="Maximum character length")
    min_length: Optional[int] = Field(None, description="Minimum character length")
    
    # Options for select/radio/checkbox fields
    options: List[str] = Field(default_factory=list, description="Available options")
    multiple: bool = Field(default=False, description="Whether multiple selections allowed")
    
    # Context and Positioning
    section: Optional[str] = Field(None, description="Section this field belongs to")
    section_order: Optional[int] = Field(None, description="Order within section")
    context_clues: List[str] = Field(default_factory=list, description="Surrounding text for context")
    
    # Validation
    validation_rules: List[ValidationRule] = Field(default_factory=list)
    validation_pattern: Optional[str] = Field(None, description="Regex validation pattern")
    
    # AI Analysis Results
    likely_profile_mapping: Optional[str] = Field(None, description="Suggested profile field mapping")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    
    # Field Value
    value: Optional[Any] = Field(None, description="Current field value")
    ai_generated: bool = Field(default=False, description="Whether value was AI-generated")
    
    # File Upload Specific
    accepted_file_types: List[str] = Field(default_factory=list, description="Accepted file extensions")
    max_file_size: Optional[int] = Field(None, description="Max file size in bytes")
    
    # Special Requirements
    custom_validation: Optional[str] = Field(None, description="Custom validation requirements")
    requires_human_input: bool = Field(default=False, description="Requires manual input/review")


class FormSection(BaseModel):
    section_id: str = Field(..., description="Unique section identifier")
    section_name: str = Field(..., description="Display name of section")
    section_order: int = Field(..., description="Order in form")
    
    description: Optional[str] = Field(None, description="Section description")
    fields: List[FormField] = Field(default_factory=list, description="Fields in this section")
    
    # Completion Status
    is_completed: bool = Field(default=False, description="Whether section is completed")
    completion_priority: str = Field(default="medium", description="Priority for completion")
    
    # Conditional Logic
    show_conditions: Optional[Dict[str, Any]] = Field(None, description="Conditions for showing section")
    dependency_fields: List[str] = Field(default_factory=list, description="Fields this section depends on")


class JobDetails(BaseModel):
    job_title: str = Field(..., description="Job title/position")
    company_name: str = Field(..., description="Company name")
    job_url: Optional[HttpUrl] = Field(None, description="Job posting URL")
    
    # Job Information
    department: Optional[str] = Field(None, description="Department/team")
    location: Optional[str] = Field(None, description="Job location")
    employment_type: Optional[str] = Field(None, description="Full-time, contract, etc.")
    
    # Job Description
    job_description: Optional[str] = Field(None, description="Full job description")
    key_requirements: List[str] = Field(default_factory=list, description="Key job requirements")
    preferred_qualifications: List[str] = Field(default_factory=list)
    
    # Compensation
    salary_range_min: Optional[int] = Field(None, description="Minimum salary")
    salary_range_max: Optional[int] = Field(None, description="Maximum salary")
    benefits: List[str] = Field(default_factory=list, description="Listed benefits")
    
    # Company Information
    company_size: Optional[str] = Field(None, description="Company size range")
    industry: Optional[str] = Field(None, description="Company industry")
    company_culture: Optional[str] = Field(None, description="Company culture description")


class ApplicationMetadata(BaseModel):
    # Timing
    application_deadline: Optional[datetime] = Field(None, description="Application deadline")
    estimated_completion_time: Optional[str] = Field(None, description="Estimated time to complete")
    
    # Form Characteristics
    form_complexity_score: Optional[float] = Field(None, ge=0.0, le=10.0)
    total_fields: int = Field(default=0, description="Total number of fields")
    required_fields: int = Field(default=0, description="Number of required fields")
    
    # Files Required
    resume_required: bool = Field(default=False)
    cover_letter_required: bool = Field(default=False)
    portfolio_required: bool = Field(default=False)
    additional_documents: List[str] = Field(default_factory=list)
    
    # AI Processing
    ai_processed: bool = Field(default=False, description="Whether AI has processed this application")
    ai_confidence: Optional[float] = Field(None, ge=0.0, le=100.0)
    human_review_needed: bool = Field(default=False)
    
    # Source Information
    application_source: Optional[str] = Field(None, description="Where application was found")
    referral_source: Optional[str] = Field(None, description="Referral information")


class Application(BaseModel):
    # Identity
    application_id: str = Field(..., description="Unique application identifier")
    profile_id: str = Field(..., description="Associated user profile ID")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    submitted_at: Optional[datetime] = Field(None)
    
    # Status
    status: ApplicationStatus = Field(default=ApplicationStatus.DRAFT)
    status_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Job and Company Information
    job_details: JobDetails = Field(..., description="Job and company information")
    
    # Form Structure
    sections: List[FormSection] = Field(default_factory=list, description="Form sections")
    form_url: Optional[HttpUrl] = Field(None, description="Application form URL")
    
    # Completion Status
    completion_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    completed_sections: List[str] = Field(default_factory=list)
    remaining_fields: List[str] = Field(default_factory=list)
    
    # Files
    uploaded_files: Dict[str, str] = Field(default_factory=dict, description="Uploaded file paths")
    
    # AI Processing
    ai_suggestions: Dict[str, Any] = Field(default_factory=dict, description="AI suggestions for responses")
    field_mappings: Dict[str, str] = Field(default_factory=dict, description="Field to profile mappings")
    
    # Metadata
    metadata: ApplicationMetadata = Field(default_factory=ApplicationMetadata)
    
    # Notes and Comments
    notes: Optional[str] = Field(None, description="Personal notes about application")
    internal_comments: List[str] = Field(default_factory=list)
    
    # Follow-up Information
    follow_up_date: Optional[datetime] = Field(None)
    interview_dates: List[datetime] = Field(default_factory=list)
    
    def update_status(self, new_status: ApplicationStatus, note: Optional[str] = None):
        """Update application status with history tracking"""
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now()
        
        # Add to status history
        history_entry = {
            "timestamp": self.updated_at,
            "from_status": old_status,
            "to_status": new_status,
            "note": note
        }
        self.status_history.append(history_entry)
        
        # Set submitted timestamp
        if new_status == ApplicationStatus.SUBMITTED and not self.submitted_at:
            self.submitted_at = self.updated_at
    
    def calculate_completion_percentage(self) -> float:
        """Calculate completion percentage based on filled required fields"""
        if not self.sections:
            return 0.0
        
        total_required = 0
        completed_required = 0
        
        for section in self.sections:
            for field in section.fields:
                if field.required:
                    total_required += 1
                    if field.value is not None and field.value != "":
                        completed_required += 1
        
        if total_required == 0:
            return 100.0
        
        percentage = (completed_required / total_required) * 100.0
        self.completion_percentage = round(percentage, 1)
        return self.completion_percentage
    
    def get_field_by_id(self, field_id: str) -> Optional[FormField]:
        """Get field by ID across all sections"""
        for section in self.sections:
            for field in section.fields:
                if field.field_id == field_id:
                    return field
        return None
    
    def get_section_by_id(self, section_id: str) -> Optional[FormSection]:
        """Get section by ID"""
        for section in self.sections:
            if section.section_id == section_id:
                return section
        return None
    
    def get_required_fields(self) -> List[FormField]:
        """Get all required fields"""
        required_fields = []
        for section in self.sections:
            for field in section.fields:
                if field.required:
                    required_fields.append(field)
        return required_fields
    
    def get_incomplete_fields(self) -> List[FormField]:
        """Get incomplete required fields"""
        incomplete = []
        for section in self.sections:
            for field in section.fields:
                if field.required and (field.value is None or field.value == ""):
                    incomplete.append(field)
        return incomplete
    
    def add_ai_suggestion(self, field_id: str, suggestion: Dict[str, Any]):
        """Add AI suggestion for a field"""
        self.ai_suggestions[field_id] = suggestion
        self.updated_at = datetime.now()
    
    def set_field_mapping(self, field_id: str, profile_path: str):
        """Set field to profile mapping"""
        self.field_mappings[field_id] = profile_path
        self.updated_at = datetime.now()
    
    def is_ready_for_submission(self) -> bool:
        """Check if application is ready for submission"""
        incomplete_fields = self.get_incomplete_fields()
        return len(incomplete_fields) == 0
    
    @property 
    def days_since_created(self) -> int:
        """Get number of days since application was created"""
        return (datetime.now() - self.created_at).days
    
    @property
    def is_overdue(self) -> bool:
        """Check if application is overdue based on deadline"""
        if not self.metadata.application_deadline:
            return False
        return datetime.now() > self.metadata.application_deadline