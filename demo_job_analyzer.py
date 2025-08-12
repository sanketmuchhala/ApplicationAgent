#!/usr/bin/env python3
"""
Demo Job Form Analyzer
Demonstrates the JobApplicationAgent's capabilities with sample job forms
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.deepseek_service import DeepSeekService
from src.services.form_analyzer import FormAnalyzer
from src.services.semantic_matcher import SemanticMatcher
from src.services.response_generator import ResponseGenerator
from src.utils.storage import StorageManager
from src.utils.paths import PathManager


async def load_sample_form(form_path: str) -> str:
    """Load a sample HTML form"""
    try:
        with open(form_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Sample form not found: {form_path}")
        return None


async def load_profile(profile_path: str) -> dict:
    """Load user profile"""
    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Profile not found: {profile_path}")
        return None


async def demo_form_analysis():
    """Demonstrate form analysis with sample forms"""
    
    print("🚀 JobApplicationAgent - Demo Form Analyzer")
    print("=" * 60)
    
    # Initialize path manager
    path_manager = PathManager()
    
    # Check for API key
    import os
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in environment variables")
        print("💡 Please set your API key in the .env file")
        return
    
    # Initialize AI service
    print("\n1. Initializing AI Service...")
    ai_config = {
        'api_key': api_key,
        'api_base': 'https://api.deepseek.com/v1',
        'model': 'deepseek-chat',
        'temperature': 0.1
    }
    
    ai_service = DeepSeekService(ai_config)
    
    # Test connection
    try:
        connected = await ai_service.test_connection()
        if not connected:
            print("❌ Failed to connect to DeepSeek API")
            return
        print("✅ DeepSeek AI connection successful")
    except Exception as e:
        print(f"❌ AI connection error: {str(e)}")
        return
    
    # Initialize services
    form_analyzer = FormAnalyzer(ai_service)
    semantic_matcher = SemanticMatcher(ai_service)
    response_generator = ResponseGenerator(ai_service)
    
    # Load user profile
    print("\n2. Loading User Profile...")
    profile_path = path_manager.get_data_dir() / "profiles" / "sanket_muchhala_profile.json"
    profile = await load_profile(str(profile_path))
    
    if not profile:
        print("❌ No user profile found. Please run setup_profile.py first")
        return
    
    print(f"✅ Loaded profile for: {profile.get('personal', {}).get('first_name', 'Unknown')} {profile.get('personal', {}).get('last_name', 'User')}")
    
    # Sample forms to analyze
    sample_forms = [
        {
            'name': 'Tech Company Form',
            'file': 'demo_samples/sample_job_form_tech.html',
            'company': 'TechCorp',
            'role': 'Senior AI/ML Engineer'
        },
        {
            'name': 'Startup Form',
            'file': 'demo_samples/sample_job_form_startup.html',
            'company': 'InnovateLabs',
            'role': 'AI Engineer'
        }
    ]
    
    # Analyze each form
    for i, form_info in enumerate(sample_forms, 1):
        print(f"\n{i + 2}. Analyzing {form_info['name']}...")
        
        # Load form HTML
        html_content = await load_sample_form(form_info['file'])
        if not html_content:
            continue
        
        # Job context
        job_context = {
            'company': form_info['company'],
            'role': form_info['role'],
            'description': f"AI/ML engineering position at {form_info['company']}"
        }
        
        try:
            # Step 1: Analyze form structure
            print(f"   📝 Analyzing form structure...")
            analysis_result = await form_analyzer.analyze_form(html_content, job_context)
            
            if not analysis_result.success:
                print(f"   ❌ Form analysis failed: {analysis_result.error}")
                continue
            
            form_data = analysis_result.data
            print(f"   ✅ Found {len(form_data.get('fields', []))} fields")
            
            # Show some key fields found
            key_fields = [f for f in form_data.get('fields', []) if f.get('importance') == 'high']
            if key_fields:
                print(f"   🔑 Key fields: {', '.join([f.get('name', 'Unknown') for f in key_fields[:5]])}")
            
            # Step 2: Match fields to profile
            print(f"   🎯 Matching fields to profile...")
            matching_result = await semantic_matcher.match_fields(form_data['fields'], profile)
            
            if not matching_result.success:
                print(f"   ❌ Field matching failed: {matching_result.error}")
                continue
            
            mappings = matching_result.data
            high_confidence_matches = [m for m in mappings if m.get('confidence', 0) > 0.8]
            print(f"   ✅ {len(high_confidence_matches)} high-confidence matches found")
            
            # Step 3: Generate responses for some fields
            print(f"   ✨ Generating sample responses...")
            
            # Select interesting fields for response generation
            text_fields = [
                m for m in mappings 
                if m.get('field_type') in ['textarea', 'text'] 
                and m.get('confidence', 0) > 0.6
                and 'why' in m.get('field_name', '').lower() or 'describe' in m.get('field_name', '').lower()
            ][:3]  # Limit to 3 for demo
            
            if text_fields:
                for field in text_fields:
                    field_name = field.get('field_name', 'Unknown')
                    field_label = field.get('field_label', field_name)
                    
                    try:
                        response_result = await response_generator.generate_response(
                            field_info=field,
                            profile_data=profile,
                            job_context=job_context
                        )
                        
                        if response_result.success:
                            response_text = response_result.data.get('response', '')
                            print(f"   📝 {field_label}: {response_text[:100]}...")
                        else:
                            print(f"   ⚠️ Could not generate response for {field_label}")
                            
                    except Exception as e:
                        print(f"   ⚠️ Response generation error for {field_label}: {str(e)}")
            
            # Step 4: Show cost information
            total_tokens = (analysis_result.tokens_used or 0) + (matching_result.tokens_used or 0)
            total_cost = (analysis_result.estimated_cost or 0) + (matching_result.estimated_cost or 0)
            
            print(f"   💰 Tokens used: {total_tokens}, Estimated cost: ${total_cost:.4f}")
            
        except Exception as e:
            print(f"   ❌ Error processing {form_info['name']}: {str(e)}")
            continue
    
    # Summary
    print(f"\n🎉 Demo Complete!")
    print(f"📊 Summary:")
    print(f"   • Analyzed {len(sample_forms)} sample job forms")
    print(f"   • Demonstrated AI-powered field analysis and matching")
    print(f"   • Generated contextual responses for form fields")
    print(f"   • Showed cost tracking and token usage")
    
    print(f"\n💡 Next Steps:")
    print(f"   • Try with real job forms by copying HTML content")
    print(f"   • Customize your profile for better matching")
    print(f"   • Use with Claude Desktop for interactive analysis")
    print(f"   • Run the MCP server: python run_server.py")


async def interactive_demo():
    """Interactive demo mode"""
    print("\n🎮 Interactive Demo Mode")
    print("Enter HTML content (paste and press Ctrl+D when done):")
    
    # Read HTML from user input
    html_lines = []
    try:
        while True:
            line = input()
            html_lines.append(line)
    except EOFError:
        pass
    
    html_content = '\n'.join(html_lines)
    
    if not html_content.strip():
        print("❌ No HTML content provided")
        return
    
    # Process the form
    print("🔄 Processing your form...")
    
    # Initialize services (similar to above)
    import os
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found")
        return
    
    ai_config = {
        'api_key': api_key,
        'api_base': 'https://api.deepseek.com/v1',
        'model': 'deepseek-chat',
        'temperature': 0.1
    }
    
    ai_service = DeepSeekService(ai_config)
    form_analyzer = FormAnalyzer(ai_service)
    
    try:
        result = await form_analyzer.analyze_form(html_content)
        if result.success:
            fields = result.data.get('fields', [])
            print(f"✅ Found {len(fields)} fields in your form")
            
            # Show field details
            for field in fields[:10]:  # Show first 10
                name = field.get('name', 'Unknown')
                field_type = field.get('type', 'unknown')
                label = field.get('label', 'No label')
                print(f"   • {name} ({field_type}): {label}")
        else:
            print(f"❌ Analysis failed: {result.error}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


async def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        await interactive_demo()
    else:
        await demo_form_analysis()


if __name__ == "__main__":
    asyncio.run(main())