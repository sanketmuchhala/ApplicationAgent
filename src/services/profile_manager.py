import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from models.profile import UserProfile
from utils.storage import StorageManager


class ProfileManager:
    """Manages user profiles with CRUD operations"""
    
    def __init__(self, storage_manager: StorageManager):
        self.storage = storage_manager
    
    async def create_profile(self, profile: UserProfile) -> UserProfile:
        """Create a new user profile"""
        # Generate unique ID if not provided
        if not profile.profile_id:
            profile.profile_id = f"profile_{uuid.uuid4().hex[:8]}"
        
        # Set timestamps
        profile.created_at = datetime.now()
        profile.updated_at = datetime.now()
        
        # Save to storage
        success = await self.storage.save_profile(profile.profile_id, profile.dict())
        
        if not success:
            raise Exception(f"Failed to save profile {profile.profile_id}")
        
        return profile
    
    async def get_profile(self, profile_id: str) -> Optional[UserProfile]:
        """Get a user profile by ID"""
        profile_data = await self.storage.load_profile(profile_id)
        
        if not profile_data:
            return None
        
        try:
            return UserProfile.parse_obj(profile_data)
        except Exception as e:
            print(f"Error parsing profile {profile_id}: {str(e)}")
            return None
    
    async def update_profile(self, profile_id: str, updates: Dict[str, Any]) -> Optional[UserProfile]:
        """Update an existing profile"""
        # Load existing profile
        existing_profile = await self.get_profile(profile_id)
        if not existing_profile:
            return None
        
        # Apply updates
        profile_dict = existing_profile.dict()
        profile_dict.update(updates)
        profile_dict["updated_at"] = datetime.now()
        
        try:
            updated_profile = UserProfile.parse_obj(profile_dict)
        except Exception as e:
            raise ValueError(f"Invalid profile updates: {str(e)}")
        
        # Save updated profile
        success = await self.storage.save_profile(profile_id, updated_profile.dict())
        
        if not success:
            raise Exception(f"Failed to update profile {profile_id}")
        
        return updated_profile
    
    async def list_profiles(self) -> List[Dict[str, Any]]:
        """List all profiles with summary information"""
        return await self.storage.list_profiles()
    
    async def delete_profile(self, profile_id: str) -> bool:
        """Delete a user profile"""
        # TODO: Also delete related applications
        return await self.storage.delete_profile(profile_id)
    
    async def search_profiles(self, query: str) -> List[Dict[str, Any]]:
        """Search profiles by name, email, or other fields"""
        all_profiles = await self.list_profiles()
        
        query_lower = query.lower()
        matching_profiles = []
        
        for profile_info in all_profiles:
            # Search in name, email, and other searchable fields
            searchable_text = " ".join([
                profile_info.get("name", ""),
                profile_info.get("email", ""),
                str(profile_info.get("profile_id", ""))
            ]).lower()
            
            if query_lower in searchable_text:
                matching_profiles.append(profile_info)
        
        return matching_profiles
    
    async def get_profile_summary(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of profile information"""
        profile = await self.get_profile(profile_id)
        
        if not profile:
            return None
        
        return {
            "profile_id": profile.profile_id,
            "name": profile.personal.full_name,
            "email": str(profile.contact.email),
            "phone": profile.contact.phone,
            "location": f"{profile.personal.city}, {profile.personal.state}" if profile.personal.city else None,
            "total_experience_years": profile.total_experience_years,
            "current_position": profile.current_position.position if profile.current_position else None,
            "current_company": profile.current_position.company if profile.current_position else None,
            "latest_education": {
                "degree": profile.latest_education.degree,
                "field": profile.latest_education.field_of_study,
                "institution": profile.latest_education.institution
            } if profile.latest_education else None,
            "top_skills": profile.technical_skills[:5],  # Top 5 skills
            "work_authorization": profile.personal.work_authorization.value,
            "remote_preference": profile.job_preferences.remote_preference.value,
            "salary_range": {
                "min": profile.compensation.desired_salary_min,
                "max": profile.compensation.desired_salary_max
            } if profile.compensation.desired_salary_min else None,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at
        }
    
    async def validate_profile(self, profile: UserProfile) -> List[str]:
        """Validate profile completeness and return list of issues"""
        issues = []
        
        # Required personal information
        if not profile.personal.first_name:
            issues.append("First name is required")
        if not profile.personal.last_name:
            issues.append("Last name is required")
        
        # Required contact information
        if not profile.contact.email:
            issues.append("Email is required")
        if not profile.contact.phone:
            issues.append("Phone number is required")
        
        # Work authorization
        if not profile.personal.work_authorization:
            issues.append("Work authorization status is required")
        
        # Experience validation
        if not profile.experience:
            issues.append("At least one work experience entry is recommended")
        else:
            for i, exp in enumerate(profile.experience):
                if not exp.company:
                    issues.append(f"Company name is required for experience entry {i+1}")
                if not exp.position:
                    issues.append(f"Position is required for experience entry {i+1}")
                if not exp.description:
                    issues.append(f"Job description is recommended for experience entry {i+1}")
        
        # Education validation
        if not profile.education:
            issues.append("At least one education entry is recommended")
        
        # Skills validation
        if not profile.technical_skills:
            issues.append("Technical skills are recommended")
        
        return issues
    
    async def get_profile_completeness(self, profile_id: str) -> Dict[str, Any]:
        """Get profile completeness score and recommendations"""
        profile = await self.get_profile(profile_id)
        
        if not profile:
            return {"error": "Profile not found"}
        
        issues = await self.validate_profile(profile)
        
        # Calculate completeness score
        total_sections = 8  # personal, contact, experience, education, skills, preferences, compensation, etc.
        completed_sections = 0
        
        if profile.personal.first_name and profile.personal.last_name:
            completed_sections += 1
        if profile.contact.email and profile.contact.phone:
            completed_sections += 1
        if profile.experience:
            completed_sections += 1
        if profile.education:
            completed_sections += 1
        if profile.technical_skills:
            completed_sections += 1
        if profile.job_preferences.desired_roles:
            completed_sections += 1
        if profile.compensation.desired_salary_min or profile.compensation.desired_salary_max:
            completed_sections += 1
        if profile.summary_statement or profile.cover_letter_templates:
            completed_sections += 1
        
        completeness_score = (completed_sections / total_sections) * 100
        
        # Generate recommendations
        recommendations = []
        if completeness_score < 50:
            recommendations.append("Complete basic personal and contact information")
        if not profile.experience:
            recommendations.append("Add work experience to improve job matching")
        if not profile.technical_skills:
            recommendations.append("Add technical skills for better field matching")
        if not profile.summary_statement:
            recommendations.append("Add a professional summary for better applications")
        
        return {
            "profile_id": profile_id,
            "completeness_score": round(completeness_score, 1),
            "completed_sections": completed_sections,
            "total_sections": total_sections,
            "issues": issues,
            "recommendations": recommendations
        }