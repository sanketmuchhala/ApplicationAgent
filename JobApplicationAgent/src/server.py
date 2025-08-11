#!/usr/bin/env python3
"""
AI Job Application Agent - MCP Server
Enhanced with DeepSeek API integration for intelligent semantic matching
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import mcp.server.stdio

from .models.ai_config import AIConfiguration, AIProviderConfig, AIProviderType
from .models.profile import UserProfile
from .models.application import Application, JobDetails
from .models.form import Form
from .services.ai_service import AIService
from .services.deepseek_service import DeepSeekService
from .services.local_service import LocalService
from .services.semantic_matcher import SemanticMatcher
from .services.form_analyzer import FormAnalyzer
from .services.response_generator import ResponseGenerator
from .services.profile_manager import ProfileManager
from .utils.storage import StorageManager
from .utils.paths import PathManager


class JobApplicationAgentServer:
    """Main MCP server for the Job Application Agent"""
    
    def __init__(self):
        self.server = Server("job-application-agent")
        self.config: Optional[AIConfiguration] = None
        self.ai_providers: Dict[str, AIService] = {}
        self.current_provider: Optional[AIService] = None
        
        # Service managers
        self.storage_manager: Optional[StorageManager] = None
        self.profile_manager: Optional[ProfileManager] = None
        self.semantic_matcher: Optional[SemanticMatcher] = None
        self.form_analyzer: Optional[FormAnalyzer] = None
        self.response_generator: Optional[ResponseGenerator] = None
        
        # Path manager
        self.path_manager = PathManager()
        
        # Register all tools
        self._register_tools()
    
    async def initialize(self):
        """Initialize the server and load configuration"""
        try:
            # Load AI configuration
            await self._load_ai_configuration()
            
            # Initialize storage
            self.storage_manager = StorageManager(self.path_manager.get_data_dir())
            await self.storage_manager.initialize()
            
            # Initialize AI providers
            await self._initialize_ai_providers()
            
            # Initialize service managers
            self.profile_manager = ProfileManager(self.storage_manager)
            self.semantic_matcher = SemanticMatcher(self.current_provider)
            self.form_analyzer = FormAnalyzer(self.current_provider)
            self.response_generator = ResponseGenerator(self.current_provider)
            
            print(f"🚀 Job Application Agent initialized with {self.current_provider.provider_name} AI provider")
            
        except Exception as e:
            print(f"❌ Failed to initialize server: {str(e)}")
            raise
    
    async def _load_ai_configuration(self):
        """Load AI provider configuration"""
        config_path = self.path_manager.get_config_dir() / "ai_providers.json"
        
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Load environment variables
            config_data = self._inject_env_vars(config_data)
            
            self.config = AIConfiguration.parse_obj(config_data)
            
        except FileNotFoundError:
            print("⚠️ AI configuration file not found, using defaults")
            self.config = self._create_default_config()
        except Exception as e:
            print(f"❌ Error loading AI configuration: {str(e)}")
            self.config = self._create_default_config()
    
    def _inject_env_vars(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Inject environment variables into configuration"""
        # DeepSeek configuration
        if 'deepseek' in config_data.get('providers', {}):
            deepseek_config = config_data['providers']['deepseek']
            deepseek_config['api_key'] = os.getenv('DEEPSEEK_API_KEY', deepseek_config.get('api_key'))
            deepseek_config['api_base'] = os.getenv('DEEPSEEK_API_BASE', deepseek_config.get('api_base'))
            deepseek_config['model'] = os.getenv('DEEPSEEK_MODEL', deepseek_config.get('model'))
        
        # Default provider
        config_data['default_provider'] = os.getenv('DEFAULT_AI_PROVIDER', config_data.get('default_provider'))
        
        # Budget settings
        if 'cost_tracking' in config_data:
            cost_config = config_data['cost_tracking']
            if os.getenv('MONTHLY_BUDGET_USD'):
                cost_config['monthly_budget'] = float(os.getenv('MONTHLY_BUDGET_USD'))
        
        return config_data
    
    def _create_default_config(self) -> AIConfiguration:
        """Create default AI configuration"""
        deepseek_config = AIProviderConfig(
            name="DeepSeek",
            provider_type=AIProviderType.DEEPSEEK,
            model="deepseek-chat",
            api_key=os.getenv('DEEPSEEK_API_KEY', ''),
            api_base=os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1'),
            cost_per_1k_input=0.00014,
            cost_per_1k_output=0.00028
        )
        
        local_config = AIProviderConfig(
            name="Local Model",
            provider_type=AIProviderType.LOCAL,
            model="local",
            enabled=False
        )
        
        basic_config = AIProviderConfig(
            name="Basic Matching",
            provider_type=AIProviderType.BASIC_MATCHING,
            model="basic",
            cost_per_1k_input=0.0,
            cost_per_1k_output=0.0
        )
        
        return AIConfiguration(
            providers={
                "deepseek": deepseek_config,
                "local": local_config,
                "basic_matching": basic_config
            },
            default_provider="deepseek",
            fallback_provider="basic_matching"
        )
    
    async def _initialize_ai_providers(self):
        """Initialize AI providers based on configuration"""
        for provider_name, provider_config in self.config.providers.items():
            if not provider_config.enabled:
                continue
            
            try:
                if provider_config.provider_type == AIProviderType.DEEPSEEK:
                    service = DeepSeekService(provider_config.dict())
                elif provider_config.provider_type == AIProviderType.LOCAL:
                    service = LocalService(provider_config.dict())
                else:
                    continue  # Skip unsupported providers for now
                
                # Test connection
                if await service.test_connection():
                    self.ai_providers[provider_name] = service
                    print(f"✅ {provider_name} provider initialized")
                else:
                    print(f"⚠️ {provider_name} provider connection failed")
                    
            except Exception as e:
                print(f"❌ Failed to initialize {provider_name} provider: {str(e)}")
        
        # Set current provider
        default_provider = self.config.default_provider
        if default_provider in self.ai_providers:
            self.current_provider = self.ai_providers[default_provider]
        elif self.ai_providers:
            # Use first available provider
            self.current_provider = list(self.ai_providers.values())[0]
        else:
            raise Exception("No AI providers available")
    
    def _register_tools(self):
        """Register all MCP tools"""
        
        # Profile Management Tools
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List all available tools"""
            return [
                # Profile Management
                Tool(
                    name="create_profile",
                    description="Create a new user profile with personal and professional information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "profile_data": {
                                "type": "object",
                                "description": "Complete profile information including personal, contact, experience, and preferences"
                            }
                        },
                        "required": ["profile_data"]
                    }
                ),
                Tool(
                    name="update_profile", 
                    description="Update an existing user profile",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "profile_id": {"type": "string", "description": "Profile ID to update"},
                            "updates": {"type": "object", "description": "Profile fields to update"}
                        },
                        "required": ["profile_id", "updates"]
                    }
                ),
                Tool(
                    name="get_profile",
                    description="Retrieve a user profile by ID",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "profile_id": {"type": "string", "description": "Profile ID to retrieve"}
                        },
                        "required": ["profile_id"]
                    }
                ),
                Tool(
                    name="list_profiles",
                    description="List all user profiles",
                    inputSchema={"type": "object", "properties": {}}
                ),
                
                # AI Provider Management
                Tool(
                    name="configure_ai_provider",
                    description="Configure AI provider settings",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "provider": {"type": "string", "description": "Provider name (deepseek, local)"},
                            "api_key": {"type": "string", "description": "API key for the provider"},
                            "settings": {"type": "object", "description": "Additional provider settings"}
                        },
                        "required": ["provider"]
                    }
                ),
                Tool(
                    name="switch_ai_provider",
                    description="Switch to a different AI provider",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "provider": {"type": "string", "description": "Provider name to switch to"}
                        },
                        "required": ["provider"]
                    }
                ),
                Tool(
                    name="get_ai_usage_stats",
                    description="Get AI usage statistics and costs",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "timeframe": {"type": "string", "enum": ["all", "today", "month"], "default": "month"}
                        }
                    }
                ),
                
                # Form Analysis Tools
                Tool(
                    name="analyze_form_with_ai",
                    description="Analyze job application form HTML with AI to extract fields and structure",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "html_content": {"type": "string", "description": "HTML content of the job application form"},
                            "job_context": {"type": "object", "description": "Optional job/company context information"}
                        },
                        "required": ["html_content"]
                    }
                ),
                Tool(
                    name="ai_match_fields",
                    description="Use AI to match form fields to user profile data",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "form_id": {"type": "string", "description": "Form ID to match fields for"},
                            "profile_id": {"type": "string", "description": "Profile ID to match against"},
                            "job_context": {"type": "object", "description": "Optional job context for better matching"}
                        },
                        "required": ["form_id", "profile_id"]
                    }
                ),
                Tool(
                    name="ai_generate_responses", 
                    description="Generate AI responses for form fields based on profile and job context",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "field_mappings": {"type": "object", "description": "Field to profile mappings"},
                            "profile_id": {"type": "string", "description": "User profile ID"},
                            "job_context": {"type": "object", "description": "Job and company context"}
                        },
                        "required": ["field_mappings", "profile_id"]
                    }
                ),
                
                # Application Management
                Tool(
                    name="create_application",
                    description="Create a new job application",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "profile_id": {"type": "string", "description": "Associated profile ID"},
                            "job_details": {"type": "object", "description": "Job and company information"},
                            "form_data": {"type": "object", "description": "Form structure data"}
                        },
                        "required": ["profile_id", "job_details"]
                    }
                ),
                Tool(
                    name="update_application_status",
                    description="Update application status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "application_id": {"type": "string", "description": "Application ID"},
                            "status": {"type": "string", "description": "New status"},
                            "note": {"type": "string", "description": "Optional status note"}
                        },
                        "required": ["application_id", "status"]
                    }
                ),
                Tool(
                    name="get_application",
                    description="Get application details",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "application_id": {"type": "string", "description": "Application ID to retrieve"}
                        },
                        "required": ["application_id"]
                    }
                ),
                
                # Utility Tools
                Tool(
                    name="test_ai_connection",
                    description="Test connection to current AI provider",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="export_data",
                    description="Export user data (profiles, applications, etc.)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "data_type": {"type": "string", "enum": ["profiles", "applications", "all"]},
                            "format": {"type": "string", "enum": ["json", "csv"], "default": "json"}
                        },
                        "required": ["data_type"]
                    }
                )
            ]
        
        # Tool implementations
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent | ImageContent | EmbeddedResource]:
            """Handle tool calls"""
            try:
                result = await self._execute_tool(name, arguments)
                return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
            except Exception as e:
                error_result = {"error": str(e), "tool": name}
                return [TextContent(type="text", text=json.dumps(error_result, indent=2))]
    
    async def _execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specified tool"""
        
        # Profile Management Tools
        if name == "create_profile":
            return await self._create_profile(arguments)
        elif name == "update_profile":
            return await self._update_profile(arguments)
        elif name == "get_profile":
            return await self._get_profile(arguments)
        elif name == "list_profiles":
            return await self._list_profiles()
        
        # AI Provider Tools
        elif name == "configure_ai_provider":
            return await self._configure_ai_provider(arguments)
        elif name == "switch_ai_provider":
            return await self._switch_ai_provider(arguments)
        elif name == "get_ai_usage_stats":
            return await self._get_ai_usage_stats(arguments)
        
        # Form Analysis Tools
        elif name == "analyze_form_with_ai":
            return await self._analyze_form_with_ai(arguments)
        elif name == "ai_match_fields":
            return await self._ai_match_fields(arguments)
        elif name == "ai_generate_responses":
            return await self._ai_generate_responses(arguments)
        
        # Application Management Tools
        elif name == "create_application":
            return await self._create_application(arguments)
        elif name == "update_application_status":
            return await self._update_application_status(arguments)
        elif name == "get_application":
            return await self._get_application(arguments)
        
        # Utility Tools
        elif name == "test_ai_connection":
            return await self._test_ai_connection()
        elif name == "export_data":
            return await self._export_data(arguments)
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    # Tool implementations
    async def _create_profile(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user profile"""
        profile_data = args["profile_data"]
        profile = UserProfile.parse_obj(profile_data)
        
        saved_profile = await self.profile_manager.create_profile(profile)
        
        return {
            "success": True,
            "profile_id": saved_profile.profile_id,
            "message": "Profile created successfully"
        }
    
    async def _get_ai_usage_stats(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI usage statistics"""
        timeframe = args.get("timeframe", "month")
        
        if not self.current_provider:
            return {"error": "No AI provider available"}
        
        stats = self.current_provider.get_usage_stats(timeframe)
        
        # Add budget information
        budget_info = None
        if self.config and self.config.cost_tracking.enabled:
            within_budget, current_cost, percentage = self.current_provider.is_within_budget(
                self.config.cost_tracking.monthly_budget
            )
            budget_info = {
                "monthly_budget": self.config.cost_tracking.monthly_budget,
                "current_cost": current_cost,
                "budget_used_percentage": percentage,
                "within_budget": within_budget
            }
        
        return {
            "usage_stats": stats,
            "budget_info": budget_info
        }
    
    async def _analyze_form_with_ai(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze form with AI"""
        html_content = args["html_content"]
        job_context = args.get("job_context")
        
        if not self.form_analyzer:
            return {"error": "Form analyzer not initialized"}
        
        result = await self.form_analyzer.analyze_form(html_content, job_context)
        
        return {
            "success": result.success,
            "analysis": result.data,
            "confidence": result.confidence_score,
            "processing_time_ms": result.processing_time_ms,
            "tokens_used": result.tokens_used,
            "estimated_cost": result.estimated_cost
        }
    
    async def _test_ai_connection(self) -> Dict[str, Any]:
        """Test AI provider connection"""
        if not self.current_provider:
            return {"error": "No AI provider configured"}
        
        try:
            connection_ok = await self.current_provider.test_connection()
            model_info = await self.current_provider.get_model_info()
            
            return {
                "connection_status": "connected" if connection_ok else "failed",
                "provider": self.current_provider.provider_name,
                "model_info": model_info
            }
        except Exception as e:
            return {
                "connection_status": "error",
                "error": str(e)
            }
    
    # Placeholder implementations for remaining tools
    async def _update_profile(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "message": "Profile update not yet implemented"}
    
    async def _get_profile(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "message": "Get profile not yet implemented"}
    
    async def _list_profiles(self) -> Dict[str, Any]:
        return {"success": True, "profiles": [], "message": "List profiles not yet implemented"}
    
    async def _configure_ai_provider(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "message": "Configure AI provider not yet implemented"}
    
    async def _switch_ai_provider(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "message": "Switch AI provider not yet implemented"}
    
    async def _ai_match_fields(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "message": "AI field matching not yet implemented"}
    
    async def _ai_generate_responses(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "message": "AI response generation not yet implemented"}
    
    async def _create_application(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "message": "Create application not yet implemented"}
    
    async def _update_application_status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "message": "Update application status not yet implemented"}
    
    async def _get_application(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "message": "Get application not yet implemented"}
    
    async def _export_data(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {"success": True, "message": "Export data not yet implemented"}


async def main():
    """Main entry point for the MCP server"""
    server_instance = JobApplicationAgentServer()
    
    try:
        await server_instance.initialize()
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server_instance.server.run(
                read_stream,
                write_stream,
                server_instance.server.create_initialization_options()
            )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"💥 Server error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())