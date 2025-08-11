# 🚀 AI Job Application Agent with DeepSeek Integration

An intelligent job application automation tool that uses DeepSeek's powerful AI API for semantic field matching, contextual response generation, and form analysis - all at ultra-low cost.

## ✨ Features

### 🤖 AI-Powered Intelligence
- **DeepSeek Integration**: Ultra-cheap AI processing (~$0.14 per 1M input tokens)
- **Smart Field Matching**: AI understands form fields and maps them to your profile
- **Contextual Responses**: Generate tailored responses based on job context
- **Form Analysis**: Automatically analyze job application forms
- **Cost Tracking**: Built-in budget monitoring and usage analytics

### 📊 Key Capabilities
- **Profile Management**: Store and manage multiple user profiles
- **Semantic Matching**: Advanced field-to-profile mapping with confidence scores
- **Response Generation**: AI-powered contextual responses for any field type
- **Form Parsing**: Extract structure and requirements from HTML forms
- **Learning System**: Improves from user corrections and feedback
- **Cost Optimization**: Intelligent caching and batch processing

### 💰 Ultra-Low Cost Structure
- **Light Usage** (10 applications/month): ~$0.50
- **Heavy Usage** (100 applications/month): ~$3.00
- **Power User** (300 applications/month): ~$8.00

## 🛠 Installation & Setup

### Prerequisites
- Python 3.8+
- DeepSeek API key (get one at [deepseek.com](https://deepseek.com))

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd JobApplicationAgent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your DeepSeek API key
```

4. **Initialize the system**
```bash
python src/cli.py setup
```

5. **Test AI connection**
```bash
python src/cli.py test-ai
```

### Claude Desktop Integration

1. **Update Claude Desktop configuration**
```json
{
  "mcpServers": {
    "job-application-agent": {
      "command": "python",
      "args": ["/path/to/JobApplicationAgent/run_server.py"],
      "env": {
        "DEEPSEEK_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

2. **Start the server**
```bash
python run_server.py
```

## 🎯 Usage

### CLI Interface

**Create a profile:**
```bash
python src/cli.py create-profile
```

**Analyze a form:**
```bash
python src/cli.py analyze-form --html-file form.html
```

**View usage statistics:**
```bash
python src/cli.py usage-stats
```

### MCP Tools (Claude Desktop)

**Available Tools:**
- `create_profile` - Create user profiles
- `analyze_form_with_ai` - AI-powered form analysis
- `ai_match_fields` - Intelligent field matching
- `ai_generate_responses` - Contextual response generation
- `get_ai_usage_stats` - Cost and usage tracking

**Example Usage in Claude:**
```
Please analyze this job application form and match it to my profile:
[HTML content]
```

## 🏗 Architecture

### Core Components

```
JobApplicationAgent/
├── src/
│   ├── server.py                 # Main MCP server
│   ├── cli.py                   # CLI interface
│   ├── models/                  # Data models
│   │   ├── ai_config.py         # AI provider configuration
│   │   ├── profile.py           # User profile models
│   │   ├── application.py       # Application models
│   │   └── form.py              # Form analysis models
│   ├── services/                # Core services
│   │   ├── ai_service.py        # AI provider abstraction
│   │   ├── deepseek_service.py  # DeepSeek implementation
│   │   ├── semantic_matcher.py  # Field matching logic
│   │   ├── form_analyzer.py     # Form analysis engine
│   │   └── response_generator.py # Response generation
│   └── utils/                   # Utilities
│       ├── storage.py           # Data persistence
│       ├── prompts.py           # AI prompt management
│       └── encryption.py       # Data security
├── config/                      # Configuration files
│   ├── ai_providers.json        # AI provider settings
│   ├── field_patterns.json     # Field matching patterns
│   └── prompts/                 # AI prompts
└── data/                        # Local data storage
    ├── profiles/                # User profiles
    ├── applications/            # Application history
    └── field_mappings/          # Learned mappings
```

### AI Integration Flow

1. **Form Analysis** → DeepSeek analyzes HTML structure
2. **Field Matching** → AI maps fields to profile data
3. **Response Generation** → Contextual responses created
4. **Cost Tracking** → Usage and costs monitored
5. **Learning** → System improves from corrections

## 📋 Configuration

### Environment Variables

```bash
# DeepSeek API Configuration
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# AI Service Settings
DEFAULT_AI_PROVIDER=deepseek
ENABLE_AI_CACHING=true
MAX_TOKENS_PER_REQUEST=4000
AI_TEMPERATURE=0.1

# Cost Management
MONTHLY_BUDGET_USD=10.00
ENABLE_COST_ALERTS=true
COST_ALERT_THRESHOLD=0.80

# Data Storage
DATA_DIR=./data
ENCRYPTION_ENABLED=true
```

### AI Provider Configuration

The system supports multiple AI providers with easy switching:

```json
{
  "providers": {
    "deepseek": {
      "name": "DeepSeek",
      "api_base": "https://api.deepseek.com/v1",
      "model": "deepseek-chat",
      "cost_per_1k_input": 0.00014,
      "cost_per_1k_output": 0.00028
    },
    "local": {
      "name": "Local Model",
      "enabled": false,
      "note": "Future implementation for complete privacy"
    }
  }
}
```

## 💡 Advanced Features

### Intelligent Field Matching

The system uses multiple approaches for field matching:
- **AI Analysis**: DeepSeek understands context and semantics
- **Pattern Matching**: Regex patterns for common fields
- **Fuzzy Matching**: Text similarity for edge cases
- **Learning**: Improves from user corrections

### Cost Optimization

- **Intelligent Caching**: Avoid repeated API calls
- **Batch Processing**: Process multiple fields together
- **Budget Monitoring**: Track costs and usage patterns
- **Rate Limiting**: Respect API limits

### Privacy & Security

- **Local Storage**: All data stored locally
- **Encryption**: Sensitive data encrypted at rest
- **No Data Sharing**: Your information stays private
- **Future Local Models**: Migration path to local AI

## 🔧 Development

### Running Tests
```bash
pytest tests/
```

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run in development mode
python src/cli.py --help
```

### Adding New AI Providers

1. Create provider class inheriting from `AIService`
2. Implement required methods
3. Add to configuration
4. Test integration

## 📊 Cost Analysis

### DeepSeek Pricing
- Input: $0.14 per 1M tokens
- Output: $0.28 per 1M tokens

### Typical Usage Costs
- **Form Analysis**: ~$0.01-0.03 per form
- **Field Matching**: ~$0.005-0.01 per form
- **Response Generation**: ~$0.02-0.05 per form

### Monthly Cost Examples
- **10 applications**: ~$0.50
- **50 applications**: ~$2.50
- **100 applications**: ~$5.00
- **300 applications**: ~$15.00

## 🛣 Roadmap

### Current (v1.0)
- ✅ DeepSeek integration
- ✅ Basic form analysis
- ✅ Profile management
- ✅ Cost tracking

### Near Future (v1.1)
- 🔄 Local model support
- 🔄 Browser extension
- 🔄 Advanced learning
- 🔄 Multi-language support

### Future (v2.0)
- 🎯 Interview preparation
- 🎯 Application tracking
- 🎯 Performance analytics
- 🎯 Team collaboration

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: support@jobagent.ai

## 🎉 Acknowledgments

- **DeepSeek**: For providing powerful and affordable AI APIs
- **Anthropic**: For Claude and MCP framework
- **Contributors**: All the amazing people who help improve this tool

---

**Made with ❤️ for job seekers worldwide**

*Automate the tedious, focus on what matters - landing your dream job!*