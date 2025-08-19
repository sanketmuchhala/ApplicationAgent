import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date

from models.profile import UserProfile
from models.form import FormField, FieldType
from models.application import Application


class ValidationError(Exception):
    """Custom exception for validation errors"""
    
    def __init__(self, field: str, message: str, error_code: Optional[str] = None):
        self.field = field
        self.message = message
        self.error_code = error_code
        super().__init__(f"{field}: {message}")


class Validator:
    """Comprehensive validation for profiles, forms, and applications"""
    
    def __init__(self, validation_rules_path: Optional[str] = None):
        if validation_rules_path is None:
            # Default to config/validation_rules.json
            current_dir = Path(__file__).parent.parent.parent
            validation_rules_path = current_dir / "config" / "validation_rules.json"
        
        self.rules_path = Path(validation_rules_path)
        self.validation_rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules from configuration file"""
        try:
            with open(self.rules_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Validation rules file not found: {self.rules_path}")
            return self._get_default_rules()
        except Exception as e:
            print(f"⚠️ Error loading validation rules: {str(e)}")
            return self._get_default_rules()
    
    def _get_default_rules(self) -> Dict[str, Any]:
        """Get default validation rules if config file is not available"""
        return {
            "field_validation_rules": {
                "email": {
                    "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                    "error_message": "Please enter a valid email address",
                    "required": True
                },
                "phone": {
                    "pattern": r"^[\d\s\-\(\)\.]{10,}$",
                    "error_message": "Please enter a valid phone number",
                    "min_length": 10,
                    "required": True
                }
            },
            "common_required_fields": [
                "first_name", "last_name", "email", "phone"
            ],
            "sensitive_fields": [
                "email", "phone", "address_line1"
            ]
        }
    
    # Profile Validation
    
    def validate_profile(self, profile: UserProfile) -> Tuple[bool, List[ValidationError]]:
        """Validate a complete user profile"""
        errors = []
        
        # Personal information validation
        errors.extend(self._validate_personal_info(profile.personal))
        
        # Contact information validation
        errors.extend(self._validate_contact_info(profile.contact))
        
        # Experience validation
        errors.extend(self._validate_experience(profile.experience))
        
        # Education validation
        errors.extend(self._validate_education(profile.education))
        
        # Compensation validation
        errors.extend(self._validate_compensation(profile.compensation))
        
        return len(errors) == 0, errors
    
    def _validate_personal_info(self, personal) -> List[ValidationError]:
        """Validate personal information"""
        errors = []
        
        if not personal.first_name or len(personal.first_name.strip()) == 0:
            errors.append(ValidationError("first_name", "First name is required"))
        
        if not personal.last_name or len(personal.last_name.strip()) == 0:
            errors.append(ValidationError("last_name", "Last name is required"))
        
        if personal.first_name and len(personal.first_name) > 50:
            errors.append(ValidationError("first_name", "First name must be 50 characters or less"))
        
        if personal.last_name and len(personal.last_name) > 50:
            errors.append(ValidationError("last_name", "Last name must be 50 characters or less"))
        
        # Validate postal code format if provided
        if personal.postal_code:
            if not self._validate_postal_code(personal.postal_code, personal.country):
                errors.append(ValidationError("postal_code", "Invalid postal code format"))
        
        return errors
    
    def _validate_contact_info(self, contact) -> List[ValidationError]:
        """Validate contact information"""
        errors = []
        
        # Email validation
        if not contact.email:
            errors.append(ValidationError("email", "Email address is required"))
        else:
            if not self._validate_email(str(contact.email)):
                errors.append(ValidationError("email", "Please enter a valid email address"))
        
        # Phone validation
        if not contact.phone:
            errors.append(ValidationError("phone", "Phone number is required"))
        else:
            if not self._validate_phone(contact.phone):
                errors.append(ValidationError("phone", "Please enter a valid phone number"))
        
        # URL validations
        if contact.linkedin_url and not self._validate_url(contact.linkedin_url):
            errors.append(ValidationError("linkedin_url", "Please enter a valid LinkedIn URL"))
        
        if contact.github_url and not self._validate_url(contact.github_url):
            errors.append(ValidationError("github_url", "Please enter a valid GitHub URL"))
        
        if contact.portfolio_url and not self._validate_url(contact.portfolio_url):
            errors.append(ValidationError("portfolio_url", "Please enter a valid portfolio URL"))
        
        return errors
    
    def _validate_experience(self, experiences) -> List[ValidationError]:
        """Validate work experience entries"""
        errors = []
        
        for i, exp in enumerate(experiences):
            field_prefix = f"experience[{i}]"
            
            if not exp.company or len(exp.company.strip()) == 0:
                errors.append(ValidationError(f"{field_prefix}.company", "Company name is required"))
            
            if not exp.position or len(exp.position.strip()) == 0:
                errors.append(ValidationError(f"{field_prefix}.position", "Position title is required"))
            
            if not exp.start_date:
                errors.append(ValidationError(f"{field_prefix}.start_date", "Start date is required"))
            
            # Validate date logic
            if exp.start_date and exp.end_date:
                if exp.end_date <= exp.start_date:
                    errors.append(ValidationError(
                        f"{field_prefix}.end_date", 
                        "End date must be after start date"
                    ))
            
            # Validate current job logic
            if exp.is_current and exp.end_date:
                errors.append(ValidationError(
                    f"{field_prefix}.is_current", 
                    "Current job should not have an end date"
                ))
        
        return errors
    
    def _validate_education(self, education_entries) -> List[ValidationError]:
        """Validate education entries"""
        errors = []
        
        for i, edu in enumerate(education_entries):
            field_prefix = f"education[{i}]"
            
            if not edu.institution or len(edu.institution.strip()) == 0:
                errors.append(ValidationError(f"{field_prefix}.institution", "Institution name is required"))
            
            if not edu.degree or len(edu.degree.strip()) == 0:
                errors.append(ValidationError(f"{field_prefix}.degree", "Degree is required"))
            
            if not edu.field_of_study or len(edu.field_of_study.strip()) == 0:
                errors.append(ValidationError(f"{field_prefix}.field_of_study", "Field of study is required"))
            
            # Validate GPA if provided
            if edu.gpa is not None:
                if not (0.0 <= edu.gpa <= 4.0):
                    errors.append(ValidationError(f"{field_prefix}.gpa", "GPA must be between 0.0 and 4.0"))
        
        return errors
    
    def _validate_compensation(self, compensation) -> List[ValidationError]:
        """Validate compensation information"""
        errors = []
        
        if compensation.desired_salary_min and compensation.desired_salary_max:
            if compensation.desired_salary_max < compensation.desired_salary_min:
                errors.append(ValidationError(
                    "compensation.desired_salary_max", 
                    "Maximum salary must be greater than minimum salary"
                ))
        
        # Validate salary ranges are reasonable
        if compensation.current_salary and compensation.current_salary > 1000000:
            errors.append(ValidationError("compensation.current_salary", "Current salary seems unreasonably high"))
        
        if compensation.desired_salary_min and compensation.desired_salary_min > 1000000:
            errors.append(ValidationError("compensation.desired_salary_min", "Desired salary seems unreasonably high"))
        
        return errors
    
    # Form Field Validation
    
    def validate_form_field(self, field: FormField, value: Any) -> Tuple[bool, Optional[str]]:
        """Validate a single form field value"""
        try:
            # Check if required field has value
            if field.required and (value is None or value == ""):
                return False, "This field is required"
            
            # If no value and not required, it's valid
            if value is None or value == "":
                return True, None
            
            # Type-specific validation
            if field.field_type == FieldType.EMAIL:
                return self._validate_email(str(value)), "Please enter a valid email address"
            
            elif field.field_type == FieldType.PHONE:
                return self._validate_phone(str(value)), "Please enter a valid phone number"
            
            elif field.field_type == FieldType.URL:
                return self._validate_url(str(value)), "Please enter a valid URL"
            
            elif field.field_type == FieldType.NUMBER:
                try:
                    float(value)
                    return True, None
                except (ValueError, TypeError):
                    return False, "Please enter a valid number"
            
            elif field.field_type == FieldType.DATE:
                return self._validate_date(str(value)), "Please enter a valid date"
            
            elif field.field_type == FieldType.SELECT:
                if field.options and str(value) not in field.options:
                    return False, f"Please select one of: {', '.join(field.options)}"
            
            # Length validation
            if isinstance(value, str):
                if field.max_length and len(value) > field.max_length:
                    return False, f"Maximum length is {field.max_length} characters"
                
                if field.min_length and len(value) < field.min_length:
                    return False, f"Minimum length is {field.min_length} characters"
            
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    # Application Validation
    
    def validate_application(self, application: Application) -> Tuple[bool, List[ValidationError]]:
        """Validate a complete application"""
        errors = []
        
        # Check required fields are filled
        required_fields = application.get_required_fields()
        for field in required_fields:
            if field.value is None or field.value == "":
                errors.append(ValidationError(
                    field.field_id, 
                    f"Required field '{field.label}' is not filled"
                ))
        
        # Validate each field value
        for section in application.sections:
            for field in section.fields:
                if field.value is not None and field.value != "":
                    is_valid, error_msg = self.validate_form_field(field, field.value)
                    if not is_valid:
                        errors.append(ValidationError(field.field_id, error_msg))
        
        return len(errors) == 0, errors
    
    # Helper Methods
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        email_rules = self.validation_rules.get("field_validation_rules", {}).get("email", {})
        pattern = email_rules.get("pattern", r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        return re.match(pattern, email) is not None
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        phone_rules = self.validation_rules.get("field_validation_rules", {}).get("phone", {})
        pattern = phone_rules.get("pattern", r"^[\d\s\-\(\)\.]{10,}$")
        return re.match(pattern, phone) is not None
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format"""
        url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
        return re.match(url_pattern, url, re.IGNORECASE) is not None
    
    def _validate_date(self, date_str: str) -> bool:
        """Validate date format"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            try:
                datetime.strptime(date_str, "%m/%d/%Y")
                return True
            except ValueError:
                return False
    
    def _validate_postal_code(self, postal_code: str, country: str) -> bool:
        """Validate postal code based on country"""
        if country.lower() in ["united states", "usa", "us"]:
            # US ZIP code validation
            return re.match(r"^\d{5}(-\d{4})?$", postal_code) is not None
        elif country.lower() in ["canada", "ca"]:
            # Canadian postal code validation
            return re.match(r"^[A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d$", postal_code) is not None
        else:
            # Basic validation for other countries
            return len(postal_code.strip()) >= 3
    
    # Data Quality Checks
    
    def check_profile_completeness(self, profile: UserProfile) -> Dict[str, Any]:
        """Check profile completeness and provide recommendations"""
        total_sections = 8
        completed_sections = 0
        
        # Check each section
        sections_status = {}
        
        # Personal information
        if profile.personal.first_name and profile.personal.last_name:
            completed_sections += 1
            sections_status["personal"] = {"complete": True, "score": 100}
        else:
            sections_status["personal"] = {"complete": False, "score": 50}
        
        # Contact information
        if profile.contact.email and profile.contact.phone:
            completed_sections += 1
            sections_status["contact"] = {"complete": True, "score": 100}
        else:
            sections_status["contact"] = {"complete": False, "score": 50}
        
        # Experience
        if profile.experience:
            completed_sections += 1
            sections_status["experience"] = {"complete": True, "score": 100}
        else:
            sections_status["experience"] = {"complete": False, "score": 0}
        
        # Education
        if profile.education:
            completed_sections += 1
            sections_status["education"] = {"complete": True, "score": 100}
        else:
            sections_status["education"] = {"complete": False, "score": 0}
        
        # Technical skills
        if profile.technical_skills:
            completed_sections += 1
            sections_status["technical_skills"] = {"complete": True, "score": 100}
        else:
            sections_status["technical_skills"] = {"complete": False, "score": 0}
        
        # Job preferences
        if profile.job_preferences.desired_roles:
            completed_sections += 1
            sections_status["job_preferences"] = {"complete": True, "score": 100}
        else:
            sections_status["job_preferences"] = {"complete": False, "score": 0}
        
        # Compensation
        if profile.compensation.desired_salary_min or profile.compensation.desired_salary_max:
            completed_sections += 1
            sections_status["compensation"] = {"complete": True, "score": 100}
        else:
            sections_status["compensation"] = {"complete": False, "score": 50}
        
        # Summary/Templates
        if profile.summary_statement or profile.cover_letter_templates:
            completed_sections += 1
            sections_status["content"] = {"complete": True, "score": 100}
        else:
            sections_status["content"] = {"complete": False, "score": 0}
        
        completeness_score = (completed_sections / total_sections) * 100
        
        return {
            "completeness_score": round(completeness_score, 1),
            "completed_sections": completed_sections,
            "total_sections": total_sections,
            "sections_status": sections_status,
            "recommendations": self._generate_completeness_recommendations(sections_status)
        }
    
    def _generate_completeness_recommendations(self, sections_status: Dict) -> List[str]:
        """Generate recommendations to improve profile completeness"""
        recommendations = []
        
        if not sections_status.get("experience", {}).get("complete", False):
            recommendations.append("Add work experience to improve job matching")
        
        if not sections_status.get("technical_skills", {}).get("complete", False):
            recommendations.append("Add technical skills for better field matching")
        
        if not sections_status.get("education", {}).get("complete", False):
            recommendations.append("Add education information to meet application requirements")
        
        if not sections_status.get("job_preferences", {}).get("complete", False):
            recommendations.append("Set job preferences to target relevant opportunities")
        
        if not sections_status.get("content", {}).get("complete", False):
            recommendations.append("Add professional summary or cover letter templates")
        
        return recommendations