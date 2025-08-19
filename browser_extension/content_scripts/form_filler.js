// JobApplicationAgent - Form Filler Content Script
class FormFiller {
  constructor() {
    this.filledFields = [];
    this.animationDuration = 300;
    this.fillDelay = 100; // Delay between field fills for better UX
  }

  async fillForm(profile, fieldMatches, preview = false) {
    if (!profile || !fieldMatches || fieldMatches.length === 0) {
      return { success: false, error: 'No profile or field matches provided' };
    }

    try {
      this.filledFields = [];
      
      if (preview) {
        return await this.showPreview(fieldMatches);
      } else {
        return await this.performFormFill(fieldMatches);
      }
    } catch (error) {
      console.error('Form filling error:', error);
      return { success: false, error: error.message };
    }
  }

  async showPreview(fieldMatches) {
    // Create and show preview overlay
    const previewOverlay = this.createPreviewOverlay(fieldMatches);
    document.body.appendChild(previewOverlay);

    return new Promise((resolve) => {
      const fillBtn = previewOverlay.querySelector('.preview-fill-btn');
      const cancelBtn = previewOverlay.querySelector('.preview-cancel-btn');

      fillBtn.addEventListener('click', async () => {
        document.body.removeChild(previewOverlay);
        const result = await this.performFormFill(fieldMatches);
        resolve(result);
      });

      cancelBtn.addEventListener('click', () => {
        document.body.removeChild(previewOverlay);
        resolve({ success: false, cancelled: true });
      });
    });
  }

  createPreviewOverlay(fieldMatches) {
    const overlay = document.createElement('div');
    overlay.className = 'jaa-preview-overlay';
    overlay.innerHTML = `
      <div class="jaa-preview-modal">
        <div class="jaa-preview-header">
          <h3>🔍 Form Fill Preview</h3>
          <p>Review the data that will be filled:</p>
        </div>
        <div class="jaa-preview-content">
          ${fieldMatches.map(match => `
            <div class="jaa-preview-field">
              <div class="jaa-preview-field-label">${match.label}</div>
              <div class="jaa-preview-field-value">${match.value || '<empty>'}</div>
              <div class="jaa-preview-field-confidence">${match.confidence}%</div>
            </div>
          `).join('')}
        </div>
        <div class="jaa-preview-actions">
          <button class="jaa-btn jaa-btn-secondary preview-cancel-btn">Cancel</button>
          <button class="jaa-btn jaa-btn-primary preview-fill-btn">Fill Form</button>
        </div>
      </div>
    `;

    // Add styles if not already added
    this.addPreviewStyles();

    return overlay;
  }

  addPreviewStyles() {
    if (document.getElementById('jaa-preview-styles')) return;

    const styles = document.createElement('style');
    styles.id = 'jaa-preview-styles';
    styles.textContent = `
      .jaa-preview-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }

      .jaa-preview-modal {
        background: white;
        border-radius: 12px;
        max-width: 500px;
        max-height: 80vh;
        width: 90vw;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        overflow: hidden;
      }

      .jaa-preview-header {
        padding: 20px;
        background: linear-gradient(135deg, #4f46e5, #3730a3);
        color: white;
        text-align: center;
      }

      .jaa-preview-header h3 {
        margin: 0 0 8px 0;
        font-size: 18px;
        font-weight: 600;
      }

      .jaa-preview-header p {
        margin: 0;
        opacity: 0.9;
        font-size: 14px;
      }

      .jaa-preview-content {
        padding: 20px;
        max-height: 400px;
        overflow-y: auto;
      }

      .jaa-preview-field {
        display: flex;
        align-items: center;
        padding: 12px;
        margin-bottom: 8px;
        background: #f9fafb;
        border-radius: 8px;
        gap: 12px;
      }

      .jaa-preview-field-label {
        font-weight: 500;
        color: #374151;
        min-width: 120px;
        font-size: 13px;
      }

      .jaa-preview-field-value {
        flex: 1;
        color: #1f2937;
        font-size: 13px;
        word-break: break-word;
      }

      .jaa-preview-field-confidence {
        background: #10b981;
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 500;
        min-width: 45px;
        text-align: center;
      }

      .jaa-preview-actions {
        padding: 20px;
        display: flex;
        gap: 12px;
        justify-content: flex-end;
        border-top: 1px solid #e5e7eb;
      }

      .jaa-btn {
        padding: 10px 20px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 500;
        border: none;
        cursor: pointer;
        transition: all 0.2s;
      }

      .jaa-btn-primary {
        background: #4f46e5;
        color: white;
      }

      .jaa-btn-primary:hover {
        background: #3730a3;
      }

      .jaa-btn-secondary {
        background: #f3f4f6;
        color: #374151;
        border: 1px solid #d1d5db;
      }

      .jaa-btn-secondary:hover {
        background: #e5e7eb;
      }
    `;

    document.head.appendChild(styles);
  }

