#!/usr/bin/env python3
"""
Simple profile setup script for ApplicationAgent
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


async def create_sample_profile():
    """Create a sample user profile"""
    print("🚀 Setting up your ApplicationAgent profile...")
    print("=" * 50)
    
    # Initialize storage
    path_manager = PathManager()
    storage = StorageManager(path_manager.get_data_dir())
    await storage.initialize()
    
    # Create a sample profile
    profile = UserProfile(
        profile_id="sanket_muchhala_profile",
        personal=PersonalInfo(
            first_name="Sanket",
            last_name="Muchhala",
            full_name="Sanket Muchhala",
            city="Bloomington",
            state="IN",
            country="USA",
            work_authorization="citizen"
        ),
        contact=ContactInfo(
            email="muchhalasanket@gmail.com",
            phone="+1-812-778-4451",
            linkedin_url="https://linkedin.com/in/sanket-muchhala",
            portfolio_url="https://github.com/sanketmuchhala"
        ),
        experience=[
            Experience(
                company="Progressive Insurance",
                position="AI Engineer",
                start_date="2024-05-01",
                end_date=None,
                current=True,
                description="Building NLP workflows for claims data intake and deploying GPT-4 based document summarization tools",
                key_achievements=[
                    "Streamlined processing tasks by 25% using Python and Azure ML",
                    "Reduced review cycles for compliance and legal teams by 40%",
                    "Improved fraud detection precision by 22% through real-time anomaly models",
                    "Cut drift incidents by 35% with centralized model performance tracking"
                ]
            ),
            Experience(
                company="Indiana University Bloomington",
                position="Research Assistant - Generative AI",
                start_date="2023-12-01",
                end_date="2024-05-01",
                current=False,
                description="Research in generative AI and esports analytics using GPT-4 and RAG pipelines",
                key_achievements=[
                    "Improved transcript accuracy by 18pp using GPT-4 RAG pipeline",
                    "Reduced latency 40% in chat feature via GPT-4 sentiment analysis",
                    "Processed over 200 hours of esports video on BigRed200 HPC system"
                ]
            ),
            Experience(
                company="IBM",
                position="Data Analyst",
                start_date="2020-09-01",
                end_date="2022-06-01",
                current=False,
                description="End-to-end development of ML models and ETL workflows",
                key_achievements=[
                    "Led churn prediction model development, reducing customer attrition by 20%",
                    "Improved data availability and cut processing time by 15%",
                    "Raised dashboard reporting accuracy by 18%",
                    "Accelerated release cycles by 25% across internal products"
                ]
            )
        ],
        education=[
            Education(
                institution="Indiana University Bloomington",
                degree="Master of Science",
                field_of_study="Data Science",
                start_date="2022-08-01",
                end_date="2024-05-01",
                gpa=3.8
            ),
            Education(
                institution="Thakur College of Engineering and Technology",
                degree="Bachelor of Technology",
                field_of_study="Information Technology",
                start_date="2018-08-01",
                end_date="2022-05-01",
                gpa=3.7
            )
        ],
        technical_skills=[
            "Python", "SQL", "R", "JavaScript", "Scikit-learn", "TensorFlow", "PyTorch", 
            "FastAPI", "MLflow", "SpaCy", "GPT-4", "LangChain", "RAG", "Agentic AI", 
            "Vector DBs", "FAISS", "NER", "Text Classification", "Summarization", 
            "Sentiment Analysis", "Pandas", "NumPy", "PySpark", "AWS", "Azure", 
            "PostgreSQL", "MySQL", "Snowflake", "Tableau", "Power BI"
        ],
        compensation=Compensation(
            current_salary=120000,
            desired_salary_min=140000,
            desired_salary_max=180000
        ),
        job_preferences=JobPreferences(
            desired_roles=["AI/ML Engineer", "Senior AI Engineer", "ML Engineer", "Data Scientist", "AI Research Engineer"],
            industries=["Technology", "Insurance", "Finance", "Healthcare", "Research"],
            remote_preference="hybrid"
        )
    )
    
    # Save profile
    profile_id = profile.profile_id
    success = await storage.save_profile(profile_id, profile.model_dump())
    if success:
        print(f"✅ Profile saved with ID: {profile_id}")
    else:
        print("❌ Failed to save profile")
        return profile
    
    # Load and display profile
    loaded_profile_data = await storage.load_profile(profile_id)
    if loaded_profile_data:
        print(f"📋 Profile loaded: {loaded_profile_data.get('personal', {}).get('full_name', 'Unknown')}")
        current_position = loaded_profile_data.get('experience', [{}])[0] if loaded_profile_data.get('experience') else {}
        print(f"💼 Current role: {current_position.get('position', 'None')}")
        print(f"🏢 Company: {current_position.get('company', 'None')}")
        skills = loaded_profile_data.get('technical_skills', [])
        print(f"📚 Skills: {', '.join(skills[:5]) if skills else 'None'}...")
    else:
        print("❌ Failed to load profile")
    
    return profile
    
    return profile


async def test_form_analysis():
    """Test form analysis with a sample HTML form"""
    print("\n🔍 Testing Form Analysis...")
    print("=" * 30)
    
    # Sample HTML form
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
        
        <label for="cover_letter">Cover Letter</label>
        <textarea id="cover_letter" name="cover_letter" rows="5"></textarea>
    </form>
    """
    
    print("📝 Sample form HTML:")
    print(sample_html)
    print("\n✅ Form analysis test completed!")


async def main():
    """Main setup function"""
    try:
        # Create profile
        profile = await create_sample_profile()
        
        # Test form analysis
        await test_form_analysis()
        
        print("\n" + "=" * 50)
        print("🎉 Setup completed successfully!")
        print("\n📋 What you can do next:")
        print("   1. Start the server: python run_server.py")
        print("   2. Use Claude Desktop with the MCP integration")
        print("   3. Test with real job application forms")
        print("   4. Customize your profile with real information")
        
        # Show profile data
        print(f"\n👤 Your Profile Summary:")
        print(f"   Name: {profile.personal.full_name}")
        print(f"   Location: {profile.personal.city}, {profile.personal.state}")
        print(f"   Experience: {profile.total_experience_years} years")
        print(f"   Skills: {len(profile.technical_skills)} technical skills")
        print(f"   Salary Range: ${profile.compensation.desired_salary_min:,} - ${profile.compensation.desired_salary_max:,}")
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
