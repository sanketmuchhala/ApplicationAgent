import hashlib
import re
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from .ai_service import AIService
from ..models.form import Form, FormField, FormSection, FormMetadata, FieldType
from ..models.ai_config import AIResponse


class FormAnalyzer:
    """Analyzes HTML job application forms to extract structure and fields"""
    
    def __init__(self, ai_service: Optional[AIService] = None):
        self.ai_service = ai_service
    
    async def analyze_form(
        self, 
        html_content: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """Analyze HTML form using AI and fallback methods"""
        
        # Try AI analysis first if available
        if self.ai_service:
            try:
                ai_result = await self.ai_service.analyze_form_fields(html_content, context)
                
                if ai_result.success:
                    # Enhance AI result with basic HTML parsing
                    enhanced_result = await self._enhance_ai_analysis(html_content, ai_result.data)
                    
                    return AIResponse(
                        success=True,
                        provider=ai_result.provider,
                        operation_type=ai_result.operation_type,
                        data=enhanced_result,
                        confidence_score=ai_result.confidence_score,
                        processing_time_ms=ai_result.processing_time_ms,
                        tokens_used=ai_result.tokens_used,
                        estimated_cost=ai_result.estimated_cost
                    )
                    
            except Exception as e:
                print(f"AI form analysis failed, using fallback: {str(e)}")
        
        # Use basic HTML parsing as fallback
        basic_result = await self._basic_form_analysis(html_content, context)
        
        return AIResponse(
            success=True,
            provider="basic_html_parser",
            operation_type="form_analysis",
            data=basic_result,
            confidence_score=60.0,  # Lower confidence for basic parsing
            processing_time_ms=100
        )
    
    async def _enhance_ai_analysis(
        self, 
        html_content: str, 
        ai_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance AI analysis with additional HTML parsing details"""
        
        # Parse HTML to extract missing technical details
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all form elements
        forms = soup.find_all('form')
        
        if forms:
            form = forms[0]  # Use first form
            
            # Extract additional form metadata
            form_action = form.get('action', '')
            form_method = form.get('method', 'POST').upper()
            form_enctype = form.get('enctype', 'application/x-www-form-urlencoded')
            
            # Add technical details to AI result
            if 'form_metadata' not in ai_data:
                ai_data['form_metadata'] = {}
                
            ai_data['form_metadata'].update({
                'form_action': form_action,
                'form_method': form_method,
                'form_enctype': form_enctype,
                'has_file_uploads': 'multipart/form-data' in form_enctype
            })
            
            # Enhance field information with HTML attributes
            fields = ai_data.get('fields', [])
            html_fields = self._extract_html_fields(soup)
            
            # Match AI fields with HTML fields to add technical details
            for field in fields:
                field_id = field.get('field_id')
                html_field = next((hf for hf in html_fields if hf['field_id'] == field_id), None)
                
                if html_field:
                    field.update({
                        'html_attributes': html_field.get('attributes', {}),
                        'validation_pattern': html_field.get('pattern'),
                        'autocomplete': html_field.get('autocomplete'),
                        'aria_label': html_field.get('aria_label')
                    })
        
        return ai_data
    
    async def _basic_form_analysis(
        self, 
        html_content: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Basic HTML form analysis without AI"""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Generate form ID based on content hash
        form_id = hashlib.md5(html_content.encode()).hexdigest()[:8]
        
        # Extract basic form information
        forms = soup.find_all('form')
        
        if not forms:
            return {
                "error": "No form elements found in HTML",
                "form_metadata": {"total_fields": 0}
            }
        
        form = forms[0]  # Analyze first form
        
        # Extract form metadata
        form_metadata = {
            "form_id": form_id,
            "title": self._extract_form_title(soup),
            "company": self._extract_company_name(soup),
            "position": self._extract_position_name(soup),
            "form_type": "standard",
            "form_action": form.get('action', ''),
            "form_method": form.get('method', 'POST').upper(),
            "total_fields": 0,
            "required_fields": 0,
            "optional_fields": 0,
            "has_file_uploads": False
        }
        
        # Extract all form fields
        html_fields = self._extract_html_fields(soup)
        
        # Convert to structured format
        sections = []
        fields = []
        
        current_section = None
        section_order = 0
        
        for html_field in html_fields:
            # Create FormField object
            field = {
                "field_id": html_field["field_id"],
                "field_name": html_field["field_name"],
                "label": html_field["label"],
                "field_type": html_field["field_type"],
                "input_type": html_field.get("input_type"),
                "required": html_field["required"],
                "placeholder": html_field.get("placeholder", ""),
                "max_length": html_field.get("max_length"),
                "options": html_field.get("options", []),
                "section": html_field.get("section", "General"),
                "context_clues": html_field.get("context_clues", [])
            }
            
            fields.append(field)
            
            # Update metadata counts
            form_metadata["total_fields"] += 1
            if field["required"]:
                form_metadata["required_fields"] += 1
            else:
                form_metadata["optional_fields"] += 1
            
            if field["field_type"] == "file":
                form_metadata["has_file_uploads"] = True
            
            # Group fields into sections
            section_name = field["section"]
            if current_section is None or current_section["section_name"] != section_name:
                current_section = {
                    "section_id": f"section_{section_order}",
                    "section_name": section_name,
                    "section_order": section_order,
                    "fields": []
                }
                sections.append(current_section)
                section_order += 1
            
            current_section["fields"].append(field)
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity_score(fields, form_metadata)
        
        return {
            "form_metadata": {**form_metadata, "complexity_score": complexity_score},
            "sections": sections,
            "fields": fields,
            "completion_strategy": self._generate_completion_strategy(fields),
            "potential_issues": self._identify_potential_issues(fields, form_metadata),
            "analysis_source": "basic_html_parser"
        }
    
    def _extract_html_fields(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all form fields from HTML"""
        fields = []
        field_counter = 0
        
        # Define field selectors
        field_selectors = [
            'input[type="text"]',
            'input[type="email"]', 
            'input[type="tel"]',
            'input[type="number"]',
            'input[type="date"]',
            'input[type="url"]',
            'input[type="password"]',
            'input[type="file"]',
            'input[type="checkbox"]',
            'input[type="radio"]',
            'textarea',
            'select'
        ]
        
        for selector in field_selectors:
            elements = soup.select(selector)
            
            for element in elements:
                field_data = self._extract_field_data(element, field_counter)
                if field_data:
                    fields.append(field_data)
                    field_counter += 1
        
        return fields
    
    def _extract_field_data(self, element, field_counter: int) -> Optional[Dict[str, Any]]:
        """Extract data from a single form field element"""
        try:
            # Get basic attributes
            field_name = element.get('name', f'field_{field_counter}')
            field_id = element.get('id', field_name)
            
            # Skip hidden fields and buttons
            if element.get('type') in ['hidden', 'submit', 'button', 'reset']:
                return None
            
            # Determine field type
            if element.name == 'input':
                input_type = element.get('type', 'text')
                field_type = self._map_input_type_to_field_type(input_type)
            elif element.name == 'textarea':
                field_type = FieldType.TEXTAREA
                input_type = 'textarea'
            elif element.name == 'select':
                field_type = FieldType.SELECT
                input_type = 'select'
            else:
                field_type = FieldType.TEXT
                input_type = 'text'
            
            # Extract label
            label = self._extract_field_label(element, field_id)
            
            # Extract other attributes
            required = element.has_attr('required') or element.get('aria-required') == 'true'
            placeholder = element.get('placeholder', '')
            max_length = element.get('maxlength')
            
            if max_length:
                try:
                    max_length = int(max_length)
                except (ValueError, TypeError):
                    max_length = None
            
            # Extract options for select/radio fields
            options = []
            if element.name == 'select':
                option_elements = element.find_all('option')
                options = [opt.get_text(strip=True) for opt in option_elements if opt.get_text(strip=True)]
            elif element.get('type') == 'radio':
                # Find other radio buttons with same name
                radio_elements = element.parent.find_all('input', {'type': 'radio', 'name': field_name})
                options = [radio.get('value', '') for radio in radio_elements if radio.get('value')]
            
            # Extract context clues
            context_clues = self._extract_context_clues(element)
            
            # Determine section
            section = self._determine_field_section(element, label, context_clues)
            
            return {
                "field_id": field_id,
                "field_name": field_name,
                "label": label,
                "field_type": field_type.value,
                "input_type": input_type,
                "required": required,
                "placeholder": placeholder,
                "max_length": max_length,
                "options": options,
                "section": section,
                "context_clues": context_clues,
                "attributes": dict(element.attrs)
            }
            
        except Exception as e:
            print(f"Error extracting field data: {str(e)}")
            return None
    
    def _map_input_type_to_field_type(self, input_type: str) -> FieldType:
        """Map HTML input type to FieldType enum"""
        mapping = {
            'text': FieldType.TEXT,
            'email': FieldType.EMAIL,
            'tel': FieldType.PHONE,
            'phone': FieldType.PHONE,
            'number': FieldType.NUMBER,
            'date': FieldType.DATE,
            'url': FieldType.URL,
            'password': FieldType.PASSWORD,
            'file': FieldType.FILE,
            'checkbox': FieldType.CHECKBOX,
            'radio': FieldType.RADIO
        }
        return mapping.get(input_type, FieldType.TEXT)
    
    def _extract_field_label(self, element, field_id: str) -> str:
        """Extract label for a form field"""
        # Try to find associated label element
        label_element = None
        
        # Method 1: label with 'for' attribute
        if field_id:
            label_element = element.find_parent().find('label', {'for': field_id})
        
        # Method 2: parent label element
        if not label_element:
            label_element = element.find_parent('label')
        
        # Method 3: preceding label
        if not label_element:
            label_element = element.find_previous_sibling('label')
        
        # Method 4: nearby text
        if not label_element:
            # Look for text in parent elements
            parent = element.parent
            for _ in range(3):  # Check up to 3 parent levels
                if parent:
                    text_content = parent.get_text(strip=True)
                    if text_content and len(text_content) < 200:  # Reasonable label length
                        # Clean up the text
                        cleaned_text = re.sub(r'\s+', ' ', text_content)
                        if cleaned_text:
                            return cleaned_text
                    parent = parent.parent
        
        if label_element:
            return label_element.get_text(strip=True)
        
        # Fallback: use placeholder, name, or id
        return element.get('placeholder', '') or element.get('name', '') or field_id
    
    def _extract_context_clues(self, element) -> List[str]:
        """Extract context clues from around the field"""
        context_clues = []
        
        # Get text from parent elements
        parent = element.parent
        for level in range(2):  # Check 2 levels up
            if parent:
                # Get all text nodes in parent, excluding the field itself
                text_nodes = []
                for text in parent.stripped_strings:
                    if text and len(text.strip()) > 2:
                        text_nodes.append(text.strip())
                
                if text_nodes:
                    context_text = ' '.join(text_nodes)
                    if context_text:
                        context_clues.append(context_text)
                
                parent = parent.parent
        
        # Get text from preceding and following siblings
        prev_sibling = element.find_previous_sibling()
        if prev_sibling:
            sibling_text = prev_sibling.get_text(strip=True)
            if sibling_text and len(sibling_text) < 100:
                context_clues.append(sibling_text)
        
        next_sibling = element.find_next_sibling()
        if next_sibling:
            sibling_text = next_sibling.get_text(strip=True)
            if sibling_text and len(sibling_text) < 100:
                context_clues.append(sibling_text)
        
        # Remove duplicates and empty strings
        context_clues = list(set([clue for clue in context_clues if clue]))
        
        return context_clues[:5]  # Limit to 5 context clues
    
    def _determine_field_section(self, element, label: str, context_clues: List[str]) -> str:
        """Determine which section a field belongs to"""
        
        # Check for fieldset or section elements
        fieldset = element.find_parent('fieldset')
        if fieldset:
            legend = fieldset.find('legend')
            if legend:
                return legend.get_text(strip=True)
        
        # Check for heading elements before this field
        for heading_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            heading = element.find_previous(heading_tag)
            if heading:
                heading_text = heading.get_text(strip=True)
                if heading_text and len(heading_text) < 50:
                    return heading_text
        
        # Use keyword matching to categorize
        all_text = f"{label} {' '.join(context_clues)}".lower()
        
        if any(keyword in all_text for keyword in ['name', 'contact', 'email', 'phone', 'address']):
            return "Personal Information"
        elif any(keyword in all_text for keyword in ['experience', 'work', 'employment', 'job', 'company']):
            return "Work Experience"
        elif any(keyword in all_text for keyword in ['education', 'school', 'degree', 'university']):
            return "Education"
        elif any(keyword in all_text for keyword in ['resume', 'cv', 'document', 'file', 'upload']):
            return "Documents"
        elif any(keyword in all_text for keyword in ['salary', 'compensation', 'pay', 'wage']):
            return "Compensation"
        elif any(keyword in all_text for keyword in ['why', 'interest', 'motivation', 'cover']):
            return "Additional Information"
        else:
            return "General"
    
    def _extract_form_title(self, soup: BeautifulSoup) -> str:
        """Extract form title from page"""
        # Try page title
        title_element = soup.find('title')
        if title_element:
            title = title_element.get_text(strip=True)
            if 'application' in title.lower() or 'apply' in title.lower():
                return title
        
        # Try main headings
        for heading_tag in ['h1', 'h2', 'h3']:
            headings = soup.find_all(heading_tag)
            for heading in headings:
                heading_text = heading.get_text(strip=True)
                if any(keyword in heading_text.lower() for keyword in ['application', 'apply', 'job', 'position']):
                    return heading_text
        
        return "Job Application Form"
    
    def _extract_company_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract company name from page"""
        # Look for common patterns
        patterns = [
            r'company[:\s]+([^<\n]+)',
            r'employer[:\s]+([^<\n]+)',
            r'organization[:\s]+([^<\n]+)'
        ]
        
        page_text = soup.get_text()
        
        for pattern in patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                company = match.group(1).strip()
                if len(company) < 100:  # Reasonable company name length
                    return company
        
        return None
    
    def _extract_position_name(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract position name from page"""
        patterns = [
            r'position[:\s]+([^<\n]+)',
            r'job title[:\s]+([^<\n]+)',
            r'role[:\s]+([^<\n]+)'
        ]
        
        page_text = soup.get_text()
        
        for pattern in patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                position = match.group(1).strip()
                if len(position) < 100:
                    return position
        
        return None
    
    def _calculate_complexity_score(self, fields: List[Dict], metadata: Dict) -> float:
        """Calculate form complexity score (0-10)"""
        score = 0.0
        
        total_fields = len(fields)
        required_fields = metadata.get("required_fields", 0)
        
        # Base complexity from field count
        if total_fields <= 5:
            score += 1.0
        elif total_fields <= 10:
            score += 2.0
        elif total_fields <= 20:
            score += 4.0
        else:
            score += 6.0
        
        # File upload complexity
        if metadata.get("has_file_uploads"):
            score += 1.0
        
        # Required fields ratio
        if total_fields > 0:
            required_ratio = required_fields / total_fields
            if required_ratio > 0.7:
                score += 1.0
        
        # Text area complexity
        textarea_count = sum(1 for f in fields if f.get("field_type") == "textarea")
        if textarea_count > 0:
            score += min(textarea_count * 0.5, 2.0)
        
        return min(score, 10.0)
    
    def _generate_completion_strategy(self, fields: List[Dict]) -> Dict[str, Any]:
        """Generate recommended completion strategy"""
        required_fields = [f["field_id"] for f in fields if f["required"]]
        optional_fields = [f["field_id"] for f in fields if not f["required"]]
        
        # Prioritize sections
        section_priorities = {
            "Personal Information": "high",
            "Contact Information": "high", 
            "Work Experience": "high",
            "Education": "medium",
            "Documents": "high",
            "Compensation": "medium",
            "Additional Information": "low"
        }
        
        return {
            "recommended_order": ["Personal Information", "Contact Information", "Work Experience", "Documents", "Education"],
            "critical_fields": required_fields,
            "optional_skip_fields": [f for f in optional_fields if "optional" in f.lower()],
            "section_priorities": section_priorities
        }
    
    def _identify_potential_issues(self, fields: List[Dict], metadata: Dict) -> List[Dict[str, Any]]:
        """Identify potential issues with form completion"""
        issues = []
        
        # File upload requirements
        if metadata.get("has_file_uploads"):
            issues.append({
                "issue_type": "file_upload_required",
                "severity": "high",
                "message": "Form requires file uploads - ensure documents are ready",
                "suggestion": "Prepare resume, cover letter, and other documents before starting"
            })
        
        # Many required fields
        required_count = metadata.get("required_fields", 0)
        if required_count > 10:
            issues.append({
                "issue_type": "many_required_fields", 
                "severity": "medium",
                "message": f"Form has {required_count} required fields",
                "suggestion": "Allow extra time to complete this application"
            })
        
        # Complex text areas
        textarea_fields = [f for f in fields if f.get("field_type") == "textarea"]
        if len(textarea_fields) > 2:
            issues.append({
                "issue_type": "multiple_essays",
                "severity": "medium", 
                "message": f"Form requires {len(textarea_fields)} text responses",
                "suggestion": "Prepare responses for essay questions in advance"
            })
        
        return issues