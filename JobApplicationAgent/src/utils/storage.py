import json
import os
import aiofiles
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


class StorageManager:
    """Manages local JSON file storage for profiles, applications, and other data"""
    
    def __init__(self, data_dir: Union[str, Path]):
        self.data_dir = Path(data_dir)
        self.profiles_dir = self.data_dir / "profiles"
        self.applications_dir = self.data_dir / "applications" 
        self.field_mappings_dir = self.data_dir / "field_mappings"
        self.forms_dir = self.data_dir / "forms"
    
    async def initialize(self):
        """Initialize storage directories"""
        directories = [
            self.data_dir,
            self.profiles_dir,
            self.applications_dir,
            self.field_mappings_dir,
            self.forms_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    # Profile Storage
    async def save_profile(self, profile_id: str, profile_data: Dict[str, Any]) -> bool:
        """Save user profile to JSON file"""
        try:
            file_path = self.profiles_dir / f"{profile_id}.json"
            profile_data["updated_at"] = datetime.now().isoformat()
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(profile_data, indent=2, default=str, ensure_ascii=False))
            
            return True
        except Exception as e:
            print(f"Error saving profile {profile_id}: {str(e)}")
            return False
    
    async def load_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Load user profile from JSON file"""
        try:
            file_path = self.profiles_dir / f"{profile_id}.json"
            if not file_path.exists():
                return None
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            print(f"Error loading profile {profile_id}: {str(e)}")
            return None
    
    async def list_profiles(self) -> List[Dict[str, Any]]:
        """List all profiles with basic information"""
        profiles = []
        
        try:
            for file_path in self.profiles_dir.glob("*.json"):
                try:
                    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                        content = await f.read()
                        profile_data = json.loads(content)
                        
                        # Extract basic info for listing
                        profile_info = {
                            "profile_id": profile_data.get("profile_id"),
                            "name": profile_data.get("personal", {}).get("full_name", "Unknown"),
                            "email": profile_data.get("contact", {}).get("email"),
                            "created_at": profile_data.get("created_at"),
                            "updated_at": profile_data.get("updated_at")
                        }
                        profiles.append(profile_info)
                        
                except Exception as e:
                    print(f"Error reading profile file {file_path}: {str(e)}")
                    continue
        except Exception as e:
            print(f"Error listing profiles: {str(e)}")
        
        return sorted(profiles, key=lambda x: x.get("updated_at", ""), reverse=True)
    
    async def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile"""
        try:
            file_path = self.profiles_dir / f"{profile_id}.json"
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting profile {profile_id}: {str(e)}")
            return False
    
    # Application Storage
    async def save_application(self, application_id: str, application_data: Dict[str, Any]) -> bool:
        """Save job application to JSON file"""
        try:
            file_path = self.applications_dir / f"{application_id}.json"
            application_data["updated_at"] = datetime.now().isoformat()
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(application_data, indent=2, default=str, ensure_ascii=False))
            
            return True
        except Exception as e:
            print(f"Error saving application {application_id}: {str(e)}")
            return False
    
    async def load_application(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Load job application from JSON file"""
        try:
            file_path = self.applications_dir / f"{application_id}.json"
            if not file_path.exists():
                return None
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            print(f"Error loading application {application_id}: {str(e)}")
            return None
    
    async def list_applications(self, profile_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List applications, optionally filtered by profile"""
        applications = []
        
        try:
            for file_path in self.applications_dir.glob("*.json"):
                try:
                    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                        content = await f.read()
                        app_data = json.loads(content)
                        
                        # Filter by profile if specified
                        if profile_id and app_data.get("profile_id") != profile_id:
                            continue
                        
                        # Extract basic info for listing
                        app_info = {
                            "application_id": app_data.get("application_id"),
                            "profile_id": app_data.get("profile_id"),
                            "company": app_data.get("job_details", {}).get("company_name"),
                            "position": app_data.get("job_details", {}).get("job_title"),
                            "status": app_data.get("status"),
                            "created_at": app_data.get("created_at"),
                            "updated_at": app_data.get("updated_at"),
                            "completion_percentage": app_data.get("completion_percentage", 0.0)
                        }
                        applications.append(app_info)
                        
                except Exception as e:
                    print(f"Error reading application file {file_path}: {str(e)}")
                    continue
        except Exception as e:
            print(f"Error listing applications: {str(e)}")
        
        return sorted(applications, key=lambda x: x.get("updated_at", ""), reverse=True)
    
    # Field Mappings Storage
    async def save_field_mappings(self, form_id: str, mappings: Dict[str, Any]) -> bool:
        """Save learned field mappings"""
        try:
            file_path = self.field_mappings_dir / f"{form_id}_mappings.json"
            mappings_data = {
                "form_id": form_id,
                "mappings": mappings,
                "created_at": datetime.now().isoformat(),
                "usage_count": 1
            }
            
            # Load existing if present to increment usage count
            if file_path.exists():
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.loads(await f.read())
                    mappings_data["usage_count"] = existing_data.get("usage_count", 0) + 1
                    mappings_data["created_at"] = existing_data.get("created_at")
            
            mappings_data["updated_at"] = datetime.now().isoformat()
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(mappings_data, indent=2, default=str, ensure_ascii=False))
            
            return True
        except Exception as e:
            print(f"Error saving field mappings for {form_id}: {str(e)}")
            return False
    
    async def load_field_mappings(self, form_id: str) -> Optional[Dict[str, Any]]:
        """Load learned field mappings"""
        try:
            file_path = self.field_mappings_dir / f"{form_id}_mappings.json"
            if not file_path.exists():
                return None
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            print(f"Error loading field mappings for {form_id}: {str(e)}")
            return None
    
    # Form Storage
    async def save_form(self, form_id: str, form_data: Dict[str, Any]) -> bool:
        """Save form structure and analysis"""
        try:
            file_path = self.forms_dir / f"{form_id}.json"
            form_data["updated_at"] = datetime.now().isoformat()
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(form_data, indent=2, default=str, ensure_ascii=False))
            
            return True
        except Exception as e:
            print(f"Error saving form {form_id}: {str(e)}")
            return False
    
    async def load_form(self, form_id: str) -> Optional[Dict[str, Any]]:
        """Load form structure and analysis"""
        try:
            file_path = self.forms_dir / f"{form_id}.json"
            if not file_path.exists():
                return None
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            print(f"Error loading form {form_id}: {str(e)}")
            return None
    
    # Generic Storage Methods
    async def save_json(self, category: str, item_id: str, data: Dict[str, Any]) -> bool:
        """Save JSON data to a specific category"""
        try:
            category_dir = self.data_dir / category
            category_dir.mkdir(exist_ok=True)
            
            file_path = category_dir / f"{item_id}.json"
            data["updated_at"] = datetime.now().isoformat()
            
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2, default=str, ensure_ascii=False))
            
            return True
        except Exception as e:
            print(f"Error saving {category}/{item_id}: {str(e)}")
            return False
    
    async def load_json(self, category: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Load JSON data from a specific category"""
        try:
            file_path = self.data_dir / category / f"{item_id}.json"
            if not file_path.exists():
                return None
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            print(f"Error loading {category}/{item_id}: {str(e)}")
            return None
    
    async def list_items(self, category: str) -> List[str]:
        """List all items in a category"""
        try:
            category_dir = self.data_dir / category
            if not category_dir.exists():
                return []
            
            items = []
            for file_path in category_dir.glob("*.json"):
                items.append(file_path.stem)  # filename without extension
            
            return sorted(items)
        except Exception as e:
            print(f"Error listing {category}: {str(e)}")
            return []
    
    # Backup and Export
    async def export_all_data(self) -> Dict[str, Any]:
        """Export all data for backup"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "profiles": [],
            "applications": [],
            "field_mappings": [],
            "forms": []
        }
        
        try:
            # Export profiles
            profile_files = list(self.profiles_dir.glob("*.json"))
            for file_path in profile_files:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    profile_data = json.loads(await f.read())
                    export_data["profiles"].append(profile_data)
            
            # Export applications
            app_files = list(self.applications_dir.glob("*.json"))
            for file_path in app_files:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    app_data = json.loads(await f.read())
                    export_data["applications"].append(app_data)
            
            # Export field mappings
            mapping_files = list(self.field_mappings_dir.glob("*.json"))
            for file_path in mapping_files:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    mapping_data = json.loads(await f.read())
                    export_data["field_mappings"].append(mapping_data)
            
            # Export forms
            form_files = list(self.forms_dir.glob("*.json"))
            for file_path in form_files:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                    form_data = json.loads(await f.read())
                    export_data["forms"].append(form_data)
            
        except Exception as e:
            print(f"Error during export: {str(e)}")
        
        return export_data
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        stats = {
            "profiles_count": 0,
            "applications_count": 0,
            "field_mappings_count": 0,
            "forms_count": 0,
            "total_size_bytes": 0
        }
        
        try:
            # Count files and calculate sizes
            for directory, stat_key in [
                (self.profiles_dir, "profiles_count"),
                (self.applications_dir, "applications_count"), 
                (self.field_mappings_dir, "field_mappings_count"),
                (self.forms_dir, "forms_count")
            ]:
                if directory.exists():
                    json_files = list(directory.glob("*.json"))
                    stats[stat_key] = len(json_files)
                    
                    # Calculate directory size
                    for file_path in json_files:
                        stats["total_size_bytes"] += file_path.stat().st_size
            
            # Convert to human readable size
            size_bytes = stats["total_size_bytes"]
            if size_bytes < 1024:
                stats["total_size_human"] = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                stats["total_size_human"] = f"{size_bytes / 1024:.1f} KB"
            else:
                stats["total_size_human"] = f"{size_bytes / (1024 * 1024):.1f} MB"
                
        except Exception as e:
            print(f"Error getting storage stats: {str(e)}")
        
        return stats