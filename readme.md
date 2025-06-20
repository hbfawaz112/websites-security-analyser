# Website Security Checker

A simple yet powerful web application that analyzes websites for security vulnerabilities and provides AI-powered recommendations for improvement.

![Security Checker](https://img.shields.io/badge/Security-Checker-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--3.5-orange.svg)

## Features

- **SSL/TLS Security Analysis** - Certificate validation and HTTPS configuration
- **Security Headers Check** - HSTS, CSP, X-Frame-Options, and more
- **Cookie Security** - Secure, HttpOnly, and SameSite attributes
- **Mixed Content Detection** - HTTP resources on HTTPS pages
- **Form Security Analysis** - Insecure form submissions
- **AI-Powered Recommendations** - Intelligent security advice using OpenAI
- **Security Scoring** - Overall security grade (A+ to F)
- **Responsive Design** - Works on desktop and mobile devices

## Demo

Try these example websites:
- `github.com` - Generally secure
- `stackoverflow.com` - Good security headers
- `badssl.com` - Test various SSL configurations

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- OpenAI API key (optional, for AI analysis)

### Installation

1. **Clone or download the project files**
   ```bash
   mkdir website-security-checker
   cd website-security-checker
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Go to `http://localhost:5000`

### Getting an OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Use it in the web interface when analyzing websites

**Note:** The application works without OpenAI API key, but AI-powered analysis will be disabled.

## Project Structure

```
website-security-checker/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── js/
│   │   └── main.js       # Frontend JavaScript
│   └── images/           # Static images
├── templates/
│   ├── layout.html       # Base template
│   ├── index.html        # Home page
│   └── results.html      # Results page
└── modules/
    ├── __init__.py
    ├── security_checks.py # Security analysis logic
    └── ai_analyzer.py    # AI integration
```

## Usage

### Web Interface

1. Enter a website URL (e.g., `example.com` or `https://example.com`)
2. Check the "Include AI-powered recommendations" checkbox if you want AI analysis
3. If AI analysis is enabled, enter your OpenAI API key
4. Click "Analyze Security"
5. View detailed security report
6. Get AI-powered recommendations (only if checkbox is checked and API key provided)

### API Usage

The application also provides a JSON API:

```bash
# POST request to analyze a website
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "include_ai": true, "openai_api_key": "your-api-key"}'
```

### Response Format

```json
{
  "scan_id": "uuid",
  "url": "https://example.com",
  "timestamp": "2025-06-12T10:30:00Z",
  "overall_score": 7.5,
  "grade": "B",
  "checks": {
    "ssl": { "status": "pass", "score": 10 },
    "headers": { "status": "warning", "score": 6 },
    "cookies": { "status": "pass", "score": 10 }
  },
  "ai_analysis": {
    "summary": "Website has good security...",
    "recommendations": ["Enable HSTS", "Add CSP header"]
  }
}
```

**Note:** The `ai_analysis` field will only be present if `include_ai` is true and a valid OpenAI API key is provided.

## Security Checks Performed

| Check | Description | Weight |
|-------|-------------|---------|
| **SSL/TLS** | Certificate validity, expiration, HTTPS usage | 30% |
| **Security Headers** | HSTS, CSP, X-Frame-Options, etc. | 25% |
| **Cookie Security** | Secure, HttpOnly, SameSite flags | 20% |
| **Mixed Content** | HTTP resources on HTTPS pages | 15% |
| **Form Security** | Insecure form submissions | 10% |

## Development

### Running in Development Mode

```bash
python app.py
```

### Adding New Security Checks

1. Edit `modules/security_checks.py`
2. Add new check method
3. Update `analyze_website()` method
4. Adjust scoring in `calculate_risk_score()`

### Customizing AI Analysis

Edit `modules/ai_analyzer.py` to:
- Modify prompts for different analysis styles
- Add new recommendation categories
- Customize scoring algorithms

## Acknowledgments

- [OpenAI](https://openai.com/) for AI-powered analysis
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Font Awesome](https://fontawesome.com/) for icons
---