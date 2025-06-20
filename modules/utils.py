"""
Utility functions for the security checker application
"""

import re
import socket
from urllib.parse import urlparse
import json
from datetime import datetime

def validate_url(url):
    """
    Validate if a URL is properly formatted and accessible
    """
    if not url:
        return False, "URL is required"
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return False, "Invalid URL format"
        
        # Check if hostname is valid
        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid hostname"
        
        # Basic hostname validation
        if not re.match(r'^[a-zA-Z0-9.-]+$', hostname):
            return False, "Invalid hostname format"
        
        return True, url
    except Exception as e:
        return False, f"URL validation error: {str(e)}"

def is_reachable(hostname, port=443, timeout=5):
    """
    Check if a hostname is reachable on specified port
    """
    try:
        socket.create_connection((hostname, port), timeout=timeout)
        return True
    except (socket.timeout, socket.error):
        return False

def sanitize_url_for_display(url):
    """
    Sanitize URL for safe display in HTML
    """
    # Remove potential XSS vectors
    url = re.sub(r'[<>"\']', '', url)
    return url[:200]  # Limit length

def format_scan_duration(start_time, end_time):
    """
    Format scan duration in human readable format
    """
    duration = end_time - start_time
    seconds = duration.total_seconds()
    
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes}m {remaining_seconds}s"

def parse_security_score(score):
    """
    Parse security score and return grade and color
    """
    if score >= 9:
        return 'A+', '#28a745'
    elif score >= 8:
        return 'A', '#28a745'
    elif score >= 7:
        return 'B', '#ffc107'
    elif score >= 6:
        return 'C', '#fd7e14'
    elif score >= 5:
        return 'D', '#dc3545'
    else:
        return 'F', '#dc3545'

def extract_domain_from_url(url):
    """
    Extract clean domain name from URL
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return url

def safe_json_dumps(obj, indent=None):
    """
    Safely serialize object to JSON, handling datetime objects
    """
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    return json.dumps(obj, default=json_serializer, indent=indent)

def truncate_text(text, max_length=100, suffix="..."):
    """
    Truncate text to specified length
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def get_file_size_human(size_bytes):
    """
    Convert bytes to human readable format
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def clean_header_value(value):
    """
    Clean HTTP header value for safe display
    """
    if not value:
        return ""
    
    # Remove control characters and limit length
    cleaned = re.sub(r'[\x00-\x1F\x7F]', '', str(value))
    return cleaned[:500]  # Limit header value length

def is_internal_ip(hostname):
    """
    Check if hostname resolves to internal/private IP
    """
    try:
        ip = socket.gethostbyname(hostname)
        
        # Check for private IP ranges
        import ipaddress
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local
    except:
        return False

def extract_certificate_info(cert_dict):
    """
    Extract useful information from SSL certificate
    """
    if not cert_dict:
        return {}
    
    info = {}
    
    # Extract subject information
    subject = dict(x[0] for x in cert_dict.get('subject', []))
    info['common_name'] = subject.get('commonName', 'Unknown')
    info['organization'] = subject.get('organizationName', 'Unknown')
    info['country'] = subject.get('countryName', 'Unknown')
    
    # Extract issuer information
    issuer = dict(x[0] for x in cert_dict.get('issuer', []))
    info['issuer_name'] = issuer.get('commonName', 'Unknown')
    info['issuer_org'] = issuer.get('organizationName', 'Unknown')
    
    # Certificate validity
    info['not_before'] = cert_dict.get('notBefore', 'Unknown')
    info['not_after'] = cert_dict.get('notAfter', 'Unknown')
    
    # Subject Alternative Names
    san_list = []
    for item in cert_dict.get('subjectAltName', []):
        if item[0] == 'DNS':
            san_list.append(item[1])
    info['subject_alt_names'] = san_list
    
    return info

def calculate_days_until_expiry(expiry_date_str):
    """
    Calculate days until certificate expiry
    """
    try:
        # Parse certificate date format: "May 12 23:59:59 2025 GMT"
        expiry_date = datetime.strptime(expiry_date_str.replace(' GMT', ''), '%b %d %H:%M:%S %Y')
        days_until_expiry = (expiry_date - datetime.now()).days
        return max(0, days_until_expiry)
    except:
        return -1

def get_security_header_description(header_name):
    """
    Get detailed description for security headers
    """
    descriptions = {
        'Strict-Transport-Security': 'Enforces HTTPS connections and prevents protocol downgrade attacks',
        'X-Frame-Options': 'Prevents clickjacking attacks by controlling iframe embedding',
        'X-Content-Type-Options': 'Prevents MIME type sniffing vulnerabilities',
        'X-XSS-Protection': 'Enables browser XSS filtering (legacy, replaced by CSP)',
        'Content-Security-Policy': 'Prevents XSS and code injection attacks by controlling resource loading',
        'Referrer-Policy': 'Controls how much referrer information is included with requests',
        'Permissions-Policy': 'Controls which browser features can be used by the page'
    }
    return descriptions.get(header_name, 'Security header that enhances website protection')

def priority_sort_recommendations(recommendations):
    """
    Sort recommendations by priority/importance
    """
    priority_keywords = {
        'ssl': 10,
        'https': 10,
        'certificate': 9,
        'hsts': 8,
        'csp': 7,
        'content-security-policy': 7,
        'x-frame-options': 6,
        'cookie': 5,
        'secure': 5,
        'httponly': 4
    }
    
    def get_priority(recommendation):
        text = recommendation.lower()
        for keyword, priority in priority_keywords.items():
            if keyword in text:
                return priority
        return 1
    
    return sorted(recommendations, key=get_priority, reverse=True)

def generate_scan_summary(results):
    """
    Generate a brief summary of scan results
    """
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() 
                       if isinstance(result, dict) and result.get('status') == 'pass')
    warning_checks = sum(1 for result in results.values() 
                        if isinstance(result, dict) and result.get('status') == 'warning')
    failed_checks = total_checks - passed_checks - warning_checks
    
    if passed_checks == total_checks:
        return f"Excellent! All {total_checks} security checks passed."
    elif failed_checks == 0:
        return f"Good security posture. {passed_checks} checks passed, {warning_checks} need attention."
    else:
        return f"Security needs improvement. {failed_checks} critical issues, {warning_checks} warnings found."