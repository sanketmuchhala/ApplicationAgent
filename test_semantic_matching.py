#!/usr/bin/env python3
"""
Test semantic matching functionality without external dependencies
"""

import sys
import re
from typing import Dict, List, Optional, Any, Tuple

# Simple fuzzy matching implementation for testing
def simple_partial_ratio(text1: str, text2: str) -> int:
    """Basic partial ratio matching without fuzzywuzzy"""
    if not text1 or not text2:
        return 0
    
    text1 = text1.lower().strip()
    text2 = text2.lower().strip()
    
    if text1 == text2:
        return 100
    if text1 in text2 or text2 in text1:
        return 90
    
    # Simple word overlap scoring
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    if not words1 or not words2:
        return 0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    if not union:
        return 0
    
    return int((len(intersection) / len(union)) * 100)


class SimpleTextSimilarity:
    """Simplified text similarity for testing"""
    
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

    def partial_ratio_match(self, text1: str, text2: str) -> int:
        """Calculate partial ratio similarity between two texts"""
        return simple_partial_ratio(text1, text2)

    def semantic_field_match(self, field_label: str) -> Tuple[Optional[str], int]:
        """Match field label to known field types"""
        cleaned_label = self.clean_text(field_label)
        
        best_match = None
        best_score = 0
        
        # Debug logging
        print(f"DEBUG: Matching field label: '{field_label}' -> cleaned: '{cleaned_label}'")
        
        for field_type, patterns in self.field_patterns.items():
            for pattern in patterns:
                score = self.partial_ratio_match(cleaned_label, pattern)
                print(f"DEBUG: '{cleaned_label}' vs '{pattern}' -> score: {score}, field_type: {field_type}")
                if score > best_score:
                    best_score = score
                    best_match = field_type
                    print(f"DEBUG: New best match: {field_type} with score {score}")
        
        print(f"DEBUG: Final result: {best_match}, {best_score}")
        return best_match, best_score


def test_semantic_matching():
    """Test the semantic matching functionality"""
    print("🧪 Testing Semantic Field Matching")
    print("=" * 50)
    
    text_sim = SimpleTextSimilarity()
    
    # Test cases
    test_cases = [
        ("first name", "first_name", 100),
        ("First Name", "first_name", 100), 
        ("firstname", "first_name", 90),
        ("given name", "first_name", 90),
        ("last name", "last_name", 100),
        ("email address", "email", 90),
        ("phone number", "phone", 90),
        ("full name", "name", 90),  # This might match 'name' instead of 'first_name'
    ]
    
    print(f"\n📋 Running {len(test_cases)} test cases...")
    
    passed = 0
    failed = 0
    
    for i, (input_text, expected_field, min_score) in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{input_text}'")
        field_type, score = text_sim.semantic_field_match(input_text)
        
        print(f"   Result: {field_type} (score: {score})")
        
        if field_type == expected_field and score >= min_score:
            print(f"   ✅ PASS")
            passed += 1
        else:
            print(f"   ❌ FAIL - Expected: {expected_field} with score >= {min_score}")
            failed += 1
    
    print(f"\n" + "=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed > 0:
        print(f"\n🔧 Debugging failed cases...")
        print("Available field types:", list(text_sim.field_patterns.keys()))
        
        # Show the first_name patterns specifically
        print("first_name patterns:", text_sim.field_patterns.get('first_name', []))
    
    return failed == 0


if __name__ == "__main__":
    success = test_semantic_matching()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        
    sys.exit(0 if success else 1)