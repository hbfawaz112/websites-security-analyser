import os
import json
from openai import OpenAI

class AIAnalyzer:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            self.client = OpenAI(api_key=api_key)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
            print("Warning: OpenAI API key not found. AI analysis disabled.")
    
    def analyze_security_results(self, security_results, url, api_key=None):
        """Generate AI-powered analysis and recommendations"""
        # If a per-request API key is provided, use it to create a temporary OpenAI client
        client = None
        if api_key:
            try:
                print(f"Using provided OpenAI API key: {api_key}")
                client = OpenAI(api_key=api_key)
            except Exception as e:
                print(f"Invalid OpenAI API key provided: {str(e)}")
                return self.get_fallback_analysis(security_results)
        elif self.enabled:
            client = self.client
        else:
            return self.get_fallback_analysis(security_results)

        if client is None:
            return self.get_fallback_analysis(security_results)
        try:
            # Prepare data for AI analysis
            analysis_prompt = self.create_analysis_prompt(security_results, url)
            
            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a cybersecurity expert analyzing website security. 
                        Provide clear, actionable recommendations in a professional but accessible tone. 
                        Focus on practical steps the website owner can take to improve security.
                        Keep recommendations concise and prioritized by importance."""
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                max_tokens=1024,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            print(f"AI response: {ai_response}")
            # Parse AI response into structured format
            return self.parse_ai_response(ai_response, security_results)
        
        except Exception as e:
            print(f"AI analysis failed: {str(e)}")
            return self.get_fallback_analysis(security_results)
    
    def create_analysis_prompt(self, security_results, url):
        """Create a detailed prompt for AI analysis"""
        prompt = f"""Analyze the security scan results for {url}:

SECURITY SCAN RESULTS:
{json.dumps(security_results, indent=2)}

Please provide:
1. A brief summary of the overall security posture (2-3 sentences)
2. Top 3-5 priority recommendations for improvement
3. Brief explanation of the most critical security risks found
4. Quick wins that can be implemented easily

Format your response clearly with sections for Summary, Recommendations, and Critical Risks."""
        
        return prompt
    
    def parse_ai_response(self, ai_response, security_results):
        """Parse AI response into structured format"""
        # Simple parsing - in production, you might want more sophisticated parsing
        lines = ai_response.split('\n')
        
        parsed_response = {
            'summary': '',
            'recommendations': [],
            'critical_risks': [],
            'quick_wins': [],
            'raw_response': ai_response
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if 'summary' in line.lower() or 'overview' in line.lower():
                current_section = 'summary'
                continue
            elif 'recommendation' in line.lower():
                current_section = 'recommendations'
                continue
            elif 'critical' in line.lower() or 'risk' in line.lower():
                current_section = 'critical_risks'
                continue
            elif 'quick win' in line.lower():
                current_section = 'quick_wins'
                continue
            
            # Add content to appropriate section
            if current_section == 'summary' and not line.startswith('-') and not line.startswith('*'):
                parsed_response['summary'] += line + ' '
            elif current_section in ['recommendations', 'critical_risks', 'quick_wins']:
                if line.startswith('-') or line.startswith('*') or line.startswith(tuple('123456789')):
                    # Clean up bullet points
                    clean_line = line.lstrip('-*0123456789. ').strip()
                    if clean_line:
                        parsed_response[current_section].append(clean_line)
        
        # Fallback: extract recommendations from raw response if parsing failed
        if not parsed_response['recommendations']:
            parsed_response['recommendations'] = self.extract_recommendations_fallback(ai_response)
        
        # Generate summary if empty
        if not parsed_response['summary'].strip():
            parsed_response['summary'] = self.generate_summary_fallback(security_results)
        
        return parsed_response
    
    def extract_recommendations_fallback(self, text):
        """Extract recommendations using simple pattern matching"""
        recommendations = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for lines that start with common recommendation patterns
            if (line.startswith(('-', '*', '•')) or 
                any(word in line.lower() for word in ['implement', 'enable', 'add', 'configure', 'set up', 'use'])):
                clean_line = line.lstrip('-*•0123456789. ').strip()
                if len(clean_line) > 10:  # Filter out very short lines
                    recommendations.append(clean_line)
        
        return recommendations[:5]  # Limit to top 5
    
    def generate_summary_fallback(self, security_results):
        """Generate a basic summary when AI parsing fails"""
        total_checks = len(security_results)
        passed_checks = sum(1 for result in security_results.values() 
                          if isinstance(result, dict) and result.get('status') == 'pass')
        
        if passed_checks == total_checks:
            return "Website shows good overall security configuration with most security measures in place."
        elif passed_checks >= total_checks * 0.7:
            return "Website has decent security but there are some areas that need attention."
        else:
            return "Website has several security vulnerabilities that should be addressed promptly."
    
    def get_fallback_analysis(self, security_results):
        """Provide basic analysis when AI is not available"""
        recommendations = []
        critical_risks = []
        
        # SSL issues
        if security_results.get('ssl', {}).get('status') != 'pass':
            critical_risks.append("SSL/HTTPS configuration issues detected")
            recommendations.append("Enable HTTPS with a valid SSL certificate")
        
        # Missing security headers
        missing_headers = security_results.get('headers', {}).get('missing', [])
        if len(missing_headers) > 2:
            critical_risks.append("Multiple important security headers are missing")
            recommendations.append("Implement security headers like HSTS, CSP, and X-Frame-Options")
        
        # Cookie security
        if security_results.get('cookies', {}).get('status') != 'pass':
            recommendations.append("Configure cookies with Secure, HttpOnly, and SameSite attributes")
        
        # Mixed content
        if security_results.get('mixed_content', {}).get('http_resources'):
            critical_risks.append("Mixed content detected (HTTP resources on HTTPS page)")
            recommendations.append("Update all HTTP resources to use HTTPS")
        
        # Form security
        if security_results.get('forms', {}).get('insecure_forms', 0) > 0:
            recommendations.append("Ensure all forms submit to HTTPS URLs")
        
        # Generic recommendations if none specific found
        if not recommendations:
            recommendations = [
                "Regularly update and patch your web server and applications",
                "Implement a Web Application Firewall (WAF)",
                "Enable monitoring and logging for security events"
            ]
        
        return {
            'summary': self.generate_summary_fallback(security_results),
            'recommendations': recommendations[:5],
            'critical_risks': critical_risks,
            'quick_wins': [
                "Enable HSTS header for improved HTTPS security",
                "Add X-Frame-Options header to prevent clickjacking"
            ],
            'raw_response': 'Fallback analysis - AI service not available'
        }