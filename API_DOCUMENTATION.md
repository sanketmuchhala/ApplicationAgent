# 📚 JobApplicationAgent API Documentation

## Overview

The JobApplicationAgent exposes its functionality through MCP (Model Context Protocol) tools that can be used with Claude Desktop or other MCP-compatible clients.

## Available MCP Tools

### Profile Management

#### `create_profile`
Creates a new user profile with personal and professional information.

**Input Schema:**
```json
{
  "profile_data": {
    "type": "object",
    "description": "Complete profile information including personal, contact, experience, and preferences"
  }
}
```

**Example:**
```json
{
  "profile_data": {
    "personal": {
      "first_name": "John",
      "last_name": "Doe",
      "city": "San Francisco",
      "state": "CA"
    },
    "contact": {
      "email": "john.doe@example.com",
      "phone": "+1-555-0123"
    },
    "experience": [{
      "company": "TechCorp",
      "position": "Software Engineer",
      "start_date": "2020-01-01"
    }]
  }
}
```

#### `update_profile`
Updates an existing user profile.

**Input Schema:**
```json
{
  "profile_id": {
    "type": "string",
    "description": "Profile ID to update"
  },
  "updates": {
    "type": "object", 
    "description": "Profile fields to update"
  }
}
```

#### `get_profile`
Retrieves a user profile by ID.

**Input Schema:**
```json
{
  "profile_id": {
    "type": "string",
    "description": "Profile ID to retrieve"
  }
}
```

#### `list_profiles`
Lists all user profiles.

**Input Schema:** None required.

### AI Provider Management

#### `configure_ai_provider`
Configures AI provider settings.

**Input Schema:**
```json
{
  "provider": {
    "type": "string",
    "description": "Provider name (deepseek, local, basic)"
  },
  "api_key": {
    "type": "string",
    "description": "API key for the provider"
  },
  "settings": {
    "type": "object",
    "description": "Additional provider settings"
  }
}
```

#### `switch_ai_provider`
Switches to a different AI provider.

**Input Schema:**
```json
{
  "provider": {
    "type": "string", 
    "description": "Provider name to switch to"
  }
}
```

#### `get_ai_usage_stats`
Gets AI usage statistics and costs.

**Input Schema:**
```json
{
  "timeframe": {
    "type": "string",
    "enum": ["all", "today", "month"],
    "default": "month"
  }
}
```

**Response:**
```json
{
  "usage_stats": {
    "total_tokens": 15000,
    "total_requests": 45,
    "total_cost": 2.45
  },
  "budget_info": {
    "monthly_budget": 50.0,
    "current_cost": 2.45,
    "budget_used_percentage": 4.9,
    "within_budget": true
  }
}
```

### Form Analysis Tools

#### `analyze_form_with_ai`
Analyzes job application form HTML with AI to extract fields and structure.

**Input Schema:**
```json
{
  "html_content": {
    "type": "string",
    "description": "HTML content of the job application form"
  },
  "job_context": {
    "type": "object",
    "description": "Optional job/company context information"
  }
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "fields": [{
      "name": "firstName",
      "type": "text",
      "label": "First Name",
      "required": true,
      "importance": "high"
    }],
    "form_type": "job_application",
    "complexity": "medium"
  },
  "confidence": 0.95,
  "processing_time_ms": 1200,
  "tokens_used": 800,
  "estimated_cost": 0.0012
}
```

#### `ai_match_fields`
Uses AI to match form fields to user profile data.

**Input Schema:**
```json
{
  "form_id": {
    "type": "string",
    "description": "Form ID to match fields for"
  },
  "profile_id": {
    "type": "string", 
    "description": "Profile ID to match against"
  },
  "job_context": {
    "type": "object",
    "description": "Optional job context for better matching"
  }
}
```

**Response:**
```json
{
  "success": true,
  "mappings": [{
    "field_name": "firstName",
    "field_type": "text",
    "matched_profile_field": "personal.first_name",
    "confidence": 0.98,
    "value": "John"
  }],
  "tokens_used": 600,
  "estimated_cost": 0.0008
}
```

#### `ai_generate_responses`
Generates AI responses for form fields based on profile and job context.

**Input Schema:**
```json
{
  "field_mappings": {
    "type": "object",
    "description": "Field to profile mappings"
  },
  "profile_id": {
    "type": "string",
    "description": "User profile ID"
  },
  "job_context": {
    "type": "object",
    "description": "Job and company context"
  }
}
```

### Application Management

#### `create_application`
Creates a new job application.

**Input Schema:**
```json
{
  "profile_id": {
    "type": "string",
    "description": "Associated profile ID"
  },
  "job_details": {
    "type": "object",
    "description": "Job and company information"
  },
  "form_data": {
    "type": "object",
    "description": "Form structure data"
  }
}
```

#### `update_application_status`
Updates application status.

**Input Schema:**
```json
{
  "application_id": {
    "type": "string",
    "description": "Application ID"
  },
  "status": {
    "type": "string",
    "description": "New status"
  },
  "note": {
    "type": "string",
    "description": "Optional status note"
  }
}
```

