#!/usr/bin/env python3
"""
Analyze any job application form with your ApplicationAgent
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.text_similarity import TextSimilarity
from src.utils.storage import StorageManager
from src.utils.paths import PathManager


async def analyze_job_form(html_content: str):
    """Analyze a job form and show how ApplicationAgent would fill it"""
    print("🎯 ApplicationAgent Form Analysis")
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

    print(f"👤 Profile: {profile_data.get('personal', {}).get('full_name', 'Unknown')}")
    print(f"💼 Current: {profile_data.get('experience', [{}])[0].get('position', 'Unknown')}")
    print(f"🏢 Company: {profile_data.get('experience', [{}])[0].get('company', 'Unknown')}")

    # Extract form fields from HTML (simplified)
    form_fields = extract_form_fields(html_content)
    
    print(f"\n📝 Found {len(form_fields)} form fields:")
    print("-" * 40)

    # Analyze each field
    for field in form_fields:
        field_type, confidence = text_sim.semantic_field_match(field["label"])
        value = get_profile_value(profile_data, field_type)
        
        print(f"📋 {field['label']}:")
        print(f"   🎯 Type: {field_type} ({confidence}% confidence)")
        print(f"   💾 Your Value: {value}")
        if field.get("required"):
            print(f"   ⚠️  Required field")
        print()

    print("🎉 Analysis Complete!")
    print("\n💡 ApplicationAgent would automatically fill these fields for you!")


def extract_form_fields(html_content: str) -> list:
    """Extract form fields from HTML content"""
    # This is a simplified version - in practice, you'd use BeautifulSoup
    fields = []
    
    # Common field patterns
    field_patterns = [
        ("First Name", "first_name"),
        ("Last Name", "last_name"), 
        ("Email", "email"),
        ("Phone", "phone"),
        ("Company", "company"),
        ("Position", "position"),
        ("Experience", "experience"),
        ("Salary", "salary"),
        ("LinkedIn", "linkedin"),
        ("GitHub", "github"),
        ("Cover Letter", "cover_letter"),
        ("Resume", "resume"),
        ("Address", "address"),
        ("City", "city"),
        ("State", "state"),
        ("Country", "country"),
        ("Zip", "zip"),
    ]
    
    for label, field_id in field_patterns:
        if label.lower() in html_content.lower():
            fields.append({
                "field_id": field_id,
                "label": label,
                "required": "*" in html_content or "required" in html_content.lower()
            })
    
    return fields


def get_profile_value(profile_data: dict, field_type: str) -> str:
    """Get value from profile based on field type"""
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
        experiences = profile_data.get('experience', [])
        total_years = 0
        for exp in experiences:
            if exp.get('current'):
                total_years += 3.4
            else:
                total_years += 2
        return f"{total_years:.1f} years"
    elif field_type == "salary":
        return f"${profile_data.get('compensation', {}).get('desired_salary_min', 'N/A'):,}"
    else:
        return "N/A"


async def main():
    """Main function"""
    print("🚀 ApplicationAgent Form Analyzer")
    print("=" * 50)
    
    # Sample HTML form (replace with real form HTML)
    sample_html = """
    <form>
        <h2>Software Engineer Application</h2>
        
        <label for="first_name">First Name *</label>
        <input type="text" id="first_name" name="first_name" required>
        
        <label for="last_name">Last Name *</label>
        <input type="text" id="last_name" name="last_name" required>
        
        <label for="email">Email Address *</label>
        <input type="email" id="email" name="email" required>
        
        <label for="phone">Phone Number</label>
        <input type="tel" id="phone" name="phone">
        
        <label for="experience">Years of Experience *</label>
        <input type="number" id="experience" name="experience" required>
        
        <label for="salary">Expected Salary</label>
        <input type="number" id="salary" name="salary" placeholder="Annual salary">
        
        <label for="linkedin">LinkedIn Profile</label>
        <input type="url" id="linkedin" name="linkedin">
        
        <label for="cover_letter">Cover Letter</label>
        <textarea id="cover_letter" name="cover_letter" rows="5"></textarea>
    </form>
    """
    
    print("📝 Analyzing sample job form...")
    await analyze_job_form(sample_html)
    
    print("\n" + "=" * 50)
    print("💡 How to use with real forms:")
    print("   1. Copy HTML from any job application form")
    print("   2. Replace the sample_html in this script")
    print("   3. Run: python analyze_job_form.py")
    print("   4. See how ApplicationAgent would fill it!")


if __name__ == "__main__":
    asyncio.run(main())
