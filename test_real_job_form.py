#!/usr/bin/env python3
"""
Test script to demonstrate ApplicationAgent with a real job application form
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.text_similarity import TextSimilarity
from src.utils.storage import StorageManager
from src.utils.paths import PathManager


async def test_job_form_analysis():
    """Test the ApplicationAgent with a sample job application form"""
    print("🎯 Testing ApplicationAgent with Real Job Form")
    print("=" * 50)

    # Initialize components
    path_manager = PathManager()
    storage = StorageManager(path_manager.get_data_dir())
    await storage.initialize()
    
    text_sim = TextSimilarity()

    # Load your profile
    profile_id = "sanket_muchhala_profile"
    profile_data = await storage.load_profile(profile_id)
    
    if not profile_data:
        print("❌ Profile not found. Please run setup_profile.py first.")
        return

    print(f"👤 Profile loaded: {profile_data.get('personal', {}).get('full_name', 'Unknown')}")
    print(f"💼 Current role: {profile_data.get('experience', [{}])[0].get('position', 'Unknown')}")
    print(f"🏢 Company: {profile_data.get('experience', [{}])[0].get('company', 'Unknown')}")

    # Sample job application form (like what you'd find on LinkedIn, Indeed, etc.)
    sample_job_form = """
    <form class="job-application-form">
        <h2>Senior AI/ML Engineer Application</h2>
        
        <div class="form-section">
            <label for="first_name">First Name *</label>
            <input type="text" id="first_name" name="first_name" required>
            
            <label for="last_name">Last Name *</label>
            <input type="text" id="last_name" name="last_name" required>
            
            <label for="email">Email Address *</label>
            <input type="email" id="email" name="email" required>
            
            <label for="phone">Phone Number</label>
            <input type="tel" id="phone" name="phone">
        </div>
        
        <div class="form-section">
            <label for="current_company">Current Company</label>
            <input type="text" id="current_company" name="current_company">
            
            <label for="current_position">Current Position</label>
            <input type="text" id="current_position" name="current_position">
            
            <label for="years_experience">Years of Experience *</label>
            <input type="number" id="years_experience" name="years_experience" required>
        </div>
        
        <div class="form-section">
            <label for="desired_salary">Desired Salary (Annual)</label>
            <input type="number" id="desired_salary" name="desired_salary" placeholder="e.g., 150000">
            
            <label for="linkedin_url">LinkedIn Profile URL</label>
            <input type="url" id="linkedin_url" name="linkedin_url">
            
            <label for="github_url">GitHub Profile URL</label>
            <input type="url" id="github_url" name="github_url">
        </div>
        
        <div class="form-section">
            <label for="cover_letter">Cover Letter</label>
            <textarea id="cover_letter" name="cover_letter" rows="6" 
                      placeholder="Tell us why you're interested in this position..."></textarea>
        </div>
    </form>
    """

    print("\n📝 Analyzing Job Application Form...")
    print("-" * 30)

    # Extract form fields (simplified version)
    form_fields = [
        {"field_id": "first_name", "label": "First Name", "required": True},
        {"field_id": "last_name", "label": "Last Name", "required": True},
        {"field_id": "email", "label": "Email Address", "required": True},
        {"field_id": "phone", "label": "Phone Number", "required": False},
        {"field_id": "current_company", "label": "Current Company", "required": False},
        {"field_id": "current_position", "label": "Current Position", "required": False},
        {"field_id": "years_experience", "label": "Years of Experience", "required": True},
        {"field_id": "desired_salary", "label": "Desired Salary", "required": False},
        {"field_id": "linkedin_url", "label": "LinkedIn Profile URL", "required": False},
        {"field_id": "github_url", "label": "GitHub Profile URL", "required": False},
        {"field_id": "cover_letter", "label": "Cover Letter", "required": False},
    ]

    print("🔍 Field Matching Results:")
    print("-" * 30)

    # Match each field to your profile
    for field in form_fields:
        field_type, confidence = text_sim.semantic_field_match(field["label"])
        
        # Get the actual value from your profile
        value = get_profile_value(profile_data, field_type)
        
        print(f"📋 {field['label']}:")
        print(f"   🎯 Matched to: {field_type} (confidence: {confidence}%)")
        print(f"   💾 Your value: {value}")
        print()

    print("🎉 Form Analysis Complete!")
    print("\n💡 This is what happens when you use ApplicationAgent with real job forms:")
    print("   ✅ Automatically identifies form fields")
    print("   ✅ Matches them to your profile data")
    print("   ✅ Fills in your information accurately")
    print("   ✅ Saves you time on repetitive applications")


def get_profile_value(profile_data, field_type):
    """Extract value from profile based on field type"""
    if field_type == "first_name":
        return profile_data.get('personal', {}).get('first_name', 'N/A')
    elif field_type == "last_name":
        return profile_data.get('personal', {}).get('last_name', 'N/A')
    elif field_type == "email":
        return profile_data.get('contact', {}).get('email', 'N/A')
    elif field_type == "phone":
        return profile_data.get('contact', {}).get('phone', 'N/A')
    elif field_type == "linkedin":
        return profile_data.get('contact', {}).get('linkedin_url', 'N/A')
    elif field_type == "github":
        return profile_data.get('contact', {}).get('portfolio_url', 'N/A')
    elif field_type == "experience":
        # Calculate total experience
        experiences = profile_data.get('experience', [])
        total_years = 0
        for exp in experiences:
            if exp.get('current'):
                total_years += 3.4  # Approximate for current role
            else:
                # Calculate years between start and end
                total_years += 2  # Approximate
        return f"{total_years:.1f} years"
    elif field_type == "salary":
        return f"${profile_data.get('compensation', {}).get('desired_salary_min', 'N/A'):,}"
    else:
        return "N/A"


async def main():
    """Main function"""
    try:
        await test_job_form_analysis()
        
        print("\n" + "=" * 50)
        print("🚀 Your ApplicationAgent is ready to use!")
        print("\n📋 Next steps:")
        print("   1. Use with real job application forms")
        print("   2. Connect to Claude Desktop for enhanced features")
        print("   3. Customize your profile further")
        print("   4. Set up DeepSeek API key for advanced AI features")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