#### `get_application`
Gets application details.

**Input Schema:**
```json
{
  "application_id": {
    "type": "string",
    "description": "Application ID to retrieve"
  }
}
```

### Utility Tools

#### `test_ai_connection`
Tests connection to current AI provider.

**Input Schema:** None required.

**Response:**
```json
{
  "connection_status": "connected",
  "provider": "deepseek",
  "model_info": {
    "model": "deepseek-chat",
    "max_tokens": 4000,
    "supports_streaming": true
  }
}
```

#### `export_data`
Exports user data (profiles, applications, etc.).

**Input Schema:**
```json
{
  "data_type": {
    "type": "string",
    "enum": ["profiles", "applications", "all"]
  },
  "format": {
    "type": "string", 
    "enum": ["json", "csv"],
    "default": "json"
  }
}
```

## Usage Examples with Claude Desktop

### Analyzing a Job Form

```
Please analyze this job application form and match it to my profile:

[Paste HTML content here]
```

Claude will use the `analyze_form_with_ai` and `ai_match_fields` tools to:
1. Extract form fields and structure
2. Match fields to your profile data
3. Provide confidence scores
4. Show estimated values for each field

### Creating a Profile

```
Create a new profile for me with the following information:
- Name: John Doe
- Email: john.doe@example.com
- Current role: Senior Software Engineer at Google
- Location: Mountain View, CA
- Skills: Python, Machine Learning, Cloud Computing
```

Claude will use the `create_profile` tool to save your information.

### Checking AI Usage

```
Show me my AI usage statistics for this month
```

Claude will use the `get_ai_usage_stats` tool to display:
- Total tokens used
- Number of requests
- Costs incurred
- Budget status

### Testing AI Connection

```
Test if the AI connection is working
```

Claude will use the `test_ai_connection` tool to verify connectivity.

## Error Handling

All tools return structured error responses when issues occur:

```json
{
  "error": "Description of what went wrong",
  "tool": "tool_name_that_failed",
  "error_code": "SPECIFIC_ERROR_CODE"
}
```

Common error codes:
- `API_KEY_MISSING`: AI provider API key not configured
- `PROFILE_NOT_FOUND`: Requested profile doesn't exist
- `FORM_ANALYSIS_FAILED`: Could not parse form HTML
- `BUDGET_EXCEEDED`: Monthly budget limit reached
- `RATE_LIMIT_EXCEEDED`: API rate limit hit

## Cost Information

### DeepSeek Pricing
- Input tokens: $0.14 per 1M tokens
- Output tokens: $0.28 per 1M tokens

### Typical Costs per Operation
- Form analysis: $0.01-0.03
- Field matching: $0.005-0.01
- Response generation: $0.02-0.05

### Budget Management
Set monthly budgets and get alerts when approaching limits:
- Budget tracking enabled by default
- Alerts at 80% of budget
- Operations blocked when budget exceeded

## Rate Limits

### DeepSeek Limits
- 100 requests per minute
- 500,000 tokens per minute

The system automatically handles rate limiting with:
- Request queuing
- Exponential backoff
- Graceful degradation to backup providers

## Security & Privacy

### Data Handling
- All data stored locally
- No data shared with third parties
- API keys encrypted at rest
- Form data processed temporarily

### API Key Security
- Store keys in environment variables
- Never commit keys to version control
- Use .env files for development
- Rotate keys regularly

## Development & Integration

### Adding Custom Tools

To add new MCP tools:

1. Define the tool in `_register_tools()`:
```python
Tool(
    name="my_custom_tool",
    description="Description of what it does",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param1"]
    }
)
```

2. Implement the handler:
```python
async def _my_custom_tool(self, args: Dict[str, Any]) -> Dict[str, Any]:
    param1 = args["param1"]
    # Implementation logic
    return {"success": True, "result": "..."}
```

3. Add to the tool router in `_execute_tool()`.

### Testing Tools

Test individual tools:
```python
import asyncio
from src.server import JobApplicationAgentServer

async def test_tool():
    server = JobApplicationAgentServer()
    await server.initialize()
    result = await server._execute_tool("tool_name", {"param": "value"})
    print(result)

asyncio.run(test_tool())
```

## Troubleshooting

### Common Issues

1. **Tool not available in Claude Desktop**
   - Check MCP server is running
   - Verify claude_desktop_config.json
   - Restart Claude Desktop

2. **API connection failures**
   - Verify API key is set
   - Check network connectivity
   - Confirm API endpoint URL

3. **High costs/token usage**
   - Review prompt efficiency
   - Check for unnecessary API calls
   - Consider caching strategies

4. **Poor field matching accuracy**
   - Provide more job context
   - Update profile with relevant keywords
   - Use manual corrections to improve learning

For more troubleshooting help, see the [Setup Guide](SETUP_GUIDE.md) and [Contributing Guidelines](CONTRIBUTING.md).