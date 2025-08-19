// JobApplicationAgent Setup Wizard JavaScript
class SetupWizard {
  constructor() {
    this.currentStep = 1;
    this.maxSteps = 4;
    this.selectedProvider = 'free';
    this.profileData = {};
    this.isEditMode = false;
    this.init();
  }

  async init() {
    this.checkEditMode();
    await this.loadExistingProfile();
    this.setupEventListeners();
    this.populateDefaultData();
  }

  checkEditMode() {
    const urlParams = new URLSearchParams(window.location.search);
    this.isEditMode = urlParams.get('edit') === 'true';
    
    if (this.isEditMode) {
      // Skip to step 2 for editing
      this.currentStep = 2;
      this.updateProgressBar();
      this.showStep(2);
    }
  }

  async loadExistingProfile() {
    try {
      const result = await chrome.storage.local.get(['userProfile', 'settings']);
      if (result.userProfile) {
        this.populateFormWithProfile(result.userProfile);
      }
      if (result.settings && result.settings.aiProvider) {
        this.selectedProvider = result.settings.aiProvider;
      }
    } catch (error) {
      console.error('Error loading existing profile:', error);
    }
  }

  populateFormWithProfile(profile) {
    // Personal Information
    if (profile.personal) {
      this.setFieldValue('firstName', profile.personal.first_name);
      this.setFieldValue('lastName', profile.personal.last_name);
      this.setFieldValue('city', profile.personal.city);
      this.setFieldValue('state', profile.personal.state);
      this.setFieldValue('workAuth', profile.personal.work_authorization);
    }

    // Contact Information
    if (profile.contact) {
      this.setFieldValue('email', profile.contact.email);
      this.setFieldValue('phone', profile.contact.phone);
      this.setFieldValue('linkedinUrl', profile.contact.linkedin_url);
      this.setFieldValue('githubUrl', profile.contact.github_url);
    }

    // Professional Information
    if (profile.professional) {
      this.setFieldValue('currentPosition', profile.professional.current_position);
      this.setFieldValue('currentCompany', profile.professional.current_company);
      this.setFieldValue('experience', profile.professional.years_of_experience?.toString());
      this.setFieldValue('remotePreference', profile.professional.remote_preference);
    }

    // Skills
    if (profile.technical_skills && Array.isArray(profile.technical_skills)) {
      this.setFieldValue('skills', profile.technical_skills.join(', '));
    }
  }

  setFieldValue(fieldId, value) {
    const field = document.getElementById(fieldId);
    if (field && value) {
      field.value = value;
    }
  }

  setupEventListeners() {
    // AI provider selection
    document.querySelectorAll('.provider-option').forEach(option => {
      option.addEventListener('click', () => {
        this.selectProvider(option.dataset.provider);
      });
    });

    // Form validation
    const form = document.getElementById('profileForm');
    if (form) {
      form.addEventListener('input', () => {
        this.validateForm();
      });
    }

    // Auto-format phone number
    const phoneField = document.getElementById('phone');
    if (phoneField) {
      phoneField.addEventListener('input', (e) => {
        this.formatPhoneNumber(e.target);
      });
    }

    // Auto-format URLs
    const urlFields = ['linkedinUrl', 'githubUrl'];
    urlFields.forEach(fieldId => {
      const field = document.getElementById(fieldId);
      if (field) {
        field.addEventListener('blur', (e) => {
          this.formatUrl(e.target);
        });
      }
    });
  }

  populateDefaultData() {
    // Pre-populate with Sanket's data as example
    if (!this.isEditMode) {
      this.setFieldValue('firstName', 'Sanket');
      this.setFieldValue('lastName', 'Muchhala');
      this.setFieldValue('email', 'sanketmuchhala1@gmail.com');
      this.setFieldValue('city', 'San Francisco');
      this.setFieldValue('state', 'CA');
      this.setFieldValue('workAuth', 'citizen');
      this.setFieldValue('currentPosition', 'Software Engineer');
      this.setFieldValue('experience', '3');
      this.setFieldValue('remotePreference', 'hybrid');
      this.setFieldValue('skills', 'JavaScript, Python, React, Node.js, TypeScript, AWS');
      this.setFieldValue('linkedinUrl', 'linkedin.com/in/sanketmuchhala');
      this.setFieldValue('githubUrl', 'github.com/sanketmuchhala');
    }
  }

  formatPhoneNumber(field) {
    let value = field.value.replace(/\D/g, '');
    if (value.length >= 10) {
      value = value.substring(0, 10);
      value = value.replace(/(\d{3})(\d{3})(\d{4})/, '($1) $2-$3');
    } else if (value.length >= 6) {
      value = value.replace(/(\d{3})(\d{3})/, '($1) $2-');
    } else if (value.length >= 3) {
      value = value.replace(/(\d{3})/, '($1) ');
    }
    field.value = value;
  }

