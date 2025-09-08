"""
Utility functions for the Lead Scraper Bot
"""

import os
import re
import logging
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd

def setup_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        'exports',
        'logs',
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"Created directory: {directory}")

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def clean_phone_number(phone: str) -> str:
    """Clean and format phone number"""
    if not phone:
        return ""
    
    # Remove all non-digit characters
    digits = re.sub(r'[^\d]', '', phone)
    
    # Format US phone numbers
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    else:
        return phone  # Return original if can't format

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for filesystem compatibility"""
    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    filename = re.sub(invalid_chars, '_', filename)
    
    # Remove multiple underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Trim and remove trailing dots/spaces
    filename = filename.strip('. ')
    
    return filename

def export_to_excel(data: List[Dict], filename: str, sheet_name: str = "Results") -> bool:
    """Export data to Excel file with formatting"""
    try:
        # Ensure exports directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else 'exports', exist_ok=True)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        if df.empty:
            logging.warning("No data to export")
            return False
        
        # Create Excel writer with formatting
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Get the workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        logging.info(f"Data exported to {filename}")
        return True
        
    except Exception as e:
        logging.error(f"Failed to export data to Excel: {e}")
        return False

def get_file_size(filepath: str) -> str:
    """Get human-readable file size"""
    try:
        size = os.path.getsize(filepath)
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        
        return f"{size:.1f} TB"
    
    except OSError:
        return "Unknown"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime object to string"""
    try:
        return dt.strftime(format_str)
    except (AttributeError, ValueError):
        return str(dt)

def parse_datetime(dt_string: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parse datetime string to datetime object"""
    try:
        return datetime.strptime(dt_string, format_str)
    except (ValueError, TypeError):
        return None

def normalize_location(location: str) -> str:
    """Normalize location string for consistency"""
    if not location:
        return ""
    
    # Common location formats
    location = location.strip()
    
    # Add state if missing for US cities
    if ',' not in location and location.lower() in ['new york', 'los angeles', 'chicago', 'houston']:
        location_map = {
            'new york': 'New York, NY',
            'los angeles': 'Los Angeles, CA',
            'chicago': 'Chicago, IL',
            'houston': 'Houston, TX'
        }
        return location_map.get(location.lower(), location)
    
    return location

def validate_url(url: str) -> bool:
    """Validate URL format"""
    if not url:
        return False
    
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None

def calculate_success_rate(total: int, successful: int) -> float:
    """Calculate success rate percentage"""
    if total == 0:
        return 0.0
    return (successful / total) * 100

def remove_duplicates(data: List[Dict], key: str = 'name') -> List[Dict]:
    """Remove duplicate entries based on a key field"""
    seen = set()
    unique_data = []
    
    for item in data:
        identifier = item.get(key, '').lower().strip()
        if identifier and identifier not in seen:
            seen.add(identifier)
            unique_data.append(item)
    
    return unique_data

def merge_business_data(existing: Dict, new: Dict) -> Dict:
    """Merge two business data dictionaries, preferring non-empty values"""
    merged = existing.copy()
    
    for key, value in new.items():
        if value and (key not in merged or not merged[key]):
            merged[key] = value
    
    return merged
