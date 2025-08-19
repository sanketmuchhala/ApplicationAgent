// JobApplicationAgent - Form Detection Content Script
class JobFormDetector {
  constructor() {
    this.detectedForms = [];
    this.isJobApplicationSite = false;
    this.confidence = 0;
    this.init();
  }

  init() {
    this.detectJobApplicationContext();
    this.scanForJobApplicationForms();
    this.setupFormObserver();
    this.setupMessageListener();
  }

  detectJobApplicationContext() {
    const url = window.location.href.toLowerCase();
    const title = document.title.toLowerCase();
    const content = document.body.textContent.toLowerCase();

    // Job site detection patterns
    const jobSitePatterns = [
      // Major job sites
      'linkedin.com/jobs',
      'indeed.com',
      'glassdoor.com',
      'monster.com',
      'careerbuilder.com',
      'ziprecruiter.com',
      'simplyhired.com',
      
      // ATS systems
      'workday.com',
      'greenhouse.io',
      'lever.co',
      'bamboohr.com',
      'jobvite.com',
      'smartrecruiters.com',
      'icims.com',
      'successfactors.com',
      
      // Company career pages
      'careers',
      'jobs',
      'apply'
    ];

    // Job application keywords
    const jobKeywords = [
      'apply now',
      'job application',
      'application form',
      'submit application',
      'apply for position',
      'career opportunities',
      'join our team',
      'work with us',
      'employment application',
      'job opening'
    ];

    // Check URL patterns
    for (const pattern of jobSitePatterns) {
      if (url.includes(pattern)) {
        this.isJobApplicationSite = true;
        this.confidence += 30;
        break;
      }
    }

    // Check title and content for job-related keywords
    for (const keyword of jobKeywords) {
      if (title.includes(keyword) || content.includes(keyword)) {
        this.confidence += 10;
        if (this.confidence >= 20) {
          this.isJobApplicationSite = true;
        }
      }
    }

    // Cap confidence at 100
    this.confidence = Math.min(this.confidence, 100);
  }

  scanForJobApplicationForms() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach((form, index) => {
      if (this.isJobApplicationForm(form)) {
        const formData = this.analyzeForm(form, index);
        this.detectedForms.push(formData);
      }
    });