  formatUrl(field) {
    let value = field.value.trim();
    if (value && !value.startsWith('http')) {
      field.value = `https://${value}`;
    }
  }

  selectProvider(provider) {
    this.selectedProvider = provider;
    
    // Update UI
    document.querySelectorAll('.provider-option').forEach(option => {
      option.classList.remove('selected');
    });
    document.querySelector(`[data-provider="${provider}"]`).classList.add('selected');

    // Show/hide API key section
    const apiKeySection = document.getElementById('apiKeySection');
    const apiKeyHelpLink = document.getElementById('apiKeyHelpLink');
    
    if (provider === 'free') {
      apiKeySection.style.display = 'none';
    } else {
      apiKeySection.style.display = 'block';
      
      // Set help link based on provider
      const helpUrls = {
        deepseek: 'https://platform.deepseek.com/api-keys',
        gemini: 'https://makersuite.google.com/app/apikey'
      };
      
      if (apiKeyHelpLink && helpUrls[provider]) {
        apiKeyHelpLink.href = helpUrls[provider];
      }
    }
  }

  validateForm() {
    const requiredFields = ['firstName', 'lastName', 'email', 'phone'];
    let isValid = true;

    requiredFields.forEach(fieldId => {
      const field = document.getElementById(fieldId);
      if (!field || !field.value.trim()) {
        isValid = false;
      }
    });

    // Email validation
    const emailField = document.getElementById('email');
    if (emailField && emailField.value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(emailField.value)) {
        isValid = false;
      }
    }

