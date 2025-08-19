// JobApplicationAgent - API Manager for AI Providers
export class APIManager {
  constructor() {
    this.providers = {
      free: new FreeProvider(),
      deepseek: new DeepSeekProvider(),
      gemini: new GeminiProvider()
    };
    this.currentProvider = null;
    this.settings = null;
    this.init();
  }

  async init() {
    await this.loadSettings();
    this.setCurrentProvider();
  }

  async loadSettings() {
    try {
      const result = await chrome.storage.local.get(['settings']);
      this.settings = result.settings || { aiProvider: 'free' };
    } catch (error) {
      console.error('Error loading settings:', error);
      this.settings = { aiProvider: 'free' };
    }
  }

  setCurrentProvider() {
    const providerType = this.settings.aiProvider || 'free';
    this.currentProvider = this.providers[providerType];
    
    if (this.currentProvider && this.settings.apiKeys) {
      this.currentProvider.setApiKey(this.settings.apiKeys[providerType]);
    }
  }

  async analyzeFields(fields, profile, context = {}) {
    await this.loadSettings();
    this.setCurrentProvider();
    
    if (!this.currentProvider) {
      throw new Error('No AI provider configured');
    }

    return await this.currentProvider.analyzeFields(fields, profile, context);
  }

  async generateResponse(fieldInfo, profile, context = {}) {
    await this.loadSettings();
    this.setCurrentProvider();
    
    if (!this.currentProvider) {
      throw new Error('No AI provider configured');
    }

    return await this.currentProvider.generateResponse(fieldInfo, profile, context);
  }

  async testApiKey(provider, apiKey) {
    const providerInstance = this.providers[provider];
    if (!providerInstance) {
      throw new Error('Invalid provider');
    }

    providerInstance.setApiKey(apiKey);
    return await providerInstance.testConnection();
  }
}

// Base AI Provider Class
class BaseProvider {
  constructor(name) {
    this.name = name;
    this.apiKey = null;
  }

  setApiKey(apiKey) {
    this.apiKey = apiKey;
  }

  async testConnection() {
    throw new Error('testConnection not implemented');
  }

  async analyzeFields(fields, profile, context) {
    throw new Error('analyzeFields not implemented');
  }

  async generateResponse(fieldInfo, profile, context) {
    throw new Error('generateResponse not implemented');
  }

  countTokens(text) {
    // Simple token estimation (4 chars per token average)
    return Math.ceil(text.length / 4);
  }

  calculateCost(inputTokens, outputTokens, inputRate, outputRate) {
    return (inputTokens * inputRate / 1000) + (outputTokens * outputRate / 1000);
  }
}

// Free Provider (Built-in Logic)
class FreeProvider extends BaseProvider {
  constructor() {
    super('free');
  }

  async testConnection() {
    return true; // Always available
  }

  async analyzeFields(fields, profile, context) {
    // Simple field matching without AI
    const matches = [];
    
    for (const field of fields) {
      const match = this.matchFieldToProfile(field, profile);
      if (match) {
        matches.push(match);
      }
    }

    return {
      success: true,
      provider: 'free',
      fieldMatches: matches,
      tokensUsed: 0,
      cost: 0
    };
  }

  matchFieldToProfile(field, profile) {
    const fieldText = `${field.label || ''} ${field.name || ''} ${field.id || ''}`.toLowerCase();
    
    // Simple pattern matching
    const patterns = {
      firstName: ['first', 'fname', 'given'],
      lastName: ['last', 'lname', 'surname', 'family'],
      email: ['email', 'e-mail'],
      phone: ['phone', 'tel', 'mobile', 'cell'],
      city: ['city', 'town'],
      state: ['state', 'province', 'region'],
      position: ['position', 'title', 'role', 'job'],
      company: ['company', 'employer', 'organization'],
      experience: ['experience', 'years'],
      skills: ['skills', 'competencies', 'expertise']
    };

    for (const [fieldType, keywords] of Object.entries(patterns)) {
      if (keywords.some(keyword => fieldText.includes(keyword))) {
        const value = this.getProfileValue(fieldType, profile);
        if (value) {
          return {
            fieldId: field.id,
            fieldType: fieldType,
            label: field.label || field.name || field.id,
            value: value,
            confidence: 75, // Static confidence for free version
            element: field.element
          };
        }
      }
    }

    return null;
  }

  getProfileValue(fieldType, profile) {
    const mappings = {
      firstName: profile.personal?.first_name,
      lastName: profile.personal?.last_name,
      email: profile.contact?.email,
      phone: profile.contact?.phone,
      city: profile.personal?.city,
      state: profile.personal?.state,
      position: profile.professional?.current_position,
      company: profile.professional?.current_company,
      experience: profile.professional?.years_of_experience?.toString(),
      skills: profile.technical_skills?.join(', ')
    };

    return mappings[fieldType] || '';
  }

