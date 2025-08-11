import os
from pathlib import Path
from typing import Optional


class PathManager:
    """Manages cross-platform file paths for the application"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        if base_dir is None:
            # Default to current directory structure
            self.base_dir = Path(__file__).parent.parent.parent
        else:
            self.base_dir = Path(base_dir)
        
        self.data_dir = self.base_dir / "data"
        self.config_dir = self.base_dir / "config"
        self.logs_dir = self.base_dir / "logs"
    
    def get_base_dir(self) -> Path:
        """Get base application directory"""
        return self.base_dir
    
    def get_data_dir(self) -> Path:
        """Get data storage directory"""
        return self.data_dir
    
    def get_config_dir(self) -> Path:
        """Get configuration directory"""
        return self.config_dir
    
    def get_logs_dir(self) -> Path:
        """Get logs directory"""
        return self.logs_dir
    
    def get_profiles_dir(self) -> Path:
        """Get profiles storage directory"""
        return self.data_dir / "profiles"
    
    def get_applications_dir(self) -> Path:
        """Get applications storage directory"""
        return self.data_dir / "applications"
    
    def get_field_mappings_dir(self) -> Path:
        """Get field mappings storage directory"""
        return self.data_dir / "field_mappings"
    
    def get_sample_forms_dir(self) -> Path:
        """Get sample forms directory"""
        return self.data_dir / "sample_forms"
    
    def get_prompts_dir(self) -> Path:
        """Get AI prompts directory"""
        return self.config_dir / "prompts"
    
    def ensure_directories_exist(self):
        """Create all necessary directories"""
        directories = [
            self.data_dir,
            self.config_dir,
            self.logs_dir,
            self.get_profiles_dir(),
            self.get_applications_dir(),
            self.get_field_mappings_dir(),
            self.get_sample_forms_dir(),
            self.get_prompts_dir()
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_temp_dir(self) -> Path:
        """Get temporary directory for file processing"""
        temp_dir = self.base_dir / "temp"
        temp_dir.mkdir(exist_ok=True)
        return temp_dir
    
    def clean_temp_dir(self):
        """Clean temporary directory"""
        temp_dir = self.get_temp_dir()
        if temp_dir.exists():
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    file_path.unlink()
    
    def get_relative_path(self, absolute_path: Path) -> str:
        """Get relative path from base directory"""
        try:
            return str(absolute_path.relative_to(self.base_dir))
        except ValueError:
            return str(absolute_path)
    
    @staticmethod
    def expand_user_path(path: str) -> Path:
        """Expand user home directory in path"""
        return Path(os.path.expanduser(path))
    
    @staticmethod
    def normalize_path(path: str) -> Path:
        """Normalize path for current OS"""
        return Path(path).resolve()