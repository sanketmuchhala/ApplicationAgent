#!/usr/bin/env python3
"""
Command Line Interface for Job Application Agent
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich import print as rprint

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from services.deepseek_service import DeepSeekService
from services.form_analyzer import FormAnalyzer
from services.semantic_matcher import SemanticMatcher
from services.response_generator import ResponseGenerator
from models.profile import UserProfile, PersonalInfo, ContactInfo
from models.ai_config import AIProviderConfig, AIProviderType
from utils.storage import StorageManager
from utils.paths import PathManager

console = Console()


class JobApplicationCLI:
    """Command Line Interface for Job Application Agent"""
    
    def __init__(self):
        self.path_manager = PathManager()
        self.storage_manager = None
        self.ai_service = None
        self.form_analyzer = None
        self.semantic_matcher = None
        self.response_generator = None
    
    async def initialize(self):
        """Initialize CLI services"""
        # Initialize storage
        self.storage_manager = StorageManager(self.path_manager.get_data_dir())
        await self.storage_manager.initialize()
        
        # Initialize AI service if API key is available
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if api_key:
            config = {
                'api_key': api_key,
                'api_base': os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1'),
                'model': os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
                'max_tokens': 4000,
                'temperature': 0.1,
                'cost_per_1k_input': 0.00014,
                'cost_per_1k_output': 0.00028
            }
            
            self.ai_service = DeepSeekService(config)
            self.form_analyzer = FormAnalyzer(self.ai_service)
            self.semantic_matcher = SemanticMatcher(self.ai_service)
            self.response_generator = ResponseGenerator(self.ai_service)
            
            # Test connection
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Testing AI connection...", total=None)
                
                try:
                    connected = await self.ai_service.test_connection()
                    if connected:
                        console.print("✅ AI service connected successfully", style="green")
                    else:
                        console.print("❌ AI service connection failed", style="red")
                        self.ai_service = None
                except Exception as e:
                    console.print(f"❌ AI service error: {str(e)}", style="red")
                    self.ai_service = None
        
        else:
            console.print("⚠️ No DEEPSEEK_API_KEY found - AI features disabled", style="yellow")


@click.group()
@click.pass_context
async def cli(ctx):
    """Job Application Agent CLI - AI-powered job application automation"""
    if ctx.obj is None:
        ctx.obj = JobApplicationCLI()
        await ctx.obj.initialize()


@cli.command()
@click.pass_context
async def setup(ctx):
    """Initial setup and configuration"""
    cli_obj = ctx.obj
    
    console.print(Panel.fit("🚀 Job Application Agent Setup", style="bold blue"))
    
    # Check if API key is configured
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        console.print("⚠️ DeepSeek API key not found", style="yellow")
        
        if Confirm.ask("Would you like to configure DeepSeek API key now?"):
            api_key = Prompt.ask("Enter your DeepSeek API key", password=True)
            
            env_file = cli_obj.path_manager.get_base_dir() / ".env"
            
            # Create or update .env file
            env_content = f"DEEPSEEK_API_KEY={api_key}\n"
            if env_file.exists():
                with open(env_file, 'a') as f:
                    f.write(env_content)
            else:
                with open(env_file, 'w') as f:
                    f.write(env_content)
            
            console.print("✅ API key saved to .env file", style="green")
            console.print("Please restart the CLI to use AI features", style="blue")
    
    # Create directories
    cli_obj.path_manager.ensure_directories_exist()
    console.print("✅ Created necessary directories", style="green")
    
    # Show setup summary
    table = Table(title="Setup Summary")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="magenta")
    
    table.add_row("Data Directory", str(cli_obj.path_manager.get_data_dir()))
    table.add_row("Config Directory", str(cli_obj.path_manager.get_config_dir()))
    table.add_row("AI Service", "✅ Connected" if cli_obj.ai_service else "❌ Not configured")
    
    console.print(table)


@cli.command()
@click.option('--html-file', type=click.Path(exists=True), help='Path to HTML file to analyze')
@click.option('--url', help='URL of job application form')
@click.pass_context
async def analyze_form(ctx, html_file: Optional[str], url: Optional[str]):
    """Analyze a job application form"""
    cli_obj = ctx.obj
    
    if not html_file and not url:
        console.print("❌ Please provide either --html-file or --url", style="red")
        return
    
    if not cli_obj.form_analyzer:
        console.print("❌ Form analyzer not available (AI service not configured)", style="red")
        return
    
    # Read HTML content
    if html_file:
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        console.print(f"📄 Analyzing form from file: {html_file}")
    else:
        # TODO: Implement URL fetching
        console.print("❌ URL fetching not yet implemented", style="red")
        return
    
    # Analyze the form
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing form with AI...", total=None)
        
        try:
            result = await cli_obj.form_analyzer.analyze_form(html_content)
            
            if result.success:
                console.print("✅ Form analysis completed", style="green")
                
                # Display results
                analysis_data = result.data
                
                # Form metadata
                metadata = analysis_data.get('form_metadata', {})
                console.print(Panel(
                    f"**Title:** {metadata.get('title', 'Unknown')}\n"
                    f"**Total Fields:** {metadata.get('total_fields', 0)}\n"
                    f"**Required Fields:** {metadata.get('required_fields', 0)}\n"
                    f"**Complexity Score:** {metadata.get('complexity_score', 0):.1f}/10",
                    title="Form Summary"
                ))
                
                # Fields table
                fields = analysis_data.get('fields', [])
                if fields:
                    table = Table(title="Form Fields")
                    table.add_column("Field ID", style="cyan")
                    table.add_column("Label", style="white")
                    table.add_column("Type", style="yellow")
                    table.add_column("Required", style="red")
                    
                    for field in fields[:10]:  # Show first 10 fields
                        table.add_row(
                            field.get('field_id', ''),
                            field.get('label', ''),
                            field.get('field_type', ''),
                            "✅" if field.get('required') else "❌"
                        )
                    
                    console.print(table)
                    
                    if len(fields) > 10:
                        console.print(f"... and {len(fields) - 10} more fields")
                
                # Save analysis results
                form_id = f"form_{hash(html_content) % 10000}"
                saved = await cli_obj.storage_manager.save_form(form_id, analysis_data)
                if saved:
                    console.print(f"💾 Analysis saved with ID: {form_id}", style="green")
                
            else:
                console.print(f"❌ Form analysis failed: {result.error_message}", style="red")
                
        except Exception as e:
            console.print(f"❌ Error during form analysis: {str(e)}", style="red")


@cli.command()
@click.pass_context
async def create_profile(ctx):
    """Create a new user profile interactively"""
    cli_obj = ctx.obj
    
    console.print(Panel.fit("👤 Create User Profile", style="bold green"))
    
    # Collect personal information
    console.print("Personal Information:", style="bold")
    first_name = Prompt.ask("First name")
    last_name = Prompt.ask("Last name")
    email = Prompt.ask("Email address")
    phone = Prompt.ask("Phone number")
    
    # Optional information
    city = Prompt.ask("City", default="")
    state = Prompt.ask("State/Province", default="")
    
    # Work authorization
    work_auth_options = ["citizen", "permanent_resident", "work_visa", "needs_sponsorship"]
    work_auth = click.prompt(
        "Work authorization",
        type=click.Choice(work_auth_options),
        default="citizen"
    )
    
    # Skills
    console.print("\nTechnical Skills (comma-separated):", style="bold")
    skills_input = Prompt.ask("Enter your technical skills", default="")
    technical_skills = [skill.strip() for skill in skills_input.split(',') if skill.strip()]
    
    # Create profile object
    try:
        profile = UserProfile(
            profile_id=f"profile_{hash(email) % 10000}",
            personal=PersonalInfo(
                first_name=first_name,
                last_name=last_name,
                city=city,
                state=state,
                work_authorization=work_auth
            ),
            contact=ContactInfo(
                email=email,
                phone=phone
            ),
            technical_skills=technical_skills
        )
        
        # Save profile
        saved = await cli_obj.storage_manager.save_profile(profile.profile_id, profile.dict())
        
        if saved:
            console.print(f"✅ Profile created with ID: {profile.profile_id}", style="green")
            
            # Display profile summary
            table = Table(title="Profile Summary")
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Name", profile.personal.full_name)
            table.add_row("Email", str(profile.contact.email))
            table.add_row("Phone", profile.contact.phone)
            table.add_row("Location", f"{city}, {state}" if city and state else "Not specified")
            table.add_row("Skills", ", ".join(technical_skills[:5]) if technical_skills else "None")
            
            console.print(table)
        else:
            console.print("❌ Failed to save profile", style="red")
            
    except Exception as e:
        console.print(f"❌ Error creating profile: {str(e)}", style="red")


@cli.command()
@click.pass_context
async def list_profiles(ctx):
    """List all user profiles"""
    cli_obj = ctx.obj
    
    try:
        profiles = await cli_obj.storage_manager.list_profiles()
        
        if not profiles:
            console.print("No profiles found. Use 'create-profile' to create one.", style="yellow")
            return
        
        table = Table(title="User Profiles")
        table.add_column("Profile ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Email", style="blue")
        table.add_column("Created", style="green")
        
        for profile in profiles:
            table.add_row(
                profile.get('profile_id', ''),
                profile.get('name', ''),
                profile.get('email', ''),
                profile.get('created_at', '')[:10] if profile.get('created_at') else ''
            )
        
        console.print(table)
        
    except Exception as e:
        console.print(f"❌ Error listing profiles: {str(e)}", style="red")


@cli.command()
@click.pass_context
async def test_ai(ctx):
    """Test AI service connection and capabilities"""
    cli_obj = ctx.obj
    
    if not cli_obj.ai_service:
        console.print("❌ AI service not configured", style="red")
        return
    
    console.print(Panel.fit("🤖 Testing AI Service", style="bold blue"))
    
    # Test connection
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Testing connection...", total=None)
        
        try:
            connected = await cli_obj.ai_service.test_connection()
            
            if connected:
                console.print("✅ Connection successful", style="green")
                
                # Get model info
                model_info = await cli_obj.ai_service.get_model_info()
                
                table = Table(title="AI Service Info")
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="white")
                
                for key, value in model_info.items():
                    table.add_row(str(key), str(value))
                
                console.print(table)
                
                # Get usage stats
                stats = cli_obj.ai_service.get_usage_stats("all")
                console.print(f"\n📊 Usage Stats: {stats['total_requests']} requests, ${stats['total_cost']:.4f} total cost")
                
            else:
                console.print("❌ Connection failed", style="red")
                
        except Exception as e:
            console.print(f"❌ Error testing AI service: {str(e)}", style="red")


@cli.command()
@click.pass_context
async def usage_stats(ctx):
    """Show AI usage statistics"""
    cli_obj = ctx.obj
    
    if not cli_obj.ai_service:
        console.print("❌ AI service not configured", style="red")
        return
    
    stats = cli_obj.ai_service.get_usage_stats("month")
    
    table = Table(title="AI Usage Statistics (This Month)")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Total Requests", str(stats['total_requests']))
    table.add_row("Success Rate", f"{stats['success_rate']:.1f}%")
    table.add_row("Total Cost", f"${stats['total_cost']:.4f}")
    table.add_row("Total Tokens", f"{stats['total_tokens']:,}")
    table.add_row("Avg Response Time", f"{stats['average_response_time_ms']:.0f}ms")
    
    console.print(table)
    
    # Show operations breakdown
    operations = stats.get('operations', {})
    if operations:
        op_table = Table(title="Operations Breakdown")
        op_table.add_column("Operation", style="cyan")
        op_table.add_column("Count", style="white")
        op_table.add_column("Cost", style="yellow")
        
        for op_name, op_data in operations.items():
            op_table.add_row(
                op_name,
                str(op_data['count']),
                f"${op_data['cost']:.4f}"
            )
        
        console.print(op_table)


def run_async_cli():
    """Run async CLI commands"""
    def async_command(f):
        def wrapper(*args, **kwargs):
            return asyncio.run(f(*args, **kwargs))
        return wrapper
    
    # Apply async wrapper to commands
    for name, command in cli.commands.items():
        cli.commands[name] = async_command(command)
    
    cli()


if __name__ == '__main__':
    # Set up asyncio event loop for CLI
    import asyncio
    
    async def run_cli():
        # Create CLI instance
        cli_obj = JobApplicationCLI()
        await cli_obj.initialize()
        
        # Check arguments to determine which command to run
        if len(sys.argv) < 2:
            console.print("Job Application Agent CLI", style="bold blue")
            console.print("Use --help to see available commands")
            return
        
        # For now, run setup by default
        if sys.argv[1] == "setup":
            await setup.callback(click.Context(setup), obj=cli_obj)
        elif sys.argv[1] == "test-ai":
            await test_ai.callback(click.Context(test_ai), obj=cli_obj)
        else:
            console.print("Available commands: setup, test-ai", style="yellow")
    
    asyncio.run(run_cli())