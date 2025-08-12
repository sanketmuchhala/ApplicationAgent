# 🚀 JobApplicationAgent - Complete Setup Guide

This guide will walk you through setting up the JobApplicationAgent system from scratch, including all dependencies, configuration, and testing.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.9+ (recommended 3.11+)
- **Operating System**: macOS, Linux, or Windows
- **Memory**: 512MB RAM minimum, 1GB recommended
- **Storage**: 500MB free space
- **Internet**: Required for DeepSeek API calls

### Required Accounts
- **DeepSeek API Key**: Get one at [https://deepseek.com](https://deepseek.com)
  - Sign up for free
  - Navigate to API section
  - Generate an API key
  - Free tier includes generous limits

## 🛠 Step-by-Step Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/sanketmuchhala/JobApplicationAgent.git
cd JobApplicationAgent

# Verify contents
ls -la
```

**Expected output:**
```
README.md
requirements.txt
run_server.py
setup_profile.py
analyze_job_form.py
src/
config/
data/
```

### Step 2: Set Up Python Environment

#### Option A: Using venv (Recommended)
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Verify activation (should show .venv in path)
which python
```

#### Option B: Using conda
```bash
# Create conda environment
conda create -n jobagent python=3.11
conda activate jobagent
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Verify key packages
pip list | grep -E "mcp|pydantic|httpx|pytest"
```

**Expected packages:**
- mcp>=1.0.0
- pydantic>=2.0.0
- httpx>=0.25.0
- pytest>=7.4.0
- pytest-asyncio>=0.21.0

### Step 4: Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit the .env file
nano .env  # or use your preferred editor
```

**Required .env configuration:**
```bash
# DeepSeek API Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# Default AI Provider
DEFAULT_AI_PROVIDER=deepseek

# Budget Configuration
MONTHLY_BUDGET_USD=50.0

# Application Settings
DEBUG=false
LOG_LEVEL=info
```

**🔑 Important:** Replace `your_deepseek_api_key_here` with your actual DeepSeek API key.

### Step 5: Test Basic Functionality

```bash
# Run basic tests
python -m pytest test_basic.py -v --asyncio-mode=auto
```

**Expected output:**
```
test_basic.py::test_basic_functionality PASSED
test_basic.py::test_with_sample_data PASSED
========================= 2 passed in 0.52s =========================
```

### Step 6: Create Your User Profile

```bash
# Run the interactive profile setup
python setup_profile.py
```

**Follow the prompts to enter your information:**
- Personal details (name, email, phone)
- Work experience
- Skills and technologies
- Education
- Job preferences

**Your profile will be saved to:** `data/profiles/your_profile.json`

### Step 7: Test AI Integration

```bash
# Test with a sample form (requires API key)
python test_real_job_form.py
```

**Expected output:**
```
🚀 Job Application Agent - Real Form Test
✅ DeepSeek AI connection successful
✅ Form analysis completed
✅ Field matching successful
✅ Response generation completed
```

### Step 8: Start the MCP Server

```bash
# Start the server
python run_server.py
```

**Expected output:**
```
🚀 Job Application Agent initialized with DeepSeek AI provider
Server running and ready to accept connections...
```

**Keep this terminal open** - the server needs to run continuously for Claude Desktop integration.

## 🖥 Claude Desktop Integration

### Step 1: Locate Claude Desktop Config

#### macOS
```bash
# Find Claude Desktop config
ls -la ~/Library/Application\ Support/Claude/
```

#### Windows
```cmd
# Navigate to
%APPDATA%\Claude\
```

### Step 2: Update Configuration

**Edit `claude_desktop_config.json`:**

```json
{
  "mcpServers": {
    "job-application-agent": {
      "command": "python",
      "args": ["/absolute/path/to/JobApplicationAgent/run_server.py"],
      "env": {
        "DEEPSEEK_API_KEY": "your_deepseek_api_key_here"
      }
    }
  }
}
```

**🚨 Important:** 
- Use the **absolute path** to your project directory
- Replace `your_deepseek_api_key_here` with your actual API key

#### Get Absolute Path
```bash
# In your project directory
pwd
# Copy the output for the config file
```

### Step 3: Restart Claude Desktop

1. **Quit Claude Desktop completely**
2. **Restart the application**
3. **Check for the Job Application Agent in available tools**

## 🧪 Verification & Testing

### Test 1: Basic Functionality
```bash
python -m pytest test_basic.py -v --asyncio-mode=auto
```

### Test 2: AI Connection
```bash
python test_real_job_form.py
```

### Test 3: MCP Server
```bash
# In one terminal
python run_server.py

# In another terminal (test connection)
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python run_server.py --stdio
```

### Test 4: Claude Desktop Integration
1. Open Claude Desktop
2. Start a new conversation
3. Try: "List available tools"
4. Look for job-application-agent tools

## 🚨 Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError
```bash
# Ensure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Verify Python path
which python
```

#### 2. API Connection Failed
```bash
# Check API key in .env file
cat .env | grep DEEPSEEK_API_KEY

# Test API key manually
curl -H "Authorization: Bearer your_api_key" https://api.deepseek.com/v1/models
```

#### 3. Async Test Issues
```bash
# Install pytest-asyncio if missing
pip install pytest-asyncio

# Run with explicit async mode
python -m pytest test_basic.py -v --asyncio-mode=auto
```

#### 4. Claude Desktop Not Connecting
```bash
# Check config file exists
ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Validate JSON format
python -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Check server is running
ps aux | grep run_server.py
```

#### 5. Permission Issues
```bash
# Fix file permissions
chmod +x run_server.py
chmod +x setup_profile.py

# Fix directory permissions
chmod 755 data/
chmod 755 config/
```

### Advanced Debugging

#### Enable Debug Mode
```bash
# Edit .env file
DEBUG=true
LOG_LEVEL=debug

# Restart server
python run_server.py
```

#### Check Logs
```bash
# View server logs
tail -f logs/server.log

# View application logs
tail -f logs/application.log
```

#### Test Individual Components
```bash
# Test storage system
python -c "from src.utils.storage import StorageManager; import asyncio; asyncio.run(StorageManager('data').initialize())"

# Test AI service
python -c "from src.services.deepseek_service import DeepSeekService; import asyncio; service = DeepSeekService({'api_key': 'test'}); print(asyncio.run(service.test_connection()))"
```

## 📊 Usage Monitoring

### Check API Usage
```bash
# View usage statistics
python -c "
from src.services.deepseek_service import DeepSeekService
import asyncio
import os
service = DeepSeekService({'api_key': os.getenv('DEEPSEEK_API_KEY')})
print(service.get_usage_stats('month'))
"
```

### Monitor Costs
```bash
# Check current costs
python -c "
from src.services.deepseek_service import DeepSeekService
import asyncio
import os
service = DeepSeekService({'api_key': os.getenv('DEEPSEEK_API_KEY')})
within_budget, cost, percentage = service.is_within_budget(50.0)
print(f'Current cost: ${cost:.2f}, Budget used: {percentage:.1f}%')
"
```

## 🎯 Next Steps

### 1. Create Job Applications
```bash
# Analyze a job form
python analyze_job_form.py
```

### 2. Use with Claude Desktop
- Open Claude Desktop
- Ask: "Help me analyze this job application form"
- Paste HTML content or describe the form

### 3. Customize Your Profile
```bash
# Edit your profile
nano data/profiles/your_profile.json
```

### 4. Explore Advanced Features
- Field matching patterns
- Custom response templates
- Cost optimization settings

## 🆘 Getting Help

### Support Channels
- **GitHub Issues**: [Report bugs and request features](https://github.com/sanketmuchhala/JobApplicationAgent/issues)
- **Documentation**: Check README.md and code comments
- **Community**: GitHub Discussions

### Before Asking for Help
1. **Check this setup guide**
2. **Review error messages carefully**
3. **Try the troubleshooting steps**
4. **Include relevant logs and configuration**

### Providing Good Bug Reports
1. **System information** (OS, Python version)
2. **Full error message** (with stack trace)
3. **Steps to reproduce** the issue
4. **Configuration files** (without API keys)
5. **Expected vs actual behavior**

---

## ✅ Setup Complete!

If you've made it this far, congratulations! Your JobApplicationAgent is now ready to help you automate job applications with AI-powered intelligence.

**Start using it:**
1. Run `python run_server.py` to start the server
2. Open Claude Desktop
3. Begin analyzing job forms and generating applications!

**Remember:**
- Keep your API key secure
- Monitor your usage and costs
- Keep the MCP server running when using Claude Desktop
- Regularly backup your profile data

Happy job hunting! 🎉