  async generateResponse(fieldInfo, profile, context) {
    // Simple template-based response generation
    const value = this.getProfileValue(fieldInfo.fieldType, profile);
    
    return {
      success: true,
      provider: 'free',
      response: value,
      confidence: 75,
      tokensUsed: 0,
      cost: 0
    };
  }
}

// DeepSeek Provider
class DeepSeekProvider extends BaseProvider {
  constructor() {
    super('deepseek');
    this.apiBase = 'https://api.deepseek.com/v1';
    this.model = 'deepseek-chat';
    this.inputCostPer1K = 0.00014;
    this.outputCostPer1K = 0.00028;
  }

  async testConnection() {
    if (!this.apiKey) return false;

    try {
      const response = await fetch(`${this.apiBase}/models`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        }
      });

      return response.ok;
    } catch (error) {
      console.error('DeepSeek connection test failed:', error);
      return false;
    }
  }

  async analyzeFields(fields, profile, context) {
    if (!this.apiKey) {
      throw new Error('DeepSeek API key not configured');
    }

    const prompt = this.buildFieldAnalysisPrompt(fields, profile, context);
    
    try {
      const response = await this.makeRequest({
        model: this.model,
        messages: [
          { role: 'system', content: 'You are an expert at matching job application form fields to user profile data. Respond only with valid JSON.' },
          { role: 'user', content: prompt }
        ],
        temperature: 0.1,
        max_tokens: 2000
      });

      const result = JSON.parse(response.content);
      const inputTokens = this.countTokens(prompt);
      const outputTokens = this.countTokens(response.content);
      const cost = this.calculateCost(inputTokens, outputTokens, this.inputCostPer1K, this.outputCostPer1K);

      return {
        success: true,
        provider: 'deepseek',
        fieldMatches: result.fieldMatches || [],
        confidence: result.confidence || 85,
        tokensUsed: inputTokens + outputTokens,
        cost: cost
      };

    } catch (error) {
      console.error('DeepSeek field analysis error:', error);
      return {
        success: false,
        provider: 'deepseek',
        error: error.message
      };
    }
  }

  async generateResponse(fieldInfo, profile, context) {
    if (!this.apiKey) {
      throw new Error('DeepSeek API key not configured');
    }

    const prompt = this.buildResponseGenerationPrompt(fieldInfo, profile, context);
    
    try {
      const response = await this.makeRequest({
        model: this.model,
        messages: [
          { role: 'system', content: 'You are an expert at writing professional job application responses. Be concise and relevant.' },
          { role: 'user', content: prompt }
        ],
        temperature: 0.3,
        max_tokens: 500
      });

      const inputTokens = this.countTokens(prompt);
      const outputTokens = this.countTokens(response.content);
      const cost = this.calculateCost(inputTokens, outputTokens, this.inputCostPer1K, this.outputCostPer1K);

      return {
        success: true,
        provider: 'deepseek',
        response: response.content.trim(),
        confidence: 90,
        tokensUsed: inputTokens + outputTokens,
        cost: cost
      };

    } catch (error) {
      console.error('DeepSeek response generation error:', error);
      return {
        success: false,
        provider: 'deepseek',
        error: error.message
      };
    }
  }

  buildFieldAnalysisPrompt(fields, profile, context) {
    return `
Analyze the following job application form fields and match them to the user's profile data. Return a JSON response with field matches.

User Profile:
${JSON.stringify(profile, null, 2)}

Form Fields:
${fields.map(f => `- ${f.label || f.name || f.id}: ${f.type || 'text'}`).join('\n')}

Context:
${JSON.stringify(context, null, 2)}

Return JSON in this format:
{
  "fieldMatches": [
    {
      "fieldId": "field_id",
      "fieldType": "firstName|lastName|email|phone|etc",
      "label": "Field Label",
      "value": "Profile value to fill",
      "confidence": 95
    }
  ],
  "confidence": 88
}

Only include fields you can confidently match with profile data.
    `;
  }

  buildResponseGenerationPrompt(fieldInfo, profile, context) {
    return `
Generate a professional response for this job application field:

Field: ${fieldInfo.label}
Field Type: ${fieldInfo.type || 'text'}
Current Value: ${fieldInfo.value || 'None'}

User Profile:
${JSON.stringify(profile, null, 2)}

Job Context:
${JSON.stringify(context, null, 2)}

Generate a concise, professional response appropriate for this field. If it's a cover letter or essay field, write 2-3 sentences. For simple fields, provide just the relevant information.
    `;
  }

  async makeRequest(payload) {
    const response = await fetch(`${this.apiBase}/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`DeepSeek API error: ${response.status} - ${error}`);
    }

    const result = await response.json();
    return {
      content: result.choices[0].message.content,
      usage: result.usage
    };
  }
}

// Google Gemini Provider
class GeminiProvider extends BaseProvider {
  constructor() {
    super('gemini');
    this.apiBase = 'https://generativelanguage.googleapis.com/v1beta';
    this.model = 'gemini-pro';
    this.inputCostPer1K = 0.0005;
    this.outputCostPer1K = 0.0015;
  }

  async testConnection() {
    if (!this.apiKey) return false;

    try {
      const response = await fetch(`${this.apiBase}/models?key=${this.apiKey}`);
      return response.ok;
    } catch (error) {
      console.error('Gemini connection test failed:', error);
      return false;
    }
  }

  async analyzeFields(fields, profile, context) {
    if (!this.apiKey) {
      throw new Error('Gemini API key not configured');
    }

    const prompt = this.buildFieldAnalysisPrompt(fields, profile, context);
    
    try {
      const response = await this.makeRequest(prompt);
      
      const result = JSON.parse(response.content);
      const inputTokens = this.countTokens(prompt);
      const outputTokens = this.countTokens(response.content);
      const cost = this.calculateCost(inputTokens, outputTokens, this.inputCostPer1K, this.outputCostPer1K);

      return {
        success: true,
        provider: 'gemini',
        fieldMatches: result.fieldMatches || [],
        confidence: result.confidence || 85,
        tokensUsed: inputTokens + outputTokens,
        cost: cost
      };

    } catch (error) {
      console.error('Gemini field analysis error:', error);
      return {
        success: false,
        provider: 'gemini',
        error: error.message
      };
    }
  }

  async generateResponse(fieldInfo, profile, context) {
    if (!this.apiKey) {
      throw new Error('Gemini API key not configured');
    }

    const prompt = this.buildResponseGenerationPrompt(fieldInfo, profile, context);
    
    try {
      const response = await this.makeRequest(prompt);
      
      const inputTokens = this.countTokens(prompt);
      const outputTokens = this.countTokens(response.content);
      const cost = this.calculateCost(inputTokens, outputTokens, this.inputCostPer1K, this.outputCostPer1K);

      return {
        success: true,
        provider: 'gemini',
        response: response.content.trim(),
        confidence: 90,
        tokensUsed: inputTokens + outputTokens,
        cost: cost
      };

    } catch (error) {
      console.error('Gemini response generation error:', error);
      return {
        success: false,
        provider: 'gemini',
        error: error.message
      };
    }
  }

  buildFieldAnalysisPrompt(fields, profile, context) {
    // Same as DeepSeek implementation
    return `
Analyze the following job application form fields and match them to the user's profile data. Return a JSON response with field matches.

User Profile:
${JSON.stringify(profile, null, 2)}

Form Fields:
${fields.map(f => `- ${f.label || f.name || f.id}: ${f.type || 'text'}`).join('\n')}

Context:
${JSON.stringify(context, null, 2)}

Return JSON in this format:
{
  "fieldMatches": [
    {
      "fieldId": "field_id",
      "fieldType": "firstName|lastName|email|phone|etc",
      "label": "Field Label",
      "value": "Profile value to fill",
      "confidence": 95
    }
  ],
  "confidence": 88
}

Only include fields you can confidently match with profile data.
    `;
  }

  buildResponseGenerationPrompt(fieldInfo, profile, context) {
    // Same as DeepSeek implementation
    return `
Generate a professional response for this job application field:

Field: ${fieldInfo.label}
Field Type: ${fieldInfo.type || 'text'}
Current Value: ${fieldInfo.value || 'None'}

User Profile:
${JSON.stringify(profile, null, 2)}

Job Context:
${JSON.stringify(context, null, 2)}

Generate a concise, professional response appropriate for this field. If it's a cover letter or essay field, write 2-3 sentences. For simple fields, provide just the relevant information.
    `;
  }

  async makeRequest(prompt) {
    const payload = {
      contents: [
        {
          parts: [
            { text: prompt }
          ]
        }
      ],
      generationConfig: {
        temperature: 0.1,
        topK: 40,
        topP: 0.95,
        maxOutputTokens: 2048
      }
    };

    const response = await fetch(`${this.apiBase}/models/${this.model}:generateContent?key=${this.apiKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Gemini API error: ${response.status} - ${error}`);
    }

    const result = await response.json();
    
    if (!result.candidates || !result.candidates[0]) {
      throw new Error('No response from Gemini API');
    }

    return {
      content: result.candidates[0].content.parts[0].text,
      usage: result.usageMetadata
    };
  }
}

export { FreeProvider, DeepSeekProvider, GeminiProvider };