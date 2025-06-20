import requests
import ssl
import socket
from urllib.parse import urlparse
from datetime import datetime
import re

class SecurityChecker:
    def __init__(self):
        self.timeout = 10
        self.user_agent = 'SecurityChecker/1.0'
    
    def analyze_website(self, url):
        """Main function to analyze website security"""
        results = {
            'ssl': self.check_ssl(url),
            'headers': self.check_security_headers(url),
            'cookies': self.check_cookies(url),
            'mixed_content': self.check_mixed_content(url),
            'forms': self.check_forms(url)
        }
        return results
    
    def check_ssl(self, url):
        """Check SSL certificate and HTTPS configuration"""
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        
        ssl_results = {
            'status': 'fail',
            'issues': [],
            'details': {},
            'score': 0
        }
        
        try:
            # Check if URL uses HTTPS
            if parsed_url.scheme != 'https':
                ssl_results['issues'].append('Website does not use HTTPS')
                return ssl_results
            
            # Get SSL certificate info
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check certificate expiry
                    expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (expiry_date - datetime.now()).days
                    
                    ssl_results['details'] = {
                        'issuer': dict(x[0] for x in cert['issuer']),
                        'subject': dict(x[0] for x in cert['subject']),
                        'expiry_date': cert['notAfter'],
                        'days_until_expiry': days_until_expiry
                    }
                    
                    # Check for issues
                    if days_until_expiry < 30:
                        ssl_results['issues'].append(f'Certificate expires in {days_until_expiry} days')
                    
                    # Check certificate chain
                    if days_until_expiry > 0:
                        ssl_results['status'] = 'pass'
                        ssl_results['score'] = 10
                        if days_until_expiry < 30:
                            ssl_results['score'] = 7
        
        except ssl.SSLError as e:
            ssl_results['issues'].append(f'SSL Error: {str(e)}')
        except socket.timeout:
            ssl_results['issues'].append('Connection timeout')
        except Exception as e:
            ssl_results['issues'].append(f'SSL check failed: {str(e)}')
        
        return ssl_results
    
    def check_security_headers(self, url):
        """Check for important security headers"""
        headers_results = {
            'status': 'fail',
            'present': [],
            'missing': [],
            'score': 0
        }
        
        # Important security headers to check
        security_headers = {
            'Strict-Transport-Security': 'HSTS',
            'X-Frame-Options': 'Clickjacking Protection',
            'X-Content-Type-Options': 'MIME Sniffing Protection',
            'X-XSS-Protection': 'XSS Protection',
            'Content-Security-Policy': 'Content Security Policy',
            'Referrer-Policy': 'Referrer Policy',
            'Permissions-Policy': 'Permissions Policy'
        }
        
        try:
            response = requests.get(url, timeout=self.timeout, headers={'User-Agent': self.user_agent})
            response_headers = response.headers
            
            for header, description in security_headers.items():
                if header in response_headers:
                    headers_results['present'].append({
                        'header': header,
                        'description': description,
                        'value': response_headers[header]
                    })
                else:
                    headers_results['missing'].append({
                        'header': header,
                        'description': description
                    })
            
            # Calculate score based on present headers
            score = (len(headers_results['present']) / len(security_headers)) * 10
            headers_results['score'] = round(score, 1)
            
            if score >= 7:
                headers_results['status'] = 'pass'
            elif score >= 4:
                headers_results['status'] = 'warning'
        
        except requests.RequestException as e:
            headers_results['error'] = f'Failed to fetch headers: {str(e)}'
        
        return headers_results
    
    def check_cookies(self, url):
        """Check cookie security attributes"""
        cookie_results = {
            'status': 'pass',
            'secure_cookies': 0,
            'insecure_cookies': 0,
            'issues': [],
            'score': 10
        }
        
        try:
            response = requests.get(url, timeout=self.timeout, headers={'User-Agent': self.user_agent})
            
            if 'Set-Cookie' in response.headers:
                cookies = response.headers['Set-Cookie']
                
                # Check for secure attributes
                if 'Secure' not in cookies:
                    cookie_results['issues'].append('Cookies missing Secure flag')
                    cookie_results['insecure_cookies'] += 1
                
                if 'HttpOnly' not in cookies:
                    cookie_results['issues'].append('Cookies missing HttpOnly flag')
                    cookie_results['insecure_cookies'] += 1
                
                if 'SameSite' not in cookies:
                    cookie_results['issues'].append('Cookies missing SameSite attribute')
                    cookie_results['insecure_cookies'] += 1
                
                if cookie_results['insecure_cookies'] > 0:
                    cookie_results['status'] = 'warning'
                    cookie_results['score'] = max(0, 10 - (cookie_results['insecure_cookies'] * 3))
            
        except requests.RequestException as e:
            cookie_results['error'] = f'Failed to check cookies: {str(e)}'
        
        return cookie_results
    
    def check_mixed_content(self, url):
        """Check for mixed content (HTTP resources on HTTPS pages)"""
        mixed_content_results = {
            'status': 'pass',
            'http_resources': [],
            'score': 10
        }
        
        parsed_url = urlparse(url)
        if parsed_url.scheme != 'https':
            return mixed_content_results
        
        try:
            response = requests.get(url, timeout=self.timeout, headers={'User-Agent': self.user_agent})
            content = response.text
            
            # Look for HTTP resources in HTTPS page
            http_patterns = [
                r'src=["\']http://[^"\']+["\']',
                r'href=["\']http://[^"\']+["\']',
                r'action=["\']http://[^"\']+["\']'
            ]
            
            for pattern in http_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                mixed_content_results['http_resources'].extend(matches)
            
            if mixed_content_results['http_resources']:
                mixed_content_results['status'] = 'warning'
                mixed_content_results['score'] = max(0, 10 - len(mixed_content_results['http_resources']))
        
        except requests.RequestException as e:
            mixed_content_results['error'] = f'Failed to check mixed content: {str(e)}'
        
        return mixed_content_results
    
    def check_forms(self, url):
        """Check form security (HTTPS submission, CSRF protection hints)"""
        form_results = {
            'status': 'pass',
            'forms_found': 0,
            'insecure_forms': 0,
            'issues': [],
            'score': 10
        }
        
        try:
            response = requests.get(url, timeout=self.timeout, headers={'User-Agent': self.user_agent})
            content = response.text
            
            # Find forms
            form_pattern = r'<form[^>]*>'
            forms = re.findall(form_pattern, content, re.IGNORECASE)
            form_results['forms_found'] = len(forms)
            
            for form in forms:
                # Check if form action is HTTP
                if 'action=' in form.lower():
                    action_match = re.search(r'action=["\']([^"\']+)["\']', form, re.IGNORECASE)
                    if action_match and action_match.group(1).startswith('http://'):
                        form_results['insecure_forms'] += 1
                        form_results['issues'].append('Form submits to HTTP URL')
            
            if form_results['insecure_forms'] > 0:
                form_results['status'] = 'warning'
                form_results['score'] = max(0, 10 - (form_results['insecure_forms'] * 5))
        
        except requests.RequestException as e:
            form_results['error'] = f'Failed to check forms: {str(e)}'
        
        return form_results
    
    def calculate_risk_score(self, results):
        """Calculate overall risk score from individual check results"""
        weights = {
            'ssl': 0.30,      # 30%
            'headers': 0.25,  # 25%
            'cookies': 0.20,  # 20%
            'mixed_content': 0.15,  # 15%
            'forms': 0.10     # 10%
        }
        
        total_score = 0
        total_weight = 0
        
        for check_name, weight in weights.items():
            if check_name in results and 'score' in results[check_name]:
                total_score += results[check_name]['score'] * weight
                total_weight += weight
        
        # Normalize score if some checks failed
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0
        
        return round(final_score, 1)