  async performFormFill(fieldMatches) {
    let filledCount = 0;
    let errors = [];

    // Add fill styles
    this.addFillStyles();

    for (const match of fieldMatches) {
      try {
        if (await this.fillField(match)) {
          filledCount++;
          await this.sleep(this.fillDelay);
        }
      } catch (error) {
        console.error(`Error filling field ${match.fieldId}:`, error);
        errors.push({
          field: match.label,
          error: error.message
        });
      }
    }

    // Show completion animation
    if (filledCount > 0) {
      this.showCompletionAnimation(filledCount);
    }

    return {
      success: filledCount > 0,
      filledCount,
      totalFields: fieldMatches.length,
      errors: errors.length > 0 ? errors : undefined
    };
  }

  async fillField(match) {
    const element = match.element;
    if (!element || !this.isElementVisible(element)) {
      return false;
    }

    // Scroll element into view
    element.scrollIntoView({ 
      behavior: 'smooth', 
      block: 'center',
      inline: 'nearest'
    });

    // Wait for scroll to complete
    await this.sleep(200);

    // Highlight field before filling
    this.highlightField(element, 'filling');

    const value = match.value?.toString() || '';
    let success = false;

    try {
      // Handle different field types
      switch (element.type?.toLowerCase() || element.tagName.toLowerCase()) {
        case 'text':
        case 'email':
        case 'tel':
        case 'url':
        case 'search':
          success = await this.fillTextInput(element, value);
          break;
        
        case 'textarea':
          success = await this.fillTextarea(element, value);
          break;
        
        case 'select':
        case 'select-one':
        case 'select-multiple':
          success = await this.fillSelect(element, value);
          break;
        
        case 'radio':
          success = await this.fillRadio(element, value);
          break;
        
        case 'checkbox':
          success = await this.fillCheckbox(element, value);
          break;
        
        case 'file':
          // File inputs require special handling - skip for now
          success = false;
          break;
        
        default:
          success = await this.fillGenericInput(element, value);
      }

      if (success) {
        this.highlightField(element, 'success');
        this.filledFields.push(match);
      } else {
        this.highlightField(element, 'error');
      }

    } catch (error) {
      console.error('Field fill error:', error);
      this.highlightField(element, 'error');
      success = false;
    }

    return success;
  }

  async fillTextInput(element, value) {
    if (!value) return false;

    // Clear existing value
    element.value = '';
    element.focus();

    // Simulate typing for better compatibility
    if (this.shouldSimulateTyping(element)) {
      return await this.simulateTyping(element, value);
    } else {
      element.value = value;
      this.triggerInputEvents(element);
      return true;
    }
  }

  async fillTextarea(element, value) {
    if (!value) return false;

    element.value = '';
    element.focus();
    
    if (this.shouldSimulateTyping(element)) {
      return await this.simulateTyping(element, value);
    } else {
      element.value = value;
      this.triggerInputEvents(element);
      return true;
    }
  }

  async fillSelect(element, value) {
    if (!value) return false;

    // Try to find matching option
    const options = Array.from(element.options);
    
    // First try exact match
    let matchingOption = options.find(option => 
      option.value.toLowerCase() === value.toLowerCase() ||
      option.text.toLowerCase() === value.toLowerCase()
    );

    // If no exact match, try partial match
    if (!matchingOption) {
      matchingOption = options.find(option => 
        option.text.toLowerCase().includes(value.toLowerCase()) ||
        value.toLowerCase().includes(option.text.toLowerCase())
      );
    }

    if (matchingOption) {
      element.value = matchingOption.value;
      element.selectedIndex = matchingOption.index;
      this.triggerChangeEvent(element);
      return true;
    }

    return false;
  }

  async fillRadio(element, value) {
    // For radio buttons, we need to find the right option in the group
    const name = element.name;
    if (!name) return false;

    const radioGroup = document.querySelectorAll(`input[name="${name}"][type="radio"]`);
    
    for (const radio of radioGroup) {
      const radioValue = radio.value.toLowerCase();
      const radioLabel = this.getRadioLabel(radio).toLowerCase();
      const targetValue = value.toLowerCase();

      if (radioValue === targetValue || 
          radioLabel.includes(targetValue) || 
          targetValue.includes(radioLabel)) {
        radio.checked = true;
        this.triggerChangeEvent(radio);
        return true;
      }
    }

    return false;
  }

