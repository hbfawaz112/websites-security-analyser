from flask import Flask, render_template, request, jsonify, flash
import os
from datetime import datetime
import uuid
from modules.security_checks import SecurityChecker
from modules.ai_analyzer import AIAnalyzer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize modules
security_checker = SecurityChecker()
ai_analyzer = AIAnalyzer()

@app.route('/')
def index():
    """Home page with URL input form"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze website security"""
    try:
        # Get URL from form or JSON
        if request.is_json:
            data = request.get_json()
            url = data.get('url')
            openai_api_key = data.get('openai_api_key')
        else:
            url = request.form.get('url')
            openai_api_key = request.form.get('openai_api_key')
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Add https:// if not present
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Generate scan ID
        scan_id = str(uuid.uuid4())
        
        # Perform security checks
        print(f"Starting security analysis for: {url}")
        security_results = security_checker.analyze_website(url)
        
        # Calculate overall score
        overall_score = security_checker.calculate_risk_score(security_results)
        
        # Get AI analysis
        ai_analysis = ai_analyzer.analyze_security_results(security_results, url, api_key=openai_api_key)
        
        # Prepare response data
        response_data = {
            'scan_id': scan_id,
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'overall_score': overall_score,
            'grade': get_security_grade(overall_score),
            'checks': security_results,
            'ai_analysis': ai_analysis
        }
        
        # Return JSON for API calls or render template for web interface
        if request.is_json:
            return jsonify(response_data)
        else:
            return render_template('results.html', data=response_data)
    
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        error_msg = f"Error analyzing website: {str(e)}"
        
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        else:
            flash(error_msg, 'error')
            return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for security analysis"""
    return analyze()

def get_security_grade(score):
    """Convert numeric score to letter grade"""
    if score >= 9:
        return 'A+'
    elif score >= 8:
        return 'A'
    elif score >= 7:
        return 'B'
    elif score >= 6:
        return 'C'
    elif score >= 5:
        return 'D'
    else:
        return 'F'

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Create modules directory if it doesn't exist
    os.makedirs('modules', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Run the application
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))