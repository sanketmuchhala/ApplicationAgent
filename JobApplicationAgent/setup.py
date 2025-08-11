#!/usr/bin/env python3
"""
Setup script for Job Application Agent
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
if requirements_path.exists():
    with open(requirements_path, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
else:
    requirements = [
        "mcp>=1.0.0",
        "pydantic>=2.0.0", 
        "httpx>=0.25.0",
        "openai>=1.0.0",
        "tiktoken>=0.5.0",
        "fuzzywuzzy>=0.18.0",
        "python-levenshtein>=0.12.0",
        "beautifulsoup4>=4.12.0",
        "cryptography>=41.0.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "python-multipart>=0.0.6",
        "click>=8.1.0",
        "rich>=13.0.0",
        "python-dotenv>=1.0.0",
        "aiofiles>=23.2.0"
    ]

setup(
    name="job-application-agent",
    version="1.0.0",
    author="Job Application Agent Team",
    author_email="info@jobagent.ai",
    description="AI-powered Job Application Agent with DeepSeek integration and MCP support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/job-application-agent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
            "pre-commit>=3.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "job-agent=job_application_agent.cli:main",
            "job-agent-server=job_application_agent.server:main",
        ],
    },
    include_package_data=True,
    package_data={
        "job_application_agent": [
            "config/*.json",
            "config/prompts/*.txt",
            "data/sample_forms/*.html",
            "data/profiles/*.json",
        ],
    },
    zip_safe=False,
)