#!/usr/bin/env python3
"""
Profile customization script for ApplicationAgent
"""

import asyncio
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.models.profile import UserProfile, PersonalInfo, ContactInfo, Experience, Education, Compensation, JobPreferences
from src.utils.storage import StorageManager
from src.utils.paths import PathManager


async def customize_profile():
    """Customize the existing profile with real user data"""
    print("🎯 Customizing Your ApplicationAgent Profile")
    print("=" * 50)
    
    # Initialize storage
    path_manager = PathManager()
    storage = StorageManager(path_manager.get_data_dir())
    await storage.initialize()
    
    # Load existing profile
    profile_id = "sanket_muchhala_profile"
    existing_data = await storage.load_profile(profile_id)
    
    if not existing_data:
        print("❌ No existing profile found. Please run setup_profile.py first.")
        return
    
    print("📋 Current Profile:")
    print(f"   Name: {existing_data.get('personal', {}).get('full_name', 'Unknown')}")
    print(f"   Email: {existing_data.get('contact', {}).get('email', 'Unknown')}")
    print(f"   Current Role: {existing_data.get('experience', [{}])[0].get('position', 'Unknown')}")
    
    print("\n🔧 Let's customize your profile with real information!")
    print("(Press Enter to keep current values)")
    
    # Get personal info
    print("\n👤 Personal Information:")
    first_name = input(f"First Name [{existing_data.get('personal', {}).get('first_name', '')}]: ").strip()
    if not first_name:
        first_name = existing_data.get('personal', {}).get('first_name', '')
    
    last_name = input(f"Last Name [{existing_data.get('personal', {}).get('last_name', '')}]: ").strip()
    if not last_name:
        last_name = existing_data.get('personal', {}).get('last_name', '')
    
    city = input(f"City [{existing_data.get('personal', {}).get('city', '')}]: ").strip()
    if not city:
        city = existing_data.get('personal', {}).get('city', '')
    
    state = input(f"State [{existing_data.get('personal', {}).get('state', '')}]: ").strip()
    if not state:
        state = existing_data.get('personal', {}).get('state', '')
    
    # Get contact info
    print("\n📧 Contact Information:")
    email = input(f"Email [{existing_data.get('contact', {}).get('email', '')}]: ").strip()
    if not email:
        email = existing_data.get('contact', {}).get('email', '')
    
    phone = input(f"Phone [{existing_data.get('contact', {}).get('phone', '')}]: ").strip()
    if not phone:
        phone = existing_data.get('contact', {}).get('phone', '')
    
    linkedin = input(f"LinkedIn URL [{existing_data.get('contact', {}).get('linkedin_url', '')}]: ").strip()
    if not linkedin:
        linkedin = existing_data.get('contact', {}).get('linkedin_url', '')
    
    # Get experience info
    print("\n💼 Current Experience:")
    current_position = input(f"Current Position [{existing_data.get('experience', [{}])[0].get('position', '')}]: ").strip()
    if not current_position:
        current_position = existing_data.get('experience', [{}])[0].get('position', '')
    
    current_company = input(f"Current Company [{existing_data.get('experience', [{}])[0].get('company', '')}]: ").strip()
    if not current_company:
        current_company = existing_data.get('experience', [{}])[0].get('company', '')
    
    # Get skills
    print("\n📚 Technical Skills:")
    print("Current skills:", ", ".join(existing_data.get('technical_skills', [])))
    new_skills = input("Add new skills (comma-separated): ").strip()
    
    # Get salary info
    print("\n💰 Salary Information:")
    current_salary = input(f"Current Salary [{existing_data.get('compensation', {}).get('current_salary', '')}]: ").strip()
    if not current_salary:
        current_salary = existing_data.get('compensation', {}).get('current_salary', '')
    else:
        try:
            current_salary = int(current_salary)
        except ValueError:
            current_salary = existing_data.get('compensation', {}).get('current_salary', '')
    
    desired_min = input(f"Desired Salary Min [{existing_data.get('compensation', {}).get('desired_salary_min', '')}]: ").strip()
    if not desired_min:
        desired_min = existing_data.get('compensation', {}).get('desired_salary_min', '')
    else:
        try:
            desired_min = int(desired_min)
        except ValueError:
            desired_min = existing_data.get('compensation', {}).get('desired_salary_min', '')
    
    desired_max = input(f"Desired Salary Max [{existing_data.get('compensation', {}).get('desired_salary_max', '')}]: ").strip()
    if not desired_max:
        desired_max = existing_data.get('compensation', {}).get('desired_salary_max', '')
    else:
        try:
            desired_max = int(desired_max)
        except ValueError:
            desired_max = existing_data.get('compensation', {}).get('desired_salary_max', '')
    
    # Update the profile
    updated_data = existing_data.copy()
    updated_data['personal'].update({
        'first_name': first_name,
        'last_name': last_name,
        'full_name': f"{first_name} {last_name}",
        'city': city,
        'state': state
    })
    
    updated_data['contact'].update({
        'email': email,
        'phone': phone,
        'linkedin_url': linkedin
    })
    
    if updated_data.get('experience'):
        updated_data['experience'][0].update({
            'position': current_position,
            'company': current_company
        })
    
    if new_skills:
        new_skills_list = [skill.strip() for skill in new_skills.split(',')]
        updated_data['technical_skills'].extend(new_skills_list)
    
    updated_data['compensation'].update({
        'current_salary': current_salary,
        'desired_salary_min': desired_min,
        'desired_salary_max': desired_max
    })
    
    # Save updated profile
    success = await storage.save_profile(profile_id, updated_data)
    if success:
        print(f"\n✅ Profile updated successfully!")
        print(f"📋 Updated Profile Summary:")
        print(f"   Name: {updated_data['personal']['full_name']}")
        print(f"   Email: {updated_data['contact']['email']}")
        print(f"   Location: {updated_data['personal']['city']}, {updated_data['personal']['state']}")
        print(f"   Current Role: {updated_data['experience'][0]['position']} at {updated_data['experience'][0]['company']}")
        print(f"   Skills: {len(updated_data['technical_skills'])} technical skills")
        print(f"   Salary Range: ${updated_data['compensation']['desired_salary_min']:,} - ${updated_data['compensation']['desired_salary_max']:,}")
    else:
        print("❌ Failed to update profile")
    
    return updated_data


async def main():
    """Main function"""
    try:
        await customize_profile()
        
        print("\n" + "=" * 50)
        print("🎉 Profile customization completed!")
        print("\n📋 Next steps:")
        print("   1. Start the server: python run_server.py")
        print("   2. Test with real job application forms")
        print("   3. Use Claude Desktop integration")
        
    except Exception as e:
        print(f"❌ Customization failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
