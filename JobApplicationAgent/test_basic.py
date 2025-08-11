#!/usr/bin/env python3
"""
Basic test script to verify the Job Application Agent system works
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models.profile import UserProfile, PersonalInfo, ContactInfo
from src.services.form_analyzer import FormAnalyzer
from src.services.semantic_matcher import SemanticMatcher
from src.services.validator import Validator
from src.utils.storage import StorageManager
from src.utils.paths import PathManager
from src.utils.text_similarity import TextSimilarity


async def test_basic_functionality():
    """Test basic functionality without AI"""
    print("🧪 Testing Basic Job Application Agent Functionality")
    print("=" * 60)
    
    # Test 1: Path Manager
    print("\n1. Testing Path Manager...")
    path_manager = PathManager()
    path_manager.ensure_directories_exist()
    print(f"   ✅ Data directory: {path_manager.get_data_dir()}")
    print(f"   ✅ Config directory: {path_manager.get_config_dir()}")
    
    # Test 2: Storage Manager
    print("\n2. Testing Storage Manager...")
    storage = StorageManager(path_manager.get_data_dir())
    await storage.initialize()
    
    # Test save/load
    test_data = {"test": "data", "timestamp": "2024-01-01"}
    saved = await storage.save_json("test", "test_item", test_data)
    loaded = await storage.load_json("test", "test_item")
    
    assert saved == True, "Save failed"
    assert loaded["test"] == "data", "Load failed"
    print("   ✅ Storage save/load working")
    
    # Test 3: Profile Model
    print("\n3. Testing Profile Model...")
    try:
        profile = UserProfile(
            profile_id="test_profile",
            personal=PersonalInfo(
                first_name="John",
                last_name="Doe",
                work_authorization="citizen"
            ),
            contact=ContactInfo(
                email="john.doe@example.com",
                phone="555-123-4567"
            )
        )
        
        # Test profile properties
        assert profile.personal.full_name == "John Doe", "Full name property failed"
        print(f"   ✅ Profile created: {profile.personal.full_name}")
        
    except Exception as e:
        print(f"   ❌ Profile model error: {str(e)}")
        return False
    
    # Test 4: Validator
    print("\n4. Testing Validator...")
    validator = Validator()
    
    is_valid, errors = validator.validate_profile(profile)
    if not is_valid:
        print(f"   ⚠️ Profile validation found issues: {len(errors)} errors")
        for error in errors[:3]:  # Show first 3 errors
            print(f"      - {error.field}: {error.message}")
    else:
        print("   ✅ Profile validation passed")
    
    # Test completeness check
    completeness = validator.check_profile_completeness(profile)
    print(f"   📊 Profile completeness: {completeness['completeness_score']:.1f}%")
    
    # Test 5: Text Similarity
    print("\n5. Testing Text Similarity...")
    text_sim = TextSimilarity()
    
    # Test field matching
    field_type, score = text_sim.semantic_field_match("first name")
    print(f"   🔍 'first name' matched to: {field_type} (score: {score})")
    if field_type != "first_name":
        print(f"   ❌ Expected 'first_name' but got '{field_type}' with score {score}")
        print("   🔍 Available field types:", list(text_sim.field_patterns.keys()))
    assert field_type == "first_name", f"Field matching failed: expected 'first_name' but got '{field_type}' with score {score}"
    
    # Test email validation
    assert text_sim.calculate_text_similarity("email address", "email") > 70, "Text similarity failed"
    print("   ✅ Text similarity working")
    
    # Test 6: Form Analyzer (basic HTML parsing)
    print("\n6. Testing Form Analyzer (Basic Mode)...")
    form_analyzer = FormAnalyzer(ai_service=None)
    
    # Simple test HTML
    test_html = """
    <form>
        <label for="first_name">First Name</label>
        <input type="text" id="first_name" name="first_name" required>
        
        <label for="email">Email Address</label>
        <input type="email" id="email" name="email" required>
        
        <label for="phone">Phone Number</label>
        <input type="tel" id="phone" name="phone">
    </form>
    """
    
    try:
        result = await form_analyzer.analyze_form(test_html)
        
        if result.success:
            fields = result.data.get('fields', [])
            print(f"   ✅ Form analysis found {len(fields)} fields")
            
            # Check if we found the expected fields
            field_names = [f.get('field_name') for f in fields]
            expected_fields = ['first_name', 'email', 'phone']
            
            found_fields = [f for f in expected_fields if f in field_names]
            print(f"   📝 Found expected fields: {found_fields}")
            
        else:
            print(f"   ❌ Form analysis failed: {result.error_message}")
            
    except Exception as e:
        print(f"   ❌ Form analyzer error: {str(e)}")
    
    # Test 7: Semantic Matcher (fallback mode)
    print("\n7. Testing Semantic Matcher (Fallback Mode)...")
    matcher = SemanticMatcher(ai_service=None)
    
    # Create mock form fields
    from src.models.form import FormField, FieldType
    
    mock_fields = [
        FormField(
            field_id="fname",
            field_name="first_name",
            label="First Name",
            field_type=FieldType.TEXT,
            required=True
        ),
        FormField(
            field_id="email_addr",
            field_name="email",
            label="Email Address", 
            field_type=FieldType.EMAIL,
            required=True
        )
    ]
    
    try:
        mappings = await matcher.match_fields_to_profile(mock_fields, profile)
        print(f"   ✅ Field matching found {len(mappings)} mappings")
        
        for mapping in mappings:
            print(f"      - {mapping.field_id} → {mapping.profile_path} (confidence: {mapping.confidence_score})")
            
    except Exception as e:
        print(f"   ❌ Semantic matcher error: {str(e)}")
    
    # Test 8: Storage Statistics
    print("\n8. Testing Storage Statistics...")
    stats = await storage.get_storage_stats()
    print(f"   📊 Storage stats: {stats}")
    
    print("\n" + "=" * 60)
    print("✅ Basic functionality tests completed!")
    return True


async def test_with_sample_data():
    """Test with sample profile and form data"""
    print("\n🧪 Testing with Sample Data")
    print("=" * 60)
    
    # Load sample profile
    sample_profile_path = Path(__file__).parent / "data" / "profiles" / "sample_profile.json"
    
    if sample_profile_path.exists():
        print("\n1. Loading sample profile...")
        with open(sample_profile_path, 'r') as f:
            profile_data = json.load(f)
        
        try:
            profile = UserProfile.parse_obj(profile_data)
            print(f"   ✅ Loaded profile: {profile.personal.full_name}")
            print(f"   📊 Experience: {profile.total_experience_years} years")
            print(f"   💼 Current role: {profile.current_position.position if profile.current_position else 'None'}")
            
        except Exception as e:
            print(f"   ❌ Error parsing sample profile: {str(e)}")
            return False
    else:
        print("   ⚠️ Sample profile not found")
        return False
    
    # Load sample form
    sample_form_path = Path(__file__).parent / "data" / "sample_forms" / "sample_job_form.html"
    
    if sample_form_path.exists():
        print("\n2. Analyzing sample form...")
        with open(sample_form_path, 'r') as f:
            html_content = f.read()
        
        form_analyzer = FormAnalyzer(ai_service=None)
        
        try:
            result = await form_analyzer.analyze_form(html_content)
            
            if result.success:
                analysis = result.data
                metadata = analysis.get('form_metadata', {})
                fields = analysis.get('fields', [])
                
                print(f"   ✅ Form title: {metadata.get('title', 'Unknown')}")
                print(f"   📝 Total fields: {metadata.get('total_fields', 0)}")
                print(f"   ⚠️ Required fields: {metadata.get('required_fields', 0)}")
                print(f"   🔥 Complexity: {metadata.get('complexity_score', 0):.1f}/10")
                
                # Show some field examples
                print("\n   Sample fields:")
                for field in fields[:5]:  # First 5 fields
                    required_indicator = "*" if field.get('required') else ""
                    print(f"      - {field.get('label', 'No label')}{required_indicator} ({field.get('field_type', 'unknown')})")
                
            else:
                print(f"   ❌ Form analysis failed")
                
        except Exception as e:
            print(f"   ❌ Error analyzing form: {str(e)}")
    
    else:
        print("   ⚠️ Sample form not found")
    
    print("\n" + "=" * 60)
    print("✅ Sample data tests completed!")
    return True


def check_ai_availability():
    """Check if AI service can be initialized"""
    print("\n🤖 Checking AI Service Availability")
    print("=" * 60)
    
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key:
        print("   ⚠️ DEEPSEEK_API_KEY not found in environment")
        print("   💡 To enable AI features:")
        print("      1. Get API key from https://deepseek.com")
        print("      2. Set environment variable: export DEEPSEEK_API_KEY=your_key")
        print("      3. Or create .env file with DEEPSEEK_API_KEY=your_key")
        return False
    else:
        print(f"   ✅ DeepSeek API key found: {api_key[:8]}...{api_key[-4:]}")
        return True


async def main():
    """Main test function"""
    print("🚀 Job Application Agent - System Test")
    print("=" * 60)
    print("Testing core functionality without external dependencies...")
    
    try:
        # Run basic tests
        basic_success = await test_basic_functionality()
        
        if basic_success:
            # Run sample data tests
            sample_success = await test_with_sample_data()
            
            # Check AI availability
            ai_available = check_ai_availability()
            
            print("\n" + "=" * 60)
            print("📋 Test Summary:")
            print(f"   Basic functionality: {'✅ PASS' if basic_success else '❌ FAIL'}")
            print(f"   Sample data tests: {'✅ PASS' if sample_success else '❌ FAIL'}")
            print(f"   AI service ready: {'✅ YES' if ai_available else '⚠️ NO (optional)'}")
            
            if basic_success and sample_success:
                print("\n🎉 System is ready to use!")
                print("\nNext steps:")
                print("   1. Set up DeepSeek API key for AI features")
                print("   2. Run: python src/cli.py setup")
                print("   3. Create profile: python src/cli.py create-profile")
                print("   4. Test with Claude Desktop integration")
                return True
            else:
                print("\n❌ Some tests failed. Please check the errors above.")
                return False
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)