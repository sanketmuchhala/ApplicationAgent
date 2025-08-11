from typing import List, Tuple, Dict, Any, Optional
from fuzzywuzzy import fuzz, process
import re


class TextSimilarity:
    """Text similarity and matching utilities"""
    
    def __init__(self):
        # Common field label patterns for job applications
        self.field_patterns = {
            'name': ['name', 'full name', 'complete name', 'your name'],
            'first_name': ['first name', 'firstname', 'given name', 'forename'],
            'last_name': ['last name', 'lastname', 'surname', 'family name'],
            'email': ['email', 'e-mail', 'email address', 'mail'],
            'phone': ['phone', 'telephone', 'mobile', 'cell', 'contact number'],
            'address': ['address', 'street address', 'home address'],
            'city': ['city', 'town'],
            'state': ['state', 'province', 'region'],
            'zip': ['zip', 'postal code', 'postcode', 'zip code'],
            'country': ['country', 'nation'],
            'experience': ['experience', 'years of experience', 'work experience'],
            'salary': ['salary', 'compensation', 'expected salary', 'desired salary'],
            'linkedin': ['linkedin', 'linkedin url', 'linkedin profile'],
            'github': ['github', 'github url', 'github profile'],
            'portfolio': ['portfolio', 'portfolio url', 'website', 'personal website']
        }
    
    def fuzzy_match(self, text: str, candidates: List[str], threshold: int = 70) -> List[Tuple[str, int]]:
        """Find fuzzy matches for text in candidate list"""
        matches = process.extract(text, candidates, limit=len(candidates))
        return [(match[0], match[1]) for match in matches if match[1] >= threshold]
    
    def best_fuzzy_match(self, text: str, candidates: List[str], threshold: int = 70) -> Tuple[str, int]:
        """Find best fuzzy match for text"""
        match = process.extractOne(text, candidates)
        if match and match[1] >= threshold:
            return match[0], match[1]
        return None, 0
    
    def partial_ratio_match(self, text1: str, text2: str) -> int:
        """Calculate partial ratio similarity between two texts"""
        return fuzz.partial_ratio(text1.lower(), text2.lower())
    
    def token_sort_ratio(self, text1: str, text2: str) -> int:
        """Calculate token sort ratio similarity"""
        return fuzz.token_sort_ratio(text1.lower(), text2.lower())
    
    def semantic_field_match(self, field_label: str) -> Tuple[Optional[str], int]:
        """Match field label to known field types"""
        cleaned_label = self.clean_text(field_label)
        
        best_match = None
        best_score = 0
        
        for field_type, patterns in self.field_patterns.items():
            for pattern in patterns:
                score = self.partial_ratio_match(cleaned_label, pattern)
                if score > best_score:
                    best_score = score
                    best_match = field_type
        
        return best_match, best_score
    
    def clean_text(self, text: str) -> str:
        """Clean text for better matching"""
        if not text:
            return ""
        
        # Convert to lowercase
        cleaned = text.lower()
        
        # Remove special characters but keep spaces
        cleaned = re.sub(r'[^\w\s]', ' ', cleaned)
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        return cleaned.strip()
    
    def extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        """Extract keywords from text"""
        if not text:
            return []
        
        cleaned = self.clean_text(text)
        words = cleaned.split()
        
        # Filter out common stop words and short words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'your', 'you', 'please'}
        
        keywords = []
        for word in words:
            if len(word) >= min_length and word not in stop_words:
                keywords.append(word)
        
        return keywords
    
    def calculate_text_similarity(self, text1: str, text2: str, method: str = 'partial') -> int:
        """Calculate similarity between two texts using specified method"""
        if not text1 or not text2:
            return 0
        
        text1_clean = self.clean_text(text1)
        text2_clean = self.clean_text(text2)
        
        if method == 'partial':
            return fuzz.partial_ratio(text1_clean, text2_clean)
        elif method == 'ratio':
            return fuzz.ratio(text1_clean, text2_clean)
        elif method == 'token_sort':
            return fuzz.token_sort_ratio(text1_clean, text2_clean)
        elif method == 'token_set':
            return fuzz.token_set_ratio(text1_clean, text2_clean)
        else:
            return fuzz.partial_ratio(text1_clean, text2_clean)
    
    def find_similar_options(self, target: str, options: List[str], threshold: int = 60) -> List[Dict[str, Any]]:
        """Find similar options from a list with scores"""
        if not target or not options:
            return []
        
        results = []
        target_clean = self.clean_text(target)
        
        for option in options:
            option_clean = self.clean_text(option)
            
            # Calculate different similarity scores
            partial_score = fuzz.partial_ratio(target_clean, option_clean)
            ratio_score = fuzz.ratio(target_clean, option_clean)
            token_sort_score = fuzz.token_sort_ratio(target_clean, option_clean)
            
            # Use the best score
            best_score = max(partial_score, ratio_score, token_sort_score)
            
            if best_score >= threshold:
                results.append({
                    'option': option,
                    'score': best_score,
                    'partial_score': partial_score,
                    'ratio_score': ratio_score,
                    'token_sort_score': token_sort_score
                })
        
        # Sort by score descending
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def match_experience_years(self, text: str) -> Tuple[float, int]:
        """Extract years of experience from text"""
        if not text:
            return 0.0, 0
        
        # Patterns to match years of experience
        patterns = [
            r'(\d+(?:\.\d+)?)\s*years?\s*(?:of\s*)?experience',
            r'(\d+(?:\.\d+)?)\s*yrs?\s*(?:of\s*)?experience',
            r'(\d+(?:\.\d+)?)\s*years?\s*(?:of\s*)?(?:work\s*)?experience',
            r'(\d+(?:\.\d+)?)\+?\s*years?',
            r'over\s*(\d+(?:\.\d+)?)\s*years?',
            r'more\s*than\s*(\d+(?:\.\d+)?)\s*years?',
        ]
        
        text_lower = text.lower()
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    years = float(match.group(1))
                    confidence = 90
                    return years, confidence
                except ValueError:
                    continue
        
        # Try to find just numbers that might represent years
        number_pattern = r'\b(\d+(?:\.\d+)?)\b'
        numbers = re.findall(number_pattern, text)
        
        for number_str in numbers:
            try:
                number = float(number_str)
                # Reasonable range for years of experience
                if 0 <= number <= 50:
                    return number, 60  # Lower confidence
            except ValueError:
                continue
        
        return 0.0, 0
    
    def match_salary_range(self, text: str) -> Tuple[int, int, int]:
        """Extract salary range from text"""
        if not text:
            return 0, 0, 0
        
        # Remove commas and dollar signs for easier matching
        cleaned_text = text.replace(',', '').replace('$', '')
        
        # Patterns for salary ranges
        range_patterns = [
            r'(\d+)(?:k|000)?\s*(?:-|to)\s*(\d+)(?:k|000)?',
            r'between\s*(\d+)(?:k|000)?\s*and\s*(\d+)(?:k|000)?',
            r'(\d+)(?:k|000)?\s*-\s*(\d+)(?:k|000)?',
        ]
        
        # Single salary patterns
        single_patterns = [
            r'(\d+)k\b',
            r'(\d+),?000\b',
            r'\$(\d+,?\d*)\b'
        ]
        
        # Try range patterns first
        for pattern in range_patterns:
            match = re.search(pattern, cleaned_text, re.IGNORECASE)
            if match:
                try:
                    min_val = int(match.group(1))
                    max_val = int(match.group(2))
                    
                    # Convert k to thousands
                    if 'k' in text.lower():
                        min_val *= 1000
                        max_val *= 1000
                    
                    return min_val, max_val, 85  # High confidence for ranges
                except ValueError:
                    continue
        
        # Try single salary patterns
        for pattern in single_patterns:
            match = re.search(pattern, cleaned_text, re.IGNORECASE)
            if match:
                try:
                    value_str = match.group(1).replace(',', '')
                    value = int(value_str)
                    
                    # Convert k to thousands
                    if 'k' in pattern:
                        value *= 1000
                    
                    return value, value, 70  # Medium confidence for single values
                except ValueError:
                    continue
        
        return 0, 0, 0
    
    def is_contact_field(self, field_label: str) -> bool:
        """Check if field is likely a contact field"""
        contact_keywords = ['email', 'phone', 'telephone', 'mobile', 'contact', 'address', 'linkedin', 'website']
        label_lower = field_label.lower()
        return any(keyword in label_lower for keyword in contact_keywords)
    
    def is_personal_field(self, field_label: str) -> bool:
        """Check if field is likely a personal information field"""
        personal_keywords = ['name', 'address', 'city', 'state', 'zip', 'country', 'birth', 'gender', 'nationality']
        label_lower = field_label.lower()
        return any(keyword in label_lower for keyword in personal_keywords)
    
    def is_experience_field(self, field_label: str) -> bool:
        """Check if field is likely an experience field"""
        experience_keywords = ['experience', 'years', 'work', 'job', 'position', 'company', 'employer', 'career', 'background']
        label_lower = field_label.lower()
        return any(keyword in label_lower for keyword in experience_keywords)
    
    def is_education_field(self, field_label: str) -> bool:
        """Check if field is likely an education field"""
        education_keywords = ['education', 'degree', 'university', 'college', 'school', 'gpa', 'graduation', 'diploma', 'certificate']
        label_lower = field_label.lower()
        return any(keyword in label_lower for keyword in education_keywords)