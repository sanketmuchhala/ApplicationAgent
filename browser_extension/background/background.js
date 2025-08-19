// JobApplicationAgent - Background Service Worker
class BackgroundService {
  constructor() {
    this.apiManager = null;
    this.init();
  }

  async init() {
    console.log('JobApplicationAgent background service started');
    this.setupEventListeners();
    this.initializeApiManager();
  }

  setupEventListeners() {
    // Handle extension install/update
    chrome.runtime.onInstalled.addListener((details) => {
      this.handleInstall(details);
    });

    // Handle messages from content scripts and popup
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      this.handleMessage(message, sender, sendResponse);
      return true; // Indicate async response
    });

    // Handle tab updates for form detection
    chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
      this.handleTabUpdate(tabId, changeInfo, tab);
    });

    // Handle alarm events for periodic tasks
    chrome.alarms.onAlarm.addListener((alarm) => {
      this.handleAlarm(alarm);
    });
  }

  async initializeApiManager() {
    try {
      const { APIManager } = await import('./api_manager.js');
      this.apiManager = new APIManager();
      console.log('API Manager initialized');
    } catch (error) {
      console.error('Failed to initialize API Manager:', error);
    }
  }

  async handleInstall(details) {
    if (details.reason === 'install') {
      console.log('Extension installed');
      
      // Set up default settings
      await this.setDefaultSettings();
      
      // Open setup page
      chrome.tabs.create({
        url: chrome.runtime.getURL('popup/setup.html')
      });

      // Set up periodic cleanup alarm
      chrome.alarms.create('cleanup', { 
        delayInMinutes: 1,
        periodInMinutes: 1440 // Daily cleanup
      });

    } else if (details.reason === 'update') {
      console.log('Extension updated from', details.previousVersion);
      await this.handleUpdate(details.previousVersion);
    }
  }

  async setDefaultSettings() {
    try {
      const defaultSettings = {
        aiProvider: 'free',
        apiKeys: {},
        enableNotifications: true,
        autoDetectForms: true,
        fillDelay: 100,
        confidenceThreshold: 70,
        maxFormsPerDay: 50
      };

      await chrome.storage.local.set({
        settings: defaultSettings,
        usageStats: {
          formssFilled: 0,
          monthlyCost: 0,
          lastReset: new Date().toISOString()
        }
      });

      console.log('Default settings initialized');
    } catch (error) {
      console.error('Error setting default settings:', error);
    }
  }

  async handleUpdate(previousVersion) {
    try {
      // Migration logic for updates
      const result = await chrome.storage.local.get(['settings', 'usageStats']);
      
      // Add any new settings that don't exist
      const updatedSettings = {
        ...result.settings,
        maxFormsPerDay: result.settings?.maxFormsPerDay || 50,
        confidenceThreshold: result.settings?.confidenceThreshold || 70
      };

      await chrome.storage.local.set({ settings: updatedSettings });
      
      console.log(`Updated from ${previousVersion} to current version`);
    } catch (error) {
      console.error('Error during update:', error);
    }
  }

  async handleMessage(message, sender, sendResponse) {
    try {
      switch (message.action) {
        case 'analyzeFields':
          const analysisResult = await this.handleFieldAnalysis(message);
          sendResponse(analysisResult);
          break;

        case 'generateResponse':
          const responseResult = await this.handleResponseGeneration(message);
          sendResponse(responseResult);
          break;

        case 'testApiKey':
          const testResult = await this.handleApiKeyTest(message);
          sendResponse(testResult);
          break;

        case 'getUsageStats':
          const stats = await this.getUsageStatistics();
          sendResponse(stats);
          break;

        case 'recordUsage':
          await this.recordUsage(message.usage);
          sendResponse({ success: true });
          break;

        case 'checkBudget':
          const budgetStatus = await this.checkBudget();
          sendResponse(budgetStatus);
          break;

        case 'exportData':
          const exportResult = await this.handleDataExport(message);
          sendResponse(exportResult);
          break;

        default:
          sendResponse({ success: false, error: 'Unknown action' });
      }
    } catch (error) {
      console.error('Message handling error:', error);
      sendResponse({ success: false, error: error.message });
    }
  }

  async handleFieldAnalysis(message) {
    if (!this.apiManager) {
      return { 
        success: false, 
        error: 'AI service not available' 
      };
    }

    try {
      const result = await this.apiManager.analyzeFields(
        message.fields,
        message.profile,
        message.context
      );

      // Record usage
      await this.recordUsage({
        operation: 'field_analysis',
        provider: result.provider,
        tokensUsed: result.tokensUsed || 0,
        cost: result.cost || 0
      });

      return result;
    } catch (error) {
      console.error('Field analysis error:', error);
      return { success: false, error: error.message };
    }
  }

  async handleResponseGeneration(message) {
    if (!this.apiManager) {
      return { 
        success: false, 
        error: 'AI service not available' 
      };
    }

    try {
      const result = await this.apiManager.generateResponse(
        message.fieldInfo,
        message.profile,
        message.context
      );

      // Record usage
      await this.recordUsage({
        operation: 'response_generation',
        provider: result.provider,
        tokensUsed: result.tokensUsed || 0,
        cost: result.cost || 0
      });

      return result;
    } catch (error) {
      console.error('Response generation error:', error);
      return { success: false, error: error.message };
    }
  }

  async handleApiKeyTest(message) {
    if (!this.apiManager) {
      return { success: false, error: 'API manager not available' };
    }

    try {
      const isValid = await this.apiManager.testApiKey(
        message.provider,
        message.apiKey
      );

      return { success: true, valid: isValid };
    } catch (error) {
      console.error('API key test error:', error);
      return { success: false, error: error.message };
    }
  }

  async handleDataExport(message) {
    try {
      const result = await chrome.storage.local.get(null);
      
      const exportData = {
        version: chrome.runtime.getManifest().version,
        exportDate: new Date().toISOString(),
        profile: result.userProfile,
        settings: result.settings,
        usageStats: result.usageStats
      };

      if (message.format === 'json') {
        return {
          success: true,
          data: JSON.stringify(exportData, null, 2),
          filename: `jobagent_backup_${new Date().toISOString().split('T')[0]}.json`
        };
      }

      return { success: false, error: 'Unsupported export format' };
    } catch (error) {
      console.error('Data export error:', error);
      return { success: false, error: error.message };
    }
  }

  async handleTabUpdate(tabId, changeInfo, tab) {
    // Only process when page is completely loaded
    if (changeInfo.status !== 'complete' || !tab.url) return;

    // Skip non-http(s) URLs
    if (!tab.url.startsWith('http')) return;

    try {
      // Check if this is a potential job site
      if (this.isJobSite(tab.url)) {
        // Inject content scripts if not already injected
        await this.injectContentScripts(tabId);
        
        // Send notification to check for forms after a delay
        setTimeout(async () => {
          try {
            await chrome.tabs.sendMessage(tabId, {
              action: 'scanForForms'
            });
          } catch (error) {
            // Tab might be closed or navigated away, ignore error
          }
        }, 2000);
      }
    } catch (error) {
      console.error('Tab update handling error:', error);
    }
  }

  isJobSite(url) {
    const jobSitePatterns = [
      'linkedin.com/jobs',
      'indeed.com',
      'glassdoor.com',
      'monster.com',
      'ziprecruiter.com',
      'workday.com',
      'greenhouse.io',
      'lever.co',
      'bamboohr.com',
      'smartrecruiters.com',
      'careers',
      'jobs',
      'apply'
    ];

    const urlLower = url.toLowerCase();
    return jobSitePatterns.some(pattern => urlLower.includes(pattern));
  }

  async injectContentScripts(tabId) {
    try {
      // Check if scripts are already injected
      const response = await chrome.tabs.sendMessage(tabId, { action: 'ping' });
      if (response && response.pong) {
        return; // Scripts already injected
      }
    } catch (error) {
      // Scripts not injected, proceed with injection
    }

    try {
      await chrome.scripting.executeScript({
        target: { tabId },
        files: [
          'lib/semantic_matcher.js',
          'lib/profile_manager.js',
          'content_scripts/form_detector.js',
          'content_scripts/form_filler.js',
          'content_scripts/ui_overlay.js'
        ]
      });

      await chrome.scripting.insertCSS({
        target: { tabId },
        files: ['content_scripts/overlay.css']
      });

      console.log('Content scripts injected successfully');
    } catch (error) {
      console.error('Script injection error:', error);
    }
  }

  async handleAlarm(alarm) {
    switch (alarm.name) {
      case 'cleanup':
        await this.performCleanup();
        break;
      case 'usage_reset':
        await this.resetUsageStats();
        break;
      default:
        console.log('Unknown alarm:', alarm.name);
    }
  }

  async performCleanup() {
    try {
      // Clean up old usage data (keep only last 30 days)
      const result = await chrome.storage.local.get(['usageHistory']);
      if (result.usageHistory) {
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
        
        const cleanedHistory = result.usageHistory.filter(entry => 
          new Date(entry.timestamp) > thirtyDaysAgo
        );

        await chrome.storage.local.set({ usageHistory: cleanedHistory });
        console.log('Performed cleanup of old usage data');
      }
    } catch (error) {
      console.error('Cleanup error:', error);
    }
  }

  async resetUsageStats() {
    try {
      const result = await chrome.storage.local.get(['usageStats']);
      const currentStats = result.usageStats || {};
      
      // Reset monthly counters
      currentStats.monthlyCost = 0;
      currentStats.monthlyForms = 0;
      currentStats.lastReset = new Date().toISOString();

      await chrome.storage.local.set({ usageStats: currentStats });
      console.log('Monthly usage stats reset');
    } catch (error) {
      console.error('Usage reset error:', error);
    }
  }

  async recordUsage(usage) {
    try {
      const result = await chrome.storage.local.get(['usageStats', 'usageHistory']);
      const stats = result.usageStats || {
        formssFilled: 0,
        monthlyCost: 0,
        monthlyForms: 0,
        totalForms: 0,
        totalCost: 0,
        lastReset: new Date().toISOString()
      };

      const history = result.usageHistory || [];

      // Update stats
      stats.totalForms++;
      stats.monthlyForms = (stats.monthlyForms || 0) + 1;
      stats.totalCost += usage.cost || 0;
      stats.monthlyCost += usage.cost || 0;

      if (usage.operation === 'form_fill') {
        stats.formssFilled++;
      }

      // Add to history
      history.push({
        ...usage,
        timestamp: new Date().toISOString()
      });

      // Keep only last 1000 entries
      if (history.length > 1000) {
        history.splice(0, history.length - 1000);
      }

      await chrome.storage.local.set({
        usageStats: stats,
        usageHistory: history
      });

    } catch (error) {
      console.error('Usage recording error:', error);
    }
  }

  async getUsageStatistics() {
    try {
      const result = await chrome.storage.local.get(['usageStats', 'usageHistory', 'settings']);
      const stats = result.usageStats || {};
      const history = result.usageHistory || [];
      const settings = result.settings || {};

      // Calculate additional metrics
      const today = new Date().toDateString();
      const todayUsage = history.filter(entry => 
        new Date(entry.timestamp).toDateString() === today
      );

      return {
        success: true,
        stats: {
          ...stats,
          todayForms: todayUsage.filter(u => u.operation === 'form_fill').length,
          todayCost: todayUsage.reduce((sum, u) => sum + (u.cost || 0), 0),
          averageFormsPerDay: this.calculateAverageFormsPerDay(history),
          remainingBudget: this.calculateRemainingBudget(stats, settings)
        }
      };
    } catch (error) {
      console.error('Usage stats error:', error);
      return { success: false, error: error.message };
    }
  }

  calculateAverageFormsPerDay(history) {
    if (history.length === 0) return 0;

    const formFills = history.filter(entry => entry.operation === 'form_fill');
    if (formFills.length === 0) return 0;

    const oldestEntry = new Date(formFills[0].timestamp);
    const daysDiff = Math.ceil((Date.now() - oldestEntry.getTime()) / (1000 * 60 * 60 * 24));
    
    return Math.round((formFills.length / Math.max(daysDiff, 1)) * 100) / 100;
  }

  calculateRemainingBudget(stats, settings) {
    const monthlyBudget = settings.monthlyBudget || 10; // Default $10/month
    const used = stats.monthlyCost || 0;
    return Math.max(0, monthlyBudget - used);
  }

  async checkBudget() {
    try {
      const result = await chrome.storage.local.get(['usageStats', 'settings']);
      const stats = result.usageStats || {};
      const settings = result.settings || {};

      const monthlyBudget = settings.monthlyBudget || 10;
      const used = stats.monthlyCost || 0;
      const percentage = monthlyBudget > 0 ? (used / monthlyBudget) * 100 : 0;

      return {
        success: true,
        budget: {
          total: monthlyBudget,
          used: used,
          remaining: Math.max(0, monthlyBudget - used),
          percentage: Math.min(percentage, 100),
          exceeded: used > monthlyBudget
        }
      };
    } catch (error) {
      console.error('Budget check error:', error);
      return { success: false, error: error.message };
    }
  }

  // Notification helpers
  async showNotification(title, message, type = 'basic') {
    if (!chrome.notifications) return;

    try {
      const settings = await chrome.storage.local.get(['settings']);
      if (!settings.settings?.enableNotifications) return;

      await chrome.notifications.create({
        type: type,
        iconUrl: 'assets/icons/icon-48.png',
        title: title,
        message: message
      });
    } catch (error) {
      console.error('Notification error:', error);
    }
  }
}

// Initialize the background service
const backgroundService = new BackgroundService();

// Handle unhandled promise rejections
self.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason);
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = BackgroundService;
}