    // Also look for form-like containers (SPAs)
    const formContainers = this.detectSPAFormContainers();
    formContainers.forEach((container, index) => {
      const formData = this.analyzeFormContainer(container, forms.length + index);
      this.detectedForms.push(formData);
    });
  }

  isJobApplicationForm(form) {
    const formText = form.textContent.toLowerCase();
    const formHTML = form.innerHTML.toLowerCase();
    
    // Job application form indicators
    const jobFormPatterns = [
      'first name',
      'last name',
      'email',
      'phone',
      'resume',
      'cv',
      'cover letter',
      'experience',
      'education',
      'skills',
      'salary',
      'availability',
      'work authorization',
      'apply',
      'submit application'
    ];

    // Personal information patterns
    const personalInfoPatterns = [
      'personal information',
      'contact information',
      'basic information',
      'applicant information',
      'your details'
    ];

    let score = 0;
    const inputFields = form.querySelectorAll('input, textarea, select');
    
    // Must have minimum number of fields to be considered
    if (inputFields.length < 3) return false;

    // Check for job application patterns
    for (const pattern of jobFormPatterns) {
      if (formText.includes(pattern) || formHTML.includes(pattern)) {
        score += 5;
      }
    }

    // Check for personal info sections
    for (const pattern of personalInfoPatterns) {
      if (formText.includes(pattern) || formHTML.includes(pattern)) {
        score += 10;
      }
    }

    // Check input field attributes and labels
    inputFields.forEach(input => {
      const fieldInfo = this.getFieldInfo(input);
      if (this.isJobRelevantField(fieldInfo)) {
        score += 3;
      }
    });

    return score >= 15; // Threshold for job application form
  }

  detectSPAFormContainers() {
    // Detect form-like structures in Single Page Applications
    const selectors = [
      '[data-testid*="application"]',
      '[class*="application-form"]',
      '[class*="job-application"]',
      '[id*="application"]',
      '.form-container',
      '.application-container',
      '[role="form"]'
    ];

    const containers = [];
    
    selectors.forEach(selector => {
      const elements = document.querySelectorAll(selector);
      elements.forEach(element => {
        const inputs = element.querySelectorAll('input, textarea, select');
        if (inputs.length >= 3) {
          containers.push(element);
        }
      });
    });

    return containers;
  }

  analyzeForm(form, index) {
    const fields = this.extractFormFields(form);
    const formInfo = {
      id: `form-${index}`,
      element: form,
      type: 'form',
      fields: fields,
      confidence: this.calculateFormConfidence(form, fields),
      action: form.action || '',
      method: form.method || 'GET',
      fieldCount: fields.length
    };

    return formInfo;
  }

  analyzeFormContainer(container, index) {
    const fields = this.extractFormFields(container);
    const formInfo = {
      id: `container-${index}`,
      element: container,
      type: 'container',
      fields: fields,
      confidence: this.calculateFormConfidence(container, fields),
      action: '',
      method: '',
      fieldCount: fields.length
    };

    return formInfo;
  }

  extractFormFields(formElement) {
    const fields = [];
    const inputs = formElement.querySelectorAll('input, textarea, select');

    inputs.forEach((input, index) => {
      // Skip hidden, submit, and button type inputs
      if (input.type === 'hidden' || input.type === 'submit' || input.type === 'button') {
        return;
      }

      const fieldInfo = this.getFieldInfo(input);
      if (fieldInfo.label || fieldInfo.name || fieldInfo.id) {
        fields.push({
          id: `field-${index}`,
          element: input,
          ...fieldInfo,
          category: this.categorizeField(fieldInfo),
          priority: this.getFieldPriority(fieldInfo),
          isRequired: input.required || input.getAttribute('aria-required') === 'true'
        });
      }
    });

    return fields.sort((a, b) => b.priority - a.priority);
  }

  getFieldInfo(input) {
    // Get field label
    let label = '';
    
    // Try to find associated label
    if (input.id) {
      const labelElement = document.querySelector(`label[for="${input.id}"]`);
      if (labelElement) {
        label = labelElement.textContent.trim();
      }
    }

    // Try parent label
    if (!label) {
      const parentLabel = input.closest('label');
      if (parentLabel) {
        label = parentLabel.textContent.replace(input.value || '', '').trim();
      }
    }

    // Try nearby text
    if (!label) {
      label = this.findNearbyLabel(input);
    }

    return {
      label: label,
      name: input.name || '',
      id: input.id || '',
      type: input.type || input.tagName.toLowerCase(),
      placeholder: input.placeholder || '',
      value: input.value || '',
      className: input.className || '',
      attributes: this.getRelevantAttributes(input)
    };
  }

  findNearbyLabel(input) {
    // Look for text in nearby elements
    const parent = input.parentElement;
    if (!parent) return '';

    // Check previous sibling text nodes
    let sibling = input.previousSibling;
    while (sibling) {
      if (sibling.nodeType === Node.TEXT_NODE && sibling.textContent.trim()) {
        return sibling.textContent.trim();
      }
      if (sibling.nodeType === Node.ELEMENT_NODE) {
        const text = sibling.textContent.trim();
        if (text && text.length < 100) { // Reasonable label length
          return text;
        }
      }
      sibling = sibling.previousSibling;
    }

    // Check parent's previous sibling or parent text
    const parentText = parent.textContent.replace(input.value || '', '').trim();
    const words = parentText.split(/\s+/);
    if (words.length <= 5) { // Short enough to be a label
      return parentText;
    }

    return '';
  }

  getRelevantAttributes(input) {
    const relevantAttrs = ['data-testid', 'aria-label', 'aria-labelledby', 'title'];
    const attributes = {};
    
    relevantAttrs.forEach(attr => {
      const value = input.getAttribute(attr);
      if (value) {
        attributes[attr] = value;
      }
    });

    return attributes;
  }

  categorizeField(fieldInfo) {
    const text = `${fieldInfo.label} ${fieldInfo.name} ${fieldInfo.id} ${fieldInfo.placeholder}`.toLowerCase();

    // Define field categories and their patterns
    const categories = {
      personal: [
        'first name', 'firstname', 'fname', 'given name',
        'last name', 'lastname', 'lname', 'surname', 'family name',
        'full name', 'name', 'middle name',
        'date of birth', 'dob', 'birthday',
        'age', 'gender', 'pronouns'
      ],
      contact: [
        'email', 'e-mail', 'email address',
        'phone', 'telephone', 'mobile', 'cell',
        'address', 'street', 'city', 'state', 'zip', 'postal', 'country',
        'linkedin', 'website', 'portfolio', 'github'
      ],
      professional: [
        'position', 'job title', 'role', 'title',
        'company', 'employer', 'organization',
        'experience', 'years of experience', 'work experience',
        'salary', 'compensation', 'expected salary',
        'availability', 'start date', 'notice period'
      ],
      education: [
        'education', 'degree', 'school', 'university', 'college',
        'graduation', 'gpa', 'major', 'field of study'
      ],
      documents: [
        'resume', 'cv', 'curriculum vitae',
        'cover letter', 'portfolio', 'references'
      ],
      authorization: [
        'work authorization', 'visa', 'citizenship', 'eligible to work',
        'sponsorship', 'permit', 'green card'
      ],
      other: [
        'skills', 'certifications', 'languages',
        'why', 'question', 'additional', 'comments', 'notes'
      ]
    };

    for (const [category, patterns] of Object.entries(categories)) {
      for (const pattern of patterns) {
        if (text.includes(pattern)) {
          return category;
        }
      }
    }

    return 'other';
  }

  getFieldPriority(fieldInfo) {
    // Assign priority scores for different field types
    const priorityMap = {
      personal: 100,
      contact: 90,
      professional: 80,
      education: 70,
      authorization: 85,
      documents: 60,
      other: 50
    };

    const category = this.categorizeField(fieldInfo);
    let priority = priorityMap[category] || 50;

    // Boost priority for required fields
    if (fieldInfo.element && fieldInfo.element.required) {
      priority += 10;
    }

    return priority;
  }

  isJobRelevantField(fieldInfo) {
    const category = this.categorizeField(fieldInfo);
    return ['personal', 'contact', 'professional', 'education', 'authorization', 'documents'].includes(category);
  }

  calculateFormConfidence(formElement, fields) {
    let confidence = 0;

    // Base confidence from context
    confidence += this.confidence * 0.3;

    // Field relevance score
    const relevantFields = fields.filter(field => this.isJobRelevantField(field));
    confidence += (relevantFields.length / fields.length) * 40;

    // Field diversity (different categories)
    const categories = new Set(fields.map(field => field.category));
    confidence += categories.size * 5;

    // Form structure indicators
    const formText = formElement.textContent.toLowerCase();
    if (formText.includes('submit') || formText.includes('apply')) {
      confidence += 10;
    }

    return Math.min(Math.round(confidence), 100);
  }

  setupFormObserver() {
    // Watch for dynamically added forms
    const observer = new MutationObserver((mutations) => {
      let shouldRescan = false;

      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            // Check if new forms or form elements were added
            if (node.tagName === 'FORM' || 
                node.querySelector && node.querySelector('form, input, textarea, select')) {
              shouldRescan = true;
            }
          }
        });
      });

      if (shouldRescan) {
        setTimeout(() => {
          this.detectedForms = [];
          this.scanForJobApplicationForms();
          this.notifyPopup();
        }, 1000); // Debounce rescanning
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  setupMessageListener() {
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
      switch (message.action) {
        case 'checkForForms':
          sendResponse({
            formsDetected: this.detectedForms.length,
            totalFields: this.getTotalFieldCount(),
            confidence: this.getAverageConfidence(),
            fields: this.getFieldSummary(),
            isJobSite: this.isJobApplicationSite
          });
          break;

        case 'analyzeFields':
          this.analyzeFieldsForProfile(message.profile)
            .then(result => sendResponse(result))
            .catch(error => sendResponse({ success: false, error: error.message }));
          return true; // Indicate async response

        case 'fillForm':
          this.fillFormWithProfile(message.profile, message.fields, message.preview)
            .then(result => sendResponse(result))
            .catch(error => sendResponse({ success: false, error: error.message }));
          return true; // Indicate async response

        default:
          sendResponse({ success: false, error: 'Unknown action' });
      }
    });
  }

  getTotalFieldCount() {
    return this.detectedForms.reduce((total, form) => total + form.fieldCount, 0);
  }

  getAverageConfidence() {
    if (this.detectedForms.length === 0) return 0;
    const totalConfidence = this.detectedForms.reduce((total, form) => total + form.confidence, 0);
    return Math.round(totalConfidence / this.detectedForms.length);
  }

  getFieldSummary() {
    return this.detectedForms.flatMap(form => 
      form.fields.map(field => ({
        id: field.id,
        label: field.label,
        category: field.category,
        type: field.type,
        required: field.isRequired,
        priority: field.priority
      }))
    );
  }

  async analyzeFieldsForProfile(profile) {
    // This will be implemented in the semantic matcher
    // For now, return basic field mapping
    const fieldMatches = [];
    
    for (const form of this.detectedForms) {
      for (const field of form.fields) {
        const match = await window.semanticMatcher?.matchFieldToProfile(field, profile);
        if (match) {
          fieldMatches.push(match);
        }
      }
    }

    return {
      success: true,
      fieldMatches: fieldMatches
    };
  }

  async fillFormWithProfile(profile, fields, preview = false) {
    // This will be implemented in the form filler
    return window.formFiller?.fillForm(profile, fields, preview) || {
      success: false,
      error: 'Form filler not available'
    };
  }

  notifyPopup() {
    // Notify popup about form detection
    chrome.runtime.sendMessage({
      action: 'formDetected',
      formsCount: this.detectedForms.length,
      confidence: this.getAverageConfidence()
    });
  }
}

// Initialize form detector when page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.jobFormDetector = new JobFormDetector();
  });
} else {
  window.jobFormDetector = new JobFormDetector();
}

// Export for use by other scripts
window.JobFormDetector = JobFormDetector;