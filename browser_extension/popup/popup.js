// JobApplicationAgent - Popup JavaScript
class JobApplicationPopup {
  constructor() {
    this.currentScreen = 'no-form';
    this.profile = null;
    this.detectedFields = [];
    this.init();
  }

  async init() {
    await this.loadProfile();
    await this.checkCurrentPage();
    this.setupEventListeners();
    this.updateUI();
  }

  async loadProfile() {
    try {
      const result = await chrome.storage.local.get(['userProfile', 'settings']);
      this.profile = result.userProfile;
      this.settings = result.settings || {
        aiProvider: 'free',
        apiKeys: {}
      };
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  }

  async checkCurrentPage() {
    try {
      // Get current tab
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      // Check if form is detected on current page
      const results = await chrome.tabs.sendMessage(tab.id, { 
        action: 'checkForForms' 
      });
      
      if (results && results.formsDetected > 0) {
        this.currentScreen = 'form-detected';
        this.detectedFields = results.fields || [];
        this.updateFormInfo(results);
      } else {
        this.currentScreen = this.profile ? 'no-form' : 'welcome';
      }
    } catch (error) {
      console.error('Error checking current page:', error);
      this.currentScreen = this.profile ? 'no-form' : 'welcome';
    }
  }

  setupEventListeners() {
    // Welcome screen
    const startSetupBtn = document.getElementById('startSetupBtn');
    if (startSetupBtn) {
      startSetupBtn.addEventListener('click', () => this.startSetup());
    }

    // Form detected screen
    const analyzeFormBtn = document.getElementById('analyzeFormBtn');
    if (analyzeFormBtn) {
      analyzeFormBtn.addEventListener('click', () => this.analyzeForm());
    }

    const quickFillBtn = document.getElementById('quickFillBtn');
    if (quickFillBtn) {
      quickFillBtn.addEventListener('click', () => this.quickFill());
    }

    const fillFormBtn = document.getElementById('fillFormBtn');
    if (fillFormBtn) {
      fillFormBtn.addEventListener('click', () => this.fillForm());
    }

    // No form screen
    const scanPageBtn = document.getElementById('scanPageBtn');
    if (scanPageBtn) {
      scanPageBtn.addEventListener('click', () => this.scanCurrentPage());
    }

    // Footer buttons
    const settingsBtn = document.getElementById('settingsBtn');
    if (settingsBtn) {
      settingsBtn.addEventListener('click', () => this.showSettings());
    }

    const helpBtn = document.getElementById('helpBtn');
    if (helpBtn) {
      helpBtn.addEventListener('click', () => this.showHelp());
    }

    const profileBtn = document.getElementById('profileBtn');
    if (profileBtn) {
      profileBtn.addEventListener('click', () => this.editProfile());
    }

    // Settings screen
    const backBtn = document.getElementById('backBtn');
    if (backBtn) {
      backBtn.addEventListener('click', () => this.goBack());
    }

    const editProfileBtn = document.getElementById('editProfileBtn');
    if (editProfileBtn) {
      editProfileBtn.addEventListener('click', () => this.editProfile());
    }

    // AI Provider selection
    const aiProviderSelect = document.getElementById('aiProviderSelect');
    if (aiProviderSelect) {
      aiProviderSelect.addEventListener('change', (e) => this.changeAIProvider(e.target.value));
    }
  }

  updateUI() {
    // Hide all screens
    const screens = document.querySelectorAll('.screen');
    screens.forEach(screen => screen.style.display = 'none');

    // Show current screen
    const currentScreenElement = this.getScreenElement(this.currentScreen);
    if (currentScreenElement) {
      currentScreenElement.style.display = 'block';
    }

    // Update status indicator
    this.updateStatusIndicator();

    // Update profile info in settings
    this.updateProfileInfo();
  }

  getScreenElement(screenName) {
    const screenMap = {
      'welcome': document.getElementById('welcomeScreen'),
      'form-detected': document.getElementById('formDetectedScreen'),
      'no-form': document.getElementById('noFormScreen'),
      'settings': document.getElementById('settingsScreen')
    };
    return screenMap[screenName];
  }

  updateStatusIndicator() {
    const indicator = document.getElementById('statusIndicator');
    const statusDot = indicator.querySelector('.status-dot');
    const statusText = indicator.querySelector('.status-text');

    if (this.profile && this.settings.aiProvider !== 'free') {
      statusDot.className = 'status-dot';
      statusText.textContent = 'Ready';
    } else if (this.profile) {
      statusDot.className = 'status-dot warning';
      statusText.textContent = 'Limited';
    } else {
      statusDot.className = 'status-dot error';
      statusText.textContent = 'Setup Needed';
    }
  }

  updateFormInfo(formData) {
    const formDetails = document.getElementById('formDetails');
    const confidenceScore = document.getElementById('confidenceScore');
    
    if (formDetails) {
      formDetails.textContent = `Found ${formData.formsDetected} form(s) with ${formData.totalFields || 0} fields`;
    }

    if (confidenceScore) {
      const confidence = formData.confidence || 85;
      const fill = confidenceScore.querySelector('.confidence-fill');
      const value = confidenceScore.querySelector('.confidence-value');
      
      if (fill) fill.style.width = `${confidence}%`;
      if (value) value.textContent = `${confidence}%`;
    }
  }

  updateProfileInfo() {
    const profileName = document.getElementById('profileName');
    const profileEmail = document.getElementById('profileEmail');

    if (profileName && profileEmail) {
      if (this.profile) {
        profileName.textContent = `${this.profile.personal?.first_name || ''} ${this.profile.personal?.last_name || ''}`.trim() || 'Unknown User';
        profileEmail.textContent = this.profile.contact?.email || '';
      } else {
        profileName.textContent = 'No Profile';
        profileEmail.textContent = '';
      }
    }

    // Update AI provider select
    const aiProviderSelect = document.getElementById('aiProviderSelect');
    if (aiProviderSelect && this.settings) {
      aiProviderSelect.value = this.settings.aiProvider || 'free';
    }
  }

  async startSetup() {
    try {
      // Open setup page in new tab
      const setupUrl = chrome.runtime.getURL('popup/setup.html');
      await chrome.tabs.create({ url: setupUrl });
      window.close();
    } catch (error) {
      this.showToast('Error opening setup', 'error');
    }
  }

  async analyzeForm() {
    this.showLoading('Analyzing form fields...');

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      const results = await chrome.tabs.sendMessage(tab.id, {
        action: 'analyzeFields',
        profile: this.profile
      });

      this.hideLoading();

      if (results && results.success) {
        this.detectedFields = results.fieldMatches;
        this.showFieldMatches();
      } else {
        this.showToast('Failed to analyze form', 'error');
      }
    } catch (error) {
      this.hideLoading();
      this.showToast('Error analyzing form', 'error');
      console.error('Form analysis error:', error);
    }
  }

