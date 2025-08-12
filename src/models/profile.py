from datetime import datetime, date
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum


class WorkAuthorizationStatus(str, Enum):
    CITIZEN = "citizen"
    PERMANENT_RESIDENT = "permanent_resident"
    WORK_VISA = "work_visa"
    NEEDS_SPONSORSHIP = "needs_sponsorship"


class ExperienceLevel(str, Enum):
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"
    EXECUTIVE = "executive"


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"


class RemotePreference(str, Enum):
    REMOTE_ONLY = "remote_only"
    HYBRID = "hybrid"
    ON_SITE = "on_site"
    FLEXIBLE = "flexible"


class PersonalInfo(BaseModel):
    first_name: str = Field(..., min_length=1, description="First name")
    last_name: str = Field(..., min_length=1, description="Last name")
    middle_name: Optional[str] = Field(None, description="Middle name")
    preferred_name: Optional[str] = Field(None, description="Preferred/nickname")
    
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    
    # Address Information
    address_line1: Optional[str] = Field(None, description="Street address")
    address_line2: Optional[str] = Field(None, description="Apartment, suite, etc.")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/Province")
    postal_code: Optional[str] = Field(None, description="ZIP/Postal code")
    country: str = Field(default="United States", description="Country")
    
    # Work Authorization
    work_authorization: WorkAuthorizationStatus = Field(..., description="Work authorization status")
    visa_type: Optional[str] = Field(None, description="Visa type if applicable")
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)
    
    @property
    def display_name(self) -> str:
        """Get preferred display name"""
        if self.preferred_name:
            return f"{self.preferred_name} {self.last_name}"
        return self.full_name


class ContactInfo(BaseModel):
    email: EmailStr = Field(..., description="Primary email address")
    phone: str = Field(..., min_length=10, description="Phone number")
    secondary_email: Optional[EmailStr] = Field(None, description="Secondary email")
    
    # Professional Profiles
    linkedin_url: Optional[str] = Field(None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(None, description="GitHub profile URL")
    portfolio_url: Optional[str] = Field(None, description="Portfolio website URL")
    
    # Additional Contact Methods
    website: Optional[str] = Field(None, description="Personal website")
    twitter_handle: Optional[str] = Field(None, description="Twitter handle")
    
    @validator('linkedin_url', 'github_url', 'portfolio_url', 'website')
    def validate_urls(cls, v):
        if v and not (v.startswith('http://') or v.startswith('https://')):
            return f'https://{v}'
        return v


class Experience(BaseModel):
    company: str = Field(..., min_length=1, description="Company name")
    position: str = Field(..., min_length=1, description="Job title/position")
    start_date: date = Field(..., description="Start date")
    end_date: Optional[date] = Field(None, description="End date (None if current)")
    
    description: str = Field(..., min_length=10, description="Job description and achievements")
    key_achievements: List[str] = Field(default_factory=list, description="Key achievements")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    skills_developed: List[str] = Field(default_factory=list, description="Skills developed")
    
    location: Optional[str] = Field(None, description="Work location")
    employment_type: EmploymentType = Field(default=EmploymentType.FULL_TIME)
    
    is_current: bool = Field(default=False, description="Whether this is current position")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v
    
    @property
    def duration_months(self) -> int:
        """Calculate duration in months"""
        end = self.end_date or date.today()
        years = end.year - self.start_date.year
        months = end.month - self.start_date.month
        return years * 12 + months
    
    @property
    def duration_display(self) -> str:
        """Get human-readable duration"""
        months = self.duration_months
        if months < 12:
            return f"{months} month{'s' if months != 1 else ''}"
        
        years = months // 12
        remaining_months = months % 12
        
        result = f"{years} year{'s' if years != 1 else ''}"
        if remaining_months > 0:
            result += f" {remaining_months} month{'s' if remaining_months != 1 else ''}"
        
        return result


class Education(BaseModel):
    institution: str = Field(..., min_length=1, description="School/University name")
    degree: str = Field(..., min_length=1, description="Degree type (BS, MS, PhD, etc.)")
    field_of_study: str = Field(..., min_length=1, description="Major/Field of study")
    
    start_date: date = Field(..., description="Start date")
    end_date: Optional[date] = Field(None, description="End date (graduation)")
    
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0, description="GPA (4.0 scale)")
    honors: Optional[str] = Field(None, description="Academic honors")
    
    relevant_coursework: List[str] = Field(default_factory=list, description="Relevant courses")
    activities: List[str] = Field(default_factory=list, description="Extracurricular activities")
    
    location: Optional[str] = Field(None, description="School location")
    is_current: bool = Field(default=False, description="Currently enrolled")


