#!/bin/bash

# Job Application Agent - Installation Script
# This script sets up the Job Application Agent system

set -e  # Exit on any error

echo "🚀 Job Application Agent - Installation Script"
echo "================================================"

# Check Python version
echo "📋 Checking Python version..."
if ! python3 --version | grep -E "(3\.[89]|3\.1[0-9])" > /dev/null; then
    echo "❌ Python 3.8+ is required"
    echo "💡 Please install Python 3.8 or later"
    exit 1
fi

python_version=$(python3 --version)
echo "✅ Found $python_version"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ] || [ ! -f "README.md" ]; then
    echo "❌ Please run this script from the JobApplicationAgent directory"
    exit 1
fi

echo "📂 Installing from: $(pwd)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install the package in development mode
echo "📦 Installing Job Application Agent..."
pip install -e .

# Create necessary directories
echo "📁 Creating data directories..."
python -c "
from src.utils.paths import PathManager
pm = PathManager()
pm.ensure_directories_exist()
print('✅ Directories created')
"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created - please edit it with your DeepSeek API key"
fi

# Run basic test
echo "🧪 Running basic system test..."
if python test_basic.py; then
    echo "✅ Basic tests passed"
else
    echo "⚠️ Some tests failed, but installation completed"
fi

echo ""
echo "================================================"
echo "🎉 Installation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env file with your DeepSeek API key:"
echo "      nano .env"
echo ""
echo "   2. Test the CLI:"
echo "      source venv/bin/activate"
echo "      python src/cli.py setup"
echo ""
echo "   3. Create a profile:"
echo "      python src/cli.py create-profile"
echo ""
echo "   4. Test AI features:"
echo "      python src/cli.py test-ai"
echo ""
echo "   5. For Claude Desktop integration:"
echo "      - Copy claude_desktop_config.json to your Claude config"
echo "      - Update the path to point to this installation"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Full setup and usage guide"
echo "   - config/ - Configuration files and templates"
echo "   - data/sample_forms/ - Example job application forms"
echo ""
echo "💰 Cost Info:"
echo "   - DeepSeek API is extremely cheap (~$0.14 per 1M tokens)"
echo "   - Typical usage: $0.50-$5.00 per month"
echo "   - Built-in cost tracking and budget alerts"
echo ""
echo "❓ Need help?"
echo "   - Run: python src/cli.py --help"
echo "   - Check the README.md for detailed documentation"
echo "   - Report issues on GitHub"
echo ""
echo "🚀 Happy job hunting! 🎯"