  async fillCheckbox(element, value) {
    // Convert value to boolean
    const shouldCheck = this.valueToBoolean(value);
    
    if (element.checked !== shouldCheck) {
      element.checked = shouldCheck;
      this.triggerChangeEvent(element);
    }
    
    return true;
  }

  async fillGenericInput(element, value) {
    try {
      element.value = value;
      this.triggerInputEvents(element);
      return true;
    } catch (error) {
      return false;
    }
  }

  shouldSimulateTyping(element) {
    // Some modern forms require realistic typing simulation
    const classNames = element.className.toLowerCase();
    const reactDetected = window.React || document.querySelector('[data-reactroot]');
    
    return reactDetected || 
           classNames.includes('react') || 
           classNames.includes('vue') || 
           element.hasAttribute('data-testid');
  }

  async simulateTyping(element, value) {
    for (let i = 0; i < value.length; i++) {
      const char = value[i];
      element.value += char;
      
      // Trigger input event for each character
      element.dispatchEvent(new Event('input', { bubbles: true }));
      
      // Small delay between characters
      await this.sleep(20);
    }
    
    this.triggerInputEvents(element);
    return true;
  }

  triggerInputEvents(element) {
    // Trigger common events that forms expect
    const events = ['input', 'change', 'blur'];
    
    events.forEach(eventType => {
      element.dispatchEvent(new Event(eventType, { 
        bubbles: true, 
        cancelable: true 
      }));
    });
  }

  triggerChangeEvent(element) {
    element.dispatchEvent(new Event('change', { 
      bubbles: true, 
      cancelable: true 
    }));
  }

  getRadioLabel(radioElement) {
    // Try to find associated label
    if (radioElement.id) {
      const label = document.querySelector(`label[for="${radioElement.id}"]`);
      if (label) return label.textContent.trim();
    }

    // Try parent label
    const parentLabel = radioElement.closest('label');
    if (parentLabel) {
      return parentLabel.textContent.replace(radioElement.value || '', '').trim();
    }

    // Try nearby text
    const parent = radioElement.parentElement;
    if (parent) {
      const text = parent.textContent.replace(radioElement.value || '', '').trim();
      if (text.length < 100) return text;
    }

    return radioElement.value || '';
  }

  valueToBoolean(value) {
    if (typeof value === 'boolean') return value;
    if (typeof value === 'string') {
      const lowerValue = value.toLowerCase();
      return ['true', 'yes', '1', 'on', 'checked'].includes(lowerValue);
    }
    return Boolean(value);
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

  highlightField(element, state) {
    element.classList.remove('jaa-field-filling', 'jaa-field-success', 'jaa-field-error');
    
    switch (state) {
      case 'filling':
        element.classList.add('jaa-field-filling');
        break;
      case 'success':
        element.classList.add('jaa-field-success');
        setTimeout(() => element.classList.remove('jaa-field-success'), 2000);
        break;
      case 'error':
        element.classList.add('jaa-field-error');
        setTimeout(() => element.classList.remove('jaa-field-error'), 2000);
        break;
    }
  }

  addFillStyles() {
    if (document.getElementById('jaa-fill-styles')) return;

    const styles = document.createElement('style');
    styles.id = 'jaa-fill-styles';
    styles.textContent = `
      .jaa-field-filling {
        border: 2px solid #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        animation: jaa-pulse 1s infinite !important;
      }

      .jaa-field-success {
        border: 2px solid #10b981 !important;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1) !important;
        animation: jaa-success-flash 0.5s ease-out !important;
      }

      .jaa-field-error {
        border: 2px solid #ef4444 !important;
        box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1) !important;
        animation: jaa-error-shake 0.5s ease-out !important;
      }

      @keyframes jaa-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
      }

      @keyframes jaa-success-flash {
        0% { background-color: rgba(16, 185, 129, 0.1); }
        50% { background-color: rgba(16, 185, 129, 0.2); }
        100% { background-color: transparent; }
      }

      @keyframes jaa-error-shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
      }

      .jaa-completion-notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(16, 185, 129, 0.3);
        z-index: 10001;
        animation: jaa-slide-in 0.5s ease-out;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 500;
        font-size: 14px;
      }

      @keyframes jaa-slide-in {
        from {
          transform: translateX(100%);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }
    `;

    document.head.appendChild(styles);
  }

  showCompletionAnimation(filledCount) {
    const notification = document.createElement('div');
    notification.className = 'jaa-completion-notification';
    notification.innerHTML = `
      ✅ Successfully filled ${filledCount} field${filledCount > 1 ? 's' : ''}!
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 4000);
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Initialize and export
window.formFiller = new FormFiller();
window.FormFiller = FormFiller;