class Compensation(BaseModel):
    current_salary: Optional[int] = Field(None, ge=0, description="Current annual salary")
    desired_salary_min: Optional[int] = Field(None, ge=0, description="Minimum desired salary")
    desired_salary_max: Optional[int] = Field(None, ge=0, description="Maximum desired salary")
    
    salary_negotiable: bool = Field(default=True, description="Whether salary is negotiable")
    hourly_rate: Optional[float] = Field(None, ge=0.0, description="Hourly rate for contract work")
    
    equity_interest: bool = Field(default=False, description="Interested in equity compensation")
    benefits_important: List[str] = Field(default_factory=list, description="Important benefits")
    
    @validator('desired_salary_max')
    def validate_salary_range(cls, v, values):
        min_salary = values.get('desired_salary_min')
        if v and min_salary and v < min_salary:
            raise ValueError('Maximum salary must be greater than minimum salary')
        return v


class JobPreferences(BaseModel):
    desired_roles: List[str] = Field(default_factory=list, description="Desired job titles/roles")
    industries: List[str] = Field(default_factory=list, description="Preferred industries")
    company_sizes: List[str] = Field(default_factory=list, description="Preferred company sizes")
    
    employment_types: List[EmploymentType] = Field(default_factory=list, description="Employment types")
    remote_preference: RemotePreference = Field(default=RemotePreference.FLEXIBLE)
    
    willing_to_relocate: bool = Field(default=False, description="Willing to relocate")
    preferred_locations: List[str] = Field(default_factory=list, description="Preferred work locations")
    
    travel_comfort: Optional[str] = Field(None, description="Comfort with travel requirements")
    start_date_availability: Optional[date] = Field(None, description="Earliest start date")
    
    notice_period_weeks: int = Field(default=2, ge=0, description="Notice period in weeks")


class CoverLetterTemplate(BaseModel):
    template_name: str = Field(..., description="Template name/identifier")
    opening_paragraph: str = Field(..., description="Opening paragraph template")
    body_paragraph: str = Field(..., description="Main body template")
    closing_paragraph: str = Field(..., description="Closing paragraph template")
    
    placeholders: Dict[str, str] = Field(default_factory=dict, description="Template placeholders")
    industry_specific: Optional[str] = Field(None, description="Industry this template is for")


class UserProfile(BaseModel):
    # Metadata
    profile_id: str = Field(..., description="Unique profile identifier")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    version: str = Field(default="1.0", description="Profile version")
    
    # Core Information
    personal: PersonalInfo = Field(..., description="Personal information")
    contact: ContactInfo = Field(..., description="Contact information")
    
    # Professional Background
    experience: List[Experience] = Field(default_factory=list, description="Work experience")
    education: List[Education] = Field(default_factory=list, description="Education history")
    
    # Skills and Qualifications
    technical_skills: List[str] = Field(default_factory=list, description="Technical skills")
    soft_skills: List[str] = Field(default_factory=list, description="Soft skills")
    certifications: List[str] = Field(default_factory=list, description="Certifications")
    languages: Dict[str, str] = Field(default_factory=dict, description="Languages and proficiency")
    
    # Preferences and Requirements
    compensation: Compensation = Field(default_factory=Compensation)
    job_preferences: JobPreferences = Field(default_factory=JobPreferences)
    
    # Content Templates
    cover_letter_templates: List[CoverLetterTemplate] = Field(default_factory=list)
    summary_statement: Optional[str] = Field(None, description="Professional summary")
    
    # Files
    resume_path: Optional[str] = Field(None, description="Path to resume file")
    cover_letter_path: Optional[str] = Field(None, description="Path to cover letter file")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Profile tags for organization")
    notes: Optional[str] = Field(None, description="Personal notes")
    
    @property
    def total_experience_years(self) -> float:
        """Calculate total years of experience"""
        if not self.experience:
            return 0.0
        
        total_months = sum(exp.duration_months for exp in self.experience)
        return round(total_months / 12.0, 1)
    
    @property
    def current_position(self) -> Optional[Experience]:
        """Get current position if any"""
        for exp in self.experience:
            if exp.is_current:
                return exp
        return None
    
    @property
    def latest_education(self) -> Optional[Education]:
        """Get most recent education"""
        if not self.education:
            return None
        return max(self.education, key=lambda e: e.end_date or e.start_date)
    
    def update_timestamp(self):
        """Update the last modified timestamp"""
        self.updated_at = datetime.now()
    
    def add_experience(self, experience: Experience):
        """Add work experience and update current job status"""
        if experience.is_current:
            # Set all other experiences as not current
            for exp in self.experience:
                exp.is_current = False
        
        self.experience.append(experience)
        self.update_timestamp()
    
    def add_education(self, education: Education):
        """Add education record"""
        self.education.append(education)
        self.update_timestamp()
    
    def get_skills_by_category(self) -> Dict[str, List[str]]:
        """Organize skills by category based on experience"""
        skills_by_category = {
            "technical": self.technical_skills,
            "soft": self.soft_skills,
        }
        
        # Add technology skills from experience
        tech_from_exp = []
        for exp in self.experience:
            tech_from_exp.extend(exp.technologies)
        
        skills_by_category["technologies"] = list(set(tech_from_exp))
        
        return skills_by_category