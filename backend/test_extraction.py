import re
from datetime import datetime, timedelta

def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'^[:]\s*', '', text)
    return text

def extract_hcp_name(text: str) -> str | None:
    text_lower = text.lower()
    edit_keywords = ['attendees', 'materials', 'samples', 'sentiment', 'outcomes', 'topics', 'date', 'time', 'interaction']
    if any(keyword in text_lower for keyword in edit_keywords) and ('met' not in text_lower and 'dr.' not in text_lower and 'doctor' not in text_lower):
        return None
    
    forbidden = [
        'today', 'yesterday', 'met', 'the', 'and', 'with', 'discussed', 'shared', 'i', 'we', 'product', 'time', 
        'date', 'attendees', 'materials', 'samples', 'outcomes', 'sentiment', 'interaction', 'hcp', 'name', 'is', 
        'dr', 'doctor', 'at', 'in', 'on', 'for', 'to', 'from', 'it', 'was', 'were', 'are', 'is', 'schedule', 
        'follow', 'up', 'not', 'a', 'an', 'visit', 'call', 'email', 'meeting', 'positive', 'negative', 'neutral', 
        'that', 'this', 'these', 'those', 'but', 'or', 'nor', 'so', 'yet', 'for', 'and', 'nor', 'but', 'or', 
        'yet', 'so', 'ug', 'am', 'pm', 'its', 'it\'s', 'change', 'update', 'edit', 'instead', 'swap', 'replace',
        'drug', 'drugs', 'unit', 'units', 'brochure', 'brochures', 'sheet', 'sheets', 'safety', 'data',
        'distributed'
    ]
    
    patterns = [
        r'(?:dr\.?|doctor)\s*([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)',
        r'met\s+(?:with\s+)?([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = clean_text(match.group(1))
            name = re.sub(r'\s+(?:at|in|on|for|to|from|with|and|the|a|an|it|was|were|are|is)$', '', name, flags=re.IGNORECASE)
            if name.lower() not in forbidden and len(name) > 2:
                return name
    
    words = text.split()
    for word in words:
        word = clean_text(word)
        if word and len(word) > 2 and word[0].isupper() and word.isalpha():
            if word.lower() not in forbidden:
                return word
    
    return None

def extract_time(text: str) -> str | None:
    text_lower = text.lower()
    
    edit_pattern = r'it\s+(\d{1,2}:\d{2}\s*(?:am|pm)?)'
    edit_match = re.search(edit_pattern, text, re.IGNORECASE)
    if edit_match:
        time_str = clean_text(edit_match.group(1))
        try:
            time_obj = datetime.strptime(time_str, "%I:%M %p")
            return time_obj.strftime("%H:%M")
        except:
            try:
                time_obj = datetime.strptime(time_str, "%I:%M%p")
                return time_obj.strftime("%H:%M")
            except:
                pass
    
    at_pattern = r'at\s+(\d{1,2}:\d{2}\s*(?:am|pm)?)'
    at_match = re.search(at_pattern, text, re.IGNORECASE)
    if at_match:
        time_str = clean_text(at_match.group(1))
        try:
            time_obj = datetime.strptime(time_str, "%I:%M %p")
            return time_obj.strftime("%H:%M")
        except:
            try:
                time_obj = datetime.strptime(time_str, "%I:%M%p")
                return time_obj.strftime("%H:%M")
            except:
                pass
    
    any_pattern = r'(\d{1,2}:\d{2}\s*(?:am|pm)?)'
    any_match = re.search(any_pattern, text, re.IGNORECASE)
    if any_match:
        time_str = clean_text(any_match.group(1))
        try:
            time_obj = datetime.strptime(time_str, "%I:%M %p")
            return time_obj.strftime("%H:%M")
        except:
            try:
                time_obj = datetime.strptime(time_str, "%I:%M%p")
                return time_obj.strftime("%H:%M")
            except:
                pass
    return None

def extract_interaction_type(text: str) -> str | None:
    text_lower = text.lower()
    
    edit_pattern = r'it\s+(?:was|is)\s+(meeting|call|email|visit)'
    edit_match = re.search(edit_pattern, text_lower)
    if edit_match:
        type_str = clean_text(edit_match.group(1))
        if type_str:
            return type_str.capitalize()
    
    if 'call' in text_lower:
        return 'Call'
    elif 'email' in text_lower:
        return 'Email'
    elif 'visit' in text_lower:
        return 'Visit'
    elif 'meeting' in text_lower:
        return 'Meeting'
    return None

def extract_attendees(text: str) -> str | None:
    text_lower = text.lower()
    
    if 'attendees' in text_lower and 'its' in text_lower:
        idx = text.lower().rfind('its')
        if idx != -1:
            attendees = clean_text(text[idx + 3:])
            if attendees:
                attendees = re.sub(r'\s+(?:and|were|was|are|is|at|in|on|for|to|from|we|it|materials|samples|sentiment|outcomes|topics|discussed)$', '', attendees, flags=re.IGNORECASE)
                if attendees:
                    return attendees
    
    patterns = [
        r'attendees?\s*(?:name\s+|were\s+|was\s+|are\s+|is\s+)?(.*?)(?:\.\s+|\s+(?:materials|samples|sentiment|outcomes|topics|discussed))',
        r'attendees?\s*(?:name\s+|were\s+|was\s+|are\s+|is\s+)?(.*)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            attendees = clean_text(match.group(1))
            if attendees:
                attendees = re.sub(r'\s+(?:and|were|was|are|is|at|in|on|for|to|from|we|it|materials|samples|sentiment|outcomes|topics|discussed)$', '', attendees, flags=re.IGNORECASE)
                if attendees:
                    return attendees
    return None

def extract_topics(text: str) -> str | None:
    text_lower = text.lower()
    
    edit_pattern = r'(?:we\s+)?discussed\s+(.*?)(?:\.\s+|\s+(?:materials|samples|sentiment|outcomes|attendees))'
    edit_match = re.search(edit_pattern, text, re.IGNORECASE | re.DOTALL)
    if edit_match:
        topics = clean_text(edit_match.group(1))
        if topics:
            topics = re.sub(r'\s+(?:and|were|was|are|is|at|in|on|for|to|from|materials|samples|sentiment|outcomes|attendees)$', '', topics, flags=re.IGNORECASE)
            if topics:
                return topics
    
    patterns = [
        r'discussed\s+(.*?)(?:\.\s+|\s+(?:materials|samples|sentiment|outcomes|attendees))',
        r'topics?\s+(?:discussed\s+)?(.*?)(?:\.\s+|\s+(?:materials|samples|sentiment|outcomes|attendees))',
        r'discussed\s+(.*)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            topics = clean_text(match.group(1))
            topics = re.sub(r'\s+(?:and|were|was|are|is|at|in|on|for|to|from|materials|samples|sentiment|outcomes|attendees)$', '', topics, flags=re.IGNORECASE)
            if topics:
                return topics
    return None

def extract_materials(text: str) -> str | None:
    text_lower = text.lower()
    
    patterns = [
        r'materials?\s*shared\s*(?:is\s+|are\s+|were\s+|was\s+)?(.*?)(?:\.\s+|\s+(?:samples|sentiment|outcomes|topics|attendees))',
        r'materials?\s*shared\s*(?:is\s+|are\s+|were\s+|was\s+)?(.*)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            materials = clean_text(match.group(1))
            if materials:
                materials = re.sub(r'\s+(?:and|were|was|are|is|at|in|on|for|to|from|samples|sentiment|outcomes|topics|attendees|shared)$', '', materials, flags=re.IGNORECASE)
                if materials:
                    return materials
    return None

def extract_samples(text: str) -> str | None:
    text_lower = text.lower()
    is_edit_message = 'not' in text_lower or 'change to' in text_lower or 'instead' in text_lower
    
    has_samples_key = 'samples' in text_lower or 'sample' in text_lower
    has_drug_unit = any(keyword in text_lower for keyword in ['unit', 'units', 'drug', 'vial', 'vials'])
    
    if is_edit_message and (has_samples_key or has_drug_unit):
        change_patterns = [
            r'change to\s+(\d+\s+units?.*)',
            r'change to\s+(.*?drug.*)',
            r'change to\s+(.*)'
        ]
        for pattern in change_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                samples = clean_text(match.group(1))
                if samples and any(keyword in samples.lower() for keyword in ['unit', 'units', 'drug', 'sample', 'samples', 'vial', 'vials']):
                    samples = re.sub(r'\s+(?:and|were|was|are|is|at|in|on|for|to|from|sentiment|outcomes|topics|attendees|materials|distributed)$', '', samples, flags=re.IGNORECASE)
                    if samples:
                        return samples
        
        its_patterns = [
            r'its\s+(\d+\s+units?.*)',
            r'its\s+(.*?drug.*)',
            r'its\s+(.*)'
        ]
        for pattern in its_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                samples = clean_text(match.group(1))
                if samples and any(keyword in samples.lower() for keyword in ['unit', 'units', 'drug', 'sample', 'samples', 'vial', 'vials']):
                    samples = re.sub(r'\s+(?:and|were|was|are|is|at|in|on|for|to|from|sentiment|outcomes|topics|attendees|materials|distributed)$', '', samples, flags=re.IGNORECASE)
                    if samples:
                        return samples
    
    patterns = [
        r'samples?\s*distributed\s*:\s*(.*?)(?:\.\s+|\s+(?:sentiment|outcomes|topics|attendees|materials))',
        r'samples?\s*distributed\s*(?:is|are|were|was)?\s*(.*?)(?:\.\s+|\s+(?:sentiment|outcomes|topics|attendees|materials))',
        r'samples?\s*distributed\s*(.*)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            samples = clean_text(match.group(1))
            if samples and any(keyword in samples.lower() for keyword in ['unit', 'units', 'drug', 'sample', 'samples', 'vial', 'vials']):
                samples = re.sub(r'\s+(?:and|were|was|are|is|at|in|on|for|to|from|sentiment|outcomes|topics|attendees|materials|distributed)$', '', samples, flags=re.IGNORECASE)
                if samples:
                    return samples
    return None

def extract_sentiment(text: str) -> str | None:
    text_lower = text.lower()
    
    edit_pattern = r'sentiment\s+(?:was|is)?\s*(positive|negative|neutral)'
    edit_match = re.search(edit_pattern, text_lower)
    if edit_match:
        sentiment_str = clean_text(edit_match.group(1))
        if sentiment_str:
            return sentiment_str.capitalize()
    
    positive = ['positive', 'good', 'great', 'excellent', 'happy', 'pleased', 'interested', 'favorable', 'liked']
    negative = ['negative', 'bad', 'poor', 'unhappy', 'concerned', 'worried', 'disappointed', 'difficult', 'issue']
    
    if any(word in text_lower for word in positive):
        return 'Positive'
    elif any(word in text_lower for word in negative):
        return 'Negative'
    elif 'neutral' in text_lower:
        return 'Neutral'
    return None

def extract_outcomes(text: str) -> str | None:
    text_lower = text.lower()
    
    edit_pattern = r'outcomes?\s*(?:were|was|are|is)?\s*(.*)'
    edit_match = re.search(edit_pattern, text, re.IGNORECASE | re.DOTALL)
    if edit_match:
        outcomes = clean_text(edit_match.group(1))
        if outcomes:
            outcomes = re.sub(r'\s+(?:and|were|was|are|is|at|in|on|for|to|from)$', '', outcomes, flags=re.IGNORECASE)
            if outcomes:
                return outcomes
    
    patterns = [
        r'outcomes?\s*:\s*(.*)',
        r'outcomes?\s*(?:is|are|were|was)?\s*(.*)',
        r'outcomes?\s+(.*)'
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            outcomes = clean_text(match.group(1))
            outcomes = re.sub(r'\s+(?:and|were|was|are|is|at|in|on|for|to|from)$', '', outcomes, flags=re.IGNORECASE)
            if outcomes:
                return outcomes
    return None

def extract_date(text: str) -> str | None:
    text_lower = text.lower()
    
    edit_pattern = r'date\s+(?:was|is)?\s*(today|yesterday)'
    edit_match = re.search(edit_pattern, text_lower)
    if edit_match:
        date_str = clean_text(edit_match.group(1))
        if date_str == 'yesterday':
            return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        elif date_str == 'today':
            return datetime.now().strftime("%Y-%m-%d")
    
    if 'yesterday' in text_lower:
        return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    elif 'today' in text_lower:
        return datetime.now().strftime("%Y-%m-%d")
    return None

test_messages = [
    "Today I met Dr. Prathish at 11:30 AM, it was a Meeting. Attendees were Praveena and Ravi. We discussed Product X efficacy, patient safety, and new treatment guidelines. Materials shared: Product brochure, safety data sheet. Samples distributed: 50 units of Drug Y. Sentiment was positive. Outcomes: Schedule follow-up in 2 weeks, send additional clinical data.",
    "it not 11:30 AM, it 10:30 am",
    "it was not Meeting, it was a visit",
    "NOT 50 units of Drug Y its 100 units of Drug Y",
    "attendees name Lisa",
    "materials shared is research paper",
    "sentiment was negative",
    "Attendees is praveena and ravi its praveena and giri",
    "Samples Distributed is not 50 units of Drug Y change to 100 units of Drug Y"
]

for i, msg in enumerate(test_messages):
    print(f"\n=== Test {i+1} ===")
    print(f"Message: {msg}")
    print(f"HCP Name: {extract_hcp_name(msg)}")
    print(f"Time: {extract_time(msg)}")
    print(f"Interaction Type: {extract_interaction_type(msg)}")
    print(f"Attendees: {extract_attendees(msg)}")
    print(f"Topics: {extract_topics(msg)}")
    print(f"Materials: {extract_materials(msg)}")
    print(f"Samples: {extract_samples(msg)}")
    print(f"Sentiment: {extract_sentiment(msg)}")
    print(f"Outcomes: {extract_outcomes(msg)}")
    print(f"Date: {extract_date(msg)}")