  showFieldMatches() {
    const fieldMatches = document.getElementById('fieldMatches');
    const fieldList = document.getElementById('fieldList');

    if (!fieldMatches || !fieldList) return;

    // Clear existing fields
    fieldList.innerHTML = '';

    // Add field matches
    this.detectedFields.forEach(field => {
      const fieldItem = document.createElement('div');
      fieldItem.className = 'field-item';
      
      const confidenceClass = field.confidence > 80 ? 'high' : field.confidence > 60 ? 'medium' : 'low';
      
      fieldItem.innerHTML = `
        <div class="field-info">
          <div class="field-label">${field.label}</div>
          <div class="field-value">${field.value || 'No matching data'}</div>
        </div>
        <div class="field-confidence ${confidenceClass}">${field.confidence}%</div>
      `;
      
      fieldList.appendChild(fieldItem);
    });

    fieldMatches.style.display = 'block';
  }

  async quickFill() {
    await this.fillForm(false); // Fill without preview
  }

  async fillForm(showPreview = true) {
    if (!this.profile) {
      this.showToast('Please create a profile first', 'warning');
      return;
    }

    this.showLoading('Filling form...');

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      const results = await chrome.tabs.sendMessage(tab.id, {
        action: 'fillForm',
        profile: this.profile,
        fields: this.detectedFields,
        preview: showPreview
      });

      this.hideLoading();

      if (results && results.success) {
        this.showToast(`Successfully filled ${results.filledCount} fields!`, 'success');
        
        // Update usage stats
        await this.updateUsageStats();
        
        // Close popup after short delay
        setTimeout(() => window.close(), 2000);
      } else {
        this.showToast('Failed to fill form', 'error');
      }
    } catch (error) {
      this.hideLoading();
      this.showToast('Error filling form', 'error');
      console.error('Form filling error:', error);
    }
  }

  async scanCurrentPage() {
    this.showLoading('Scanning page...');
    
    try {
      await this.checkCurrentPage();
      this.updateUI();
      this.hideLoading();
      
      if (this.currentScreen === 'form-detected') {
        this.showToast('Job application form found!', 'success');
      } else {
        this.showToast('No application forms detected', 'warning');
      }
    } catch (error) {
      this.hideLoading();
      this.showToast('Error scanning page', 'error');
    }
  }

  showSettings() {
    this.currentScreen = 'settings';
    this.updateUI();
  }

  goBack() {
    this.currentScreen = this.detectedFields.length > 0 ? 'form-detected' : 'no-form';
    this.updateUI();
  }

  async editProfile() {
    try {
      const setupUrl = chrome.runtime.getURL('popup/setup.html') + '?edit=true';
      await chrome.tabs.create({ url: setupUrl });
      window.close();
    } catch (error) {
      this.showToast('Error opening profile editor', 'error');
    }
  }

  async changeAIProvider(provider) {
    this.settings.aiProvider = provider;
    
    try {
      await chrome.storage.local.set({ settings: this.settings });
      this.updateStatusIndicator();
      this.showToast('AI provider updated', 'success');
    } catch (error) {
      this.showToast('Error updating AI provider', 'error');
    }
  }

  showHelp() {
    const helpUrl = 'https://github.com/sanket/JobApplicationAgent#usage';
    chrome.tabs.create({ url: helpUrl });
  }

  async updateUsageStats() {
    try {
      const result = await chrome.storage.local.get(['usageStats']);
      const stats = result.usageStats || { formssFilled: 0, monthlyCost: 0 };
      
      stats.formssFilled += 1;
      // Update monthly cost based on AI provider
      
      await chrome.storage.local.set({ usageStats: stats });
      
      // Update UI
      const formsFilledCount = document.getElementById('formsFilledCount');
      const monthlyCost = document.getElementById('monthlyCost');
      
      if (formsFilledCount) formsFilledCount.textContent = stats.formssFilled;
      if (monthlyCost) monthlyCost.textContent = `$${stats.monthlyCost.toFixed(2)}`;
      
    } catch (error) {
      console.error('Error updating usage stats:', error);
    }
  }

  showLoading(message = 'Processing...') {
    const overlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    
    if (overlay) overlay.style.display = 'flex';
    if (loadingText) loadingText.textContent = message;
  }

  hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.style.display = 'none';
  }

  showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastIcon = document.getElementById('toastIcon');
    const toastMessage = document.getElementById('toastMessage');
    
    if (!toast) return;

    // Set icon based on type
    const icons = {
      success: '✅',
      warning: '⚠️',
      error: '❌',
      info: 'ℹ️'
    };

    toast.className = `toast ${type}`;
    if (toastIcon) toastIcon.textContent = icons[type] || icons.info;
    if (toastMessage) toastMessage.textContent = message;
    
    toast.style.display = 'flex';
    
    // Auto hide after 3 seconds
    setTimeout(() => {
      toast.style.display = 'none';
    }, 3000);
  }
}

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new JobApplicationPopup();
});

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'formDetected') {
    // Form was detected, update UI
    const popup = window.jobApplicationPopup;
    if (popup) {
      popup.currentScreen = 'form-detected';
      popup.updateUI();
    }
  }
});