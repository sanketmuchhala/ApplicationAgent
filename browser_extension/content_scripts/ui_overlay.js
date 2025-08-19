// JobApplicationAgent - UI Overlay for Visual Feedback
class UIOverlay {
  constructor() {
    this.overlays = new Map();
    this.notifications = [];
    this.isActive = false;
    this.init();
  }

  init() {
    this.injectStyles();
    this.setupMessageListener();
  }

  injectStyles() {
    if (document.getElementById('jaa-overlay-styles')) return;

    const link = document.createElement('link');
    link.id = 'jaa-overlay-styles';
    link.rel = 'stylesheet';
    link.href = chrome.runtime.getURL('content_scripts/overlay.css');
    document.head.appendChild(link);
  }

  setupMessageListener() {
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      switch (message.action) {
        case 'showFieldHighlights':
          this.showFieldHighlights(message.fields);
          sendResponse({ success: true });
          break;
        case 'hideFieldHighlights':
          this.hideFieldHighlights();
          sendResponse({ success: true });
          break;
        case 'showFormDetectedBanner':
          this.showFormDetectedBanner(message.data);
          sendResponse({ success: true });
          break;
        case 'showFillProgress':
          this.showFillProgress(message.fields);
          sendResponse({ success: true });
          break;
        case 'updateFillProgress':
          this.updateFillProgress(message.fieldId, message.status);
          sendResponse({ success: true });
          break;
        case 'showCompletionNotification':
          this.showCompletionNotification(message.data);
          sendResponse({ success: true });
          break;
        default:
          sendResponse({ success: false, error: 'Unknown action' });
      }
    });
  }

  showFieldHighlights(fields) {
    this.hideFieldHighlights(); // Clear existing highlights

    fields.forEach(field => {
      if (field.element && this.isElementVisible(field.element)) {
        this.highlightField(field.element, field.confidence || 75);
      }
    });

    this.isActive = true;
  }

  highlightField(element, confidence) {
    // Create highlight overlay
    const overlay = document.createElement('div');
    overlay.className = 'jaa-field-highlight';
    
    // Set highlight color based on confidence
    let highlightClass = 'high-confidence';
    if (confidence < 60) {
      highlightClass = 'low-confidence';
    } else if (confidence < 80) {
      highlightClass = 'medium-confidence';
    }
    
    overlay.classList.add(highlightClass);

    // Position overlay over the element
    const rect = element.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

    overlay.style.cssText = `
      position: absolute;
      top: ${rect.top + scrollTop - 2}px;
      left: ${rect.left + scrollLeft - 2}px;
      width: ${rect.width + 4}px;
      height: ${rect.height + 4}px;
      z-index: 10000;
      pointer-events: none;
      border-radius: 4px;
    `;

    // Add confidence tooltip
    const tooltip = document.createElement('div');
    tooltip.className = 'jaa-confidence-tooltip';
    tooltip.textContent = `${confidence}%`;
    overlay.appendChild(tooltip);

    // Add to DOM
    document.body.appendChild(overlay);
    this.overlays.set(element, overlay);

    // Add highlight class to original element
    element.classList.add('jaa-highlighted-field');

    // Animate in
    requestAnimationFrame(() => {
      overlay.classList.add('visible');
    });
  }

  hideFieldHighlights() {
    // Remove all highlight overlays
    this.overlays.forEach((overlay, element) => {
      overlay.remove();
      element.classList.remove('jaa-highlighted-field');
    });
    this.overlays.clear();
    this.isActive = false;
  }

  showFormDetectedBanner(data) {
    // Remove existing banner
    this.hideFormDetectedBanner();

    const banner = document.createElement('div');
    banner.id = 'jaa-form-detected-banner';
    banner.className = 'jaa-banner jaa-form-detected';
    
    banner.innerHTML = `
      <div class="jaa-banner-content">
        <div class="jaa-banner-icon">🎯</div>
        <div class="jaa-banner-text">
          <div class="jaa-banner-title">Job Application Form Detected!</div>
          <div class="jaa-banner-subtitle">${data.fieldsCount || 0} fields found with ${data.confidence || 0}% confidence</div>
        </div>
        <div class="jaa-banner-actions">
          <button class="jaa-btn jaa-btn-primary" id="jaa-analyze-btn">
            <span class="jaa-btn-icon">🔍</span>
            Analyze & Fill
          </button>
          <button class="jaa-btn jaa-btn-secondary" id="jaa-dismiss-btn">
            <span class="jaa-btn-icon">✕</span>
          </button>
        </div>
      </div>
    `;

    // Add event listeners
    banner.querySelector('#jaa-analyze-btn').addEventListener('click', () => {
      this.handleAnalyzeClick();
    });

    banner.querySelector('#jaa-dismiss-btn').addEventListener('click', () => {
      this.hideFormDetectedBanner();
    });

    // Position banner
    banner.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 10001;
      animation: jaa-slide-in-right 0.3s ease-out;
    `;

    document.body.appendChild(banner);

    // Auto-hide after 10 seconds
    setTimeout(() => {
      this.hideFormDetectedBanner();
    }, 10000);
  }

  hideFormDetectedBanner() {
    const banner = document.getElementById('jaa-form-detected-banner');
    if (banner) {
      banner.remove();
    }
  }

  showFillProgress(fields) {
    // Remove existing progress overlay
    this.hideFillProgress();

    const overlay = document.createElement('div');
    overlay.id = 'jaa-fill-progress-overlay';
    overlay.className = 'jaa-progress-overlay';

    const totalFields = fields.length;
    let completedFields = 0;

    overlay.innerHTML = `
      <div class="jaa-progress-modal">
        <div class="jaa-progress-header">
          <div class="jaa-progress-icon">⚡</div>
          <h3>Filling Application Form</h3>
          <p>Please wait while we fill out your information...</p>
        </div>
        <div class="jaa-progress-content">
          <div class="jaa-progress-bar">
            <div class="jaa-progress-fill" style="width: 0%"></div>
          </div>
          <div class="jaa-progress-text">
            <span id="jaa-progress-current">0</span> of <span id="jaa-progress-total">${totalFields}</span> fields completed
          </div>
          <div class="jaa-field-list" id="jaa-field-progress-list">
            ${fields.map(field => `
              <div class="jaa-field-progress-item" data-field-id="${field.id}">
                <div class="jaa-field-status">⏳</div>
                <div class="jaa-field-name">${field.label || field.name || 'Unknown Field'}</div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    // Animate in
    requestAnimationFrame(() => {
      overlay.classList.add('visible');
    });
  }

  updateFillProgress(fieldId, status) {
    const overlay = document.getElementById('jaa-fill-progress-overlay');
    if (!overlay) return;

    const fieldItem = overlay.querySelector(`[data-field-id="${fieldId}"]`);
    if (!fieldItem) return;

    const statusIcon = fieldItem.querySelector('.jaa-field-status');
    const progressFill = overlay.querySelector('.jaa-progress-fill');
    const progressCurrent = overlay.querySelector('#jaa-progress-current');
    const progressTotal = overlay.querySelector('#jaa-progress-total');

    // Update field status
    switch (status) {
      case 'filling':
        statusIcon.textContent = '🔄';
        statusIcon.className = 'jaa-field-status filling';
        break;
      case 'completed':
        statusIcon.textContent = '✅';
        statusIcon.className = 'jaa-field-status completed';
        break;
      case 'error':
        statusIcon.textContent = '❌';
        statusIcon.className = 'jaa-field-status error';
        break;
    }

    // Update progress bar
    const completedCount = overlay.querySelectorAll('.jaa-field-status.completed').length;
    const totalCount = parseInt(progressTotal.textContent);
    const percentage = (completedCount / totalCount) * 100;

    progressFill.style.width = `${percentage}%`;
    progressCurrent.textContent = completedCount;

    // Hide overlay when completed
    if (completedCount === totalCount) {
      setTimeout(() => {
        this.hideFillProgress();
      }, 2000);
    }
  }

  hideFillProgress() {
    const overlay = document.getElementById('jaa-fill-progress-overlay');
    if (overlay) {
      overlay.classList.add('hiding');
      setTimeout(() => overlay.remove(), 300);
    }
  }

  showCompletionNotification(data) {
    const notification = document.createElement('div');
    notification.className = 'jaa-notification jaa-success-notification';
    
    const { filledCount, totalFields, errors } = data;
    const hasErrors = errors && errors.length > 0;

    notification.innerHTML = `
      <div class="jaa-notification-content">
        <div class="jaa-notification-icon">${hasErrors ? '⚠️' : '🎉'}</div>
        <div class="jaa-notification-text">
          <div class="jaa-notification-title">
            ${hasErrors ? 'Partially Completed!' : 'Form Filled Successfully!'}
          </div>
          <div class="jaa-notification-message">
            Filled ${filledCount} of ${totalFields} fields
            ${hasErrors ? ` (${errors.length} errors)` : ''}
          </div>
        </div>
        <button class="jaa-notification-close" onclick="this.parentElement.parentElement.remove()">✕</button>
      </div>
    `;

    // Position notification
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 10002;
      animation: jaa-slide-in-right 0.3s ease-out;
    `;

    document.body.appendChild(notification);
    this.notifications.push(notification);

    // Auto-hide after 5 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove();
        this.notifications = this.notifications.filter(n => n !== notification);
      }
    }, 5000);
  }

  showFloatingAssistant() {
    // Remove existing assistant
    this.hideFloatingAssistant();

    const assistant = document.createElement('div');
    assistant.id = 'jaa-floating-assistant';
    assistant.className = 'jaa-floating-assistant';

    assistant.innerHTML = `
      <div class="jaa-assistant-content">
        <div class="jaa-assistant-avatar">🤖</div>
        <div class="jaa-assistant-message">
          <p>I found a job application form on this page. Would you like me to help fill it out?</p>
          <div class="jaa-assistant-actions">
            <button class="jaa-btn jaa-btn-primary jaa-btn-sm" onclick="window.jaaUIOverlay.handleAnalyzeClick()">
              Yes, Fill Form
            </button>
            <button class="jaa-btn jaa-btn-secondary jaa-btn-sm" onclick="window.jaaUIOverlay.hideFloatingAssistant()">
              Not Now
            </button>
          </div>
        </div>
      </div>
    `;

    // Position in bottom right
    assistant.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      z-index: 10003;
      animation: jaa-bounce-in 0.5s ease-out;
    `;

    document.body.appendChild(assistant);
  }

  hideFloatingAssistant() {
    const assistant = document.getElementById('jaa-floating-assistant');
    if (assistant) {
      assistant.remove();
    }
  }

  handleAnalyzeClick() {
    // Hide banners and notifications
    this.hideFormDetectedBanner();
    this.hideFloatingAssistant();
    
    // Send message to popup to open
    chrome.runtime.sendMessage({
      action: 'openPopup',
      reason: 'form_analysis_requested'
    });
  }

  isElementVisible(element) {
    const rect = element.getBoundingClientRect();
    const style = window.getComputedStyle(element);
    
    return rect.width > 0 && 
           rect.height > 0 && 
           style.visibility !== 'hidden' && 
           style.display !== 'none' &&
           element.offsetParent !== null;
  }

  // Utility methods for animations
  fadeIn(element, duration = 300) {
    element.style.opacity = '0';
    element.style.transition = `opacity ${duration}ms ease`;
    
    requestAnimationFrame(() => {
      element.style.opacity = '1';
    });
  }

  fadeOut(element, duration = 300) {
    element.style.opacity = '1';
    element.style.transition = `opacity ${duration}ms ease`;
    
    requestAnimationFrame(() => {
      element.style.opacity = '0';
    });

    setTimeout(() => {
      if (element.parentNode) {
        element.remove();
      }
    }, duration);
  }

  slideInFromRight(element, duration = 300) {
    element.style.transform = 'translateX(100%)';
    element.style.transition = `transform ${duration}ms ease-out`;
    
    requestAnimationFrame(() => {
      element.style.transform = 'translateX(0)';
    });
  }

  // Clean up when page unloads
  cleanup() {
    this.hideFieldHighlights();
    this.hideFormDetectedBanner();
    this.hideFillProgress();
    this.hideFloatingAssistant();
    
    // Remove all notifications
    this.notifications.forEach(notification => {
      if (notification.parentNode) {
        notification.remove();
      }
    });
    this.notifications = [];
  }
}

// Initialize UI overlay
window.jaaUIOverlay = new UIOverlay();

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  window.jaaUIOverlay.cleanup();
});

// Export for other scripts
window.UIOverlay = UIOverlay;