    return isValid;
  }

  collectFormData() {
    this.profileData = {
      personal: {
        first_name: document.getElementById('firstName').value.trim(),
        last_name: document.getElementById('lastName').value.trim(),
        city: document.getElementById('city').value.trim(),
        state: document.getElementById('state').value.trim(),
        work_authorization: document.getElementById('workAuth').value
      },
      contact: {
        email: document.getElementById('email').value.trim(),
        phone: document.getElementById('phone').value.trim(),
        linkedin_url: document.getElementById('linkedinUrl').value.trim(),
        github_url: document.getElementById('githubUrl').value.trim()
      },
      professional: {
        current_position: document.getElementById('currentPosition').value.trim(),
        current_company: document.getElementById('currentCompany').value.trim(),
        years_of_experience: parseInt(document.getElementById('experience').value) || 0,
        remote_preference: document.getElementById('remotePreference').value
      },
      technical_skills: this.parseSkills(document.getElementById('skills').value)
    };

    return this.profileData;
  }

  parseSkills(skillsText) {
    if (!skillsText) return [];
    return skillsText
      .split(',')
      .map(skill => skill.trim())
      .filter(skill => skill.length > 0);
  }

  nextStep() {
    if (this.currentStep < this.maxSteps) {
      this.currentStep++;
      this.updateProgressBar();
      this.showStep(this.currentStep);
      this.trackStepProgress();
    }
  }

  previousStep() {
    if (this.currentStep > 1) {
      this.currentStep--;
      this.updateProgressBar();
      this.showStep(this.currentStep);
    }
  }

  validateAndNextStep() {
    if (this.currentStep === 2) {
      if (!this.validateForm()) {
        this.showToast('Please fill in all required fields correctly', 'error');
        return;
      }
      this.collectFormData();
    }
    this.nextStep();
  }

  async finalizeSetup() {
    try {
      // Validate API key if premium provider selected
      if (this.selectedProvider !== 'free') {
        const apiKey = document.getElementById('apiKey').value.trim();
        if (!apiKey) {
          this.showToast('Please enter your API key', 'error');
          return;
        }
        
        // Test API key
        this.showLoading('Testing API connection...');
        const isValid = await this.testApiKey(this.selectedProvider, apiKey);
        this.hideLoading();
        
        if (!isValid) {
          this.showToast('Invalid API key. Please check and try again.', 'error');
          return;
        }
      }

      // Save profile and settings
      await this.saveProfile();
      await this.saveSettings();
      
      this.nextStep();
      this.updateSummary();
    } catch (error) {
      this.hideLoading();
      console.error('Setup finalization error:', error);
      this.showToast('Setup failed. Please try again.', 'error');
    }
  }

  async testApiKey(provider, apiKey) {
    // Simple API key validation
    try {
      if (provider === 'deepseek') {
        // Test DeepSeek API
        const response = await fetch('https://api.deepseek.com/v1/models', {
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
          }
        });
        return response.ok;
      } else if (provider === 'gemini') {
        // Test Gemini API
        const response = await fetch(`https://generativelanguage.googleapis.com/v1/models?key=${apiKey}`);
        return response.ok;
      }
    } catch (error) {
      console.error('API key test error:', error);
      return false;
    }
    return true;
  }

  async saveProfile() {
    try {
      await chrome.storage.local.set({
        userProfile: this.profileData
      });
    } catch (error) {
      console.error('Error saving profile:', error);
      throw error;
    }
  }

  async saveSettings() {
    const settings = {
      aiProvider: this.selectedProvider,
      apiKeys: {}
    };

    if (this.selectedProvider !== 'free') {
      const apiKey = document.getElementById('apiKey').value.trim();
      settings.apiKeys[this.selectedProvider] = apiKey;
    }

    try {
      await chrome.storage.local.set({ settings });
    } catch (error) {
      console.error('Error saving settings:', error);
      throw error;
    }
  }

  updateProgressBar() {
    document.querySelectorAll('.progress-step').forEach((step, index) => {
      const stepNumber = index + 1;
      step.classList.remove('active', 'completed');
      
      if (stepNumber === this.currentStep) {
        step.classList.add('active');
      } else if (stepNumber < this.currentStep) {
        step.classList.add('completed');
      }
    });
  }

  showStep(stepNumber) {
    document.querySelectorAll('.step-panel').forEach(panel => {
      panel.classList.remove('active');
    });
    
    const targetPanel = document.getElementById(`step-${stepNumber}`);
    if (targetPanel) {
      targetPanel.classList.add('active');
    }
  }

  updateSummary() {
    const profileSummary = document.getElementById('profileSummary');
    const aiProviderSummary = document.getElementById('aiProviderSummary');
    
    if (profileSummary) {
      const name = `${this.profileData.personal.first_name} ${this.profileData.personal.last_name}`.trim();
      profileSummary.textContent = `${name} - ${this.profileData.contact.email}`;
    }
    
    if (aiProviderSummary) {
      const providerNames = {
        free: 'Free (Built-in)',
        deepseek: 'DeepSeek AI',
        gemini: 'Google Gemini'
      };
      aiProviderSummary.textContent = providerNames[this.selectedProvider] || 'Unknown';
    }
  }

  trackStepProgress() {
    // Track setup progress for analytics (optional)
    if (typeof gtag !== 'undefined') {
      gtag('event', 'setup_step_completed', {
        step: this.currentStep - 1
      });
    }
  }

  showLoading(message = 'Loading...') {
    const loadingOverlay = document.createElement('div');
    loadingOverlay.id = 'loadingOverlay';
    loadingOverlay.innerHTML = `
      <div style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(255,255,255,0.9); display: flex; align-items: center; justify-content: center; z-index: 10000;">
        <div style="text-align: center;">
          <div style="width: 32px; height: 32px; border: 3px solid #e5e7eb; border-top: 3px solid #4f46e5; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 16px;"></div>
          <p style="color: #6b7280; font-size: 14px;">${message}</p>
        </div>
      </div>
      <style>@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }</style>
    `;
    document.body.appendChild(loadingOverlay);
  }

  hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
      loadingOverlay.remove();
    }
  }

  showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: ${type === 'error' ? '#dc2626' : type === 'success' ? '#059669' : '#4f46e5'};
      color: white;
      padding: 12px 20px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      z-index: 10001;
      animation: slideUp 0.3s ease;
    `;
    toast.textContent = message;
    
    const style = document.createElement('style');
    style.textContent = '@keyframes slideUp { from { transform: translateY(100%); opacity: 0; } to { transform: translateY(0); opacity: 1; } }';
    document.head.appendChild(style);
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.remove();
      style.remove();
    }, 4000);
  }

  openTestSite() {
    chrome.tabs.create({
      url: 'https://jobs.linkedin.com'
    });
  }

  completeSetup() {
    // Close setup and potentially open success page
    if (this.isEditMode) {
      // Just close the tab
      window.close();
    } else {
      // Show completion message and close
      this.showToast('Setup completed successfully!', 'success');
      setTimeout(() => {
        window.close();
      }, 2000);
    }
  }
}

// Global functions for button clicks (referenced in HTML)
let setupWizard;

window.nextStep = function() {
  setupWizard.nextStep();
};

window.previousStep = function() {
  setupWizard.previousStep();
};

window.validateAndNextStep = function() {
  setupWizard.validateAndNextStep();
};

window.finalizeSetup = function() {
  setupWizard.finalizeSetup();
};

window.openTestSite = function() {
  setupWizard.openTestSite();
};

window.completeSetup = function() {
  setupWizard.completeSetup();
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  setupWizard = new SetupWizard();
});