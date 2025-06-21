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

## AWS Deployment

This application can be deployed to AWS using Docker containers and ECS Fargate. Follow these steps to deploy your application to the cloud.

### Prerequisites

- AWS CLI installed and configured
- Docker Desktop installed
- AWS account with appropriate permissions

### Step 1: Install Required Tools

**Install Docker Desktop:**
- Download from [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
- Enable **Linux containers** during installation

**Install AWS CLI:**
- Download from [AWS CLI v2 for Windows](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-windows.html)
- Verify installation:
  ```bash
  docker --version
  aws --version
  ```

### Step 2: Configure AWS CLI

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Region (e.g., `eu-central-1`, `us-east-1`)
- Output format: `json`

### Step 3: Build and Tag Docker Image

In your project directory:

```bash
docker build -t ai-site-analyser .
```

### Step 4: Create ECR Repository

```bash
aws ecr create-repository --repository-name ai-site-analyser
```

### Step 5: Authenticate Docker to ECR

```bash
aws ecr get-login-password --region <your-region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
```

Replace `<your-region>` and `<account-id>` with your actual values.

### Step 6: Tag and Push Image to ECR

```bash
docker tag ai-site-analyser:latest <account-id>.dkr.ecr.<region>.amazonaws.com/ai-site-analyser:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/ai-site-analyser:latest
```

### Step 7: Create ECS Cluster

1. Go to [ECS Console](https://console.aws.amazon.com/ecs)
2. Click **Clusters** > **Create Cluster**
3. Select **Networking only (Fargate)**
4. Name your cluster (e.g., `ai-site-analyser`)
5. Click **Create**

### Step 8: Create Task Definition

1. Go to ECS > **Task Definitions** > **Create new**
2. Launch type: **Fargate**
3. Name: `ai-site-analyser`
4. Add container:
   - Name: `ai-site-analyser-app`
   - Image: `<account-id>.dkr.ecr.<region>.amazonaws.com/ai-site-analyser:latest`
   - Port mapping: `5000`
5. Set CPU: `0.25 vCPU`, Memory: `512MB`
6. Click **Create**

### Step 9: Run the Task

1. Go to **Clusters** > your cluster > **Tasks** > **Run new task**
2. Launch type: **Fargate**
3. Choose task definition: `ai-site-analyser`
4. Select a **public subnet**
5. Create or choose a **security group** with:
   - **Inbound Rule**: HTTP (TCP/5000) from `0.0.0.0/0`
6. Enable **Auto-assign Public IP**
7. Click **Run Task**

### Step 10: Access Your Application

1. Go to the **running task** → **ENI (Elastic Network Interface)**
2. Click to view the **public IPv4 address**
3. Open in browser: `http://<public-ip>:5000`

### Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Docker daemon connection error | Docker not running | Ensure Docker Desktop is running |
| `aws` command not found | AWS CLI not in PATH | Install AWS CLI and restart terminal |
| ECS task times out | No public IP or wrong security group | Enable Auto-assign Public IP and check security group |
| App only accessible locally | Flask listening on localhost | Use `host="0.0.0.0"` in `app.run()` |
| Port blocked | Security group doesn't allow traffic | Add inbound rule for TCP:5000 from 0.0.0.0/0 |
| Missing modules | Dependencies not installed | Ensure all packages are in `requirements.txt` |

## Next Steps & Improvements

This project has great potential for enhancement. Here are some planned features and improvements:

### 🤖 AI Model Selection
- **Multiple AI Providers**: Support for different AI models and providers
  - OpenAI GPT-4, GPT-3.5-turbo
  - Google Gemini Pro
  - Anthropic Claude
  - Local models (Ollama, etc.)
- **Model Comparison**: Compare security analysis results across different AI models
- **Custom Prompts**: Allow users to customize AI analysis prompts
- **Model Performance Metrics**: Track which models provide the best security insights

### 📊 Dashboard & Analytics
- **Security Dashboard**: Visual overview of analyzed websites
- **Trend Analysis**: Track security improvements over time
- **Comparative Analysis**: Compare multiple websites side-by-side
- **Security Metrics**: Charts and graphs showing security trends
- **Real-time Monitoring**: Continuous security monitoring for critical websites

### 📈 History & Reporting
- **Scan History**: Store and retrieve previous security scans
- **Report Export**: Export security reports in multiple formats
  - PDF reports with detailed findings
  - CSV/Excel data export
  - JSON API responses
  - Executive summary reports
- **Scheduled Scans**: Automate regular security assessments
- **Email Notifications**: Alert users about security changes or issues

### 🔧 Advanced Features
- **Custom Security Checks**: Allow users to define custom security rules
- **API Rate Limiting**: Implement proper rate limiting for external APIs
- **User Authentication**: User accounts and role-based access
- **Team Collaboration**: Share reports and findings with team members
- **Integration APIs**: Webhook support for CI/CD pipelines
- **Mobile App**: Native mobile application for on-the-go security checks

### 🛡️ Enhanced Security Analysis
- **Vulnerability Database**: Integration with CVE databases
- **Penetration Testing**: Basic automated penetration testing
- **Compliance Checking**: GDPR, HIPAA, PCI-DSS compliance checks
- **Third-party Risk**: Analyze dependencies and third-party services
- **Dark Web Monitoring**: Check if domain appears in data breaches

### 🎨 User Experience
- **Progressive Web App**: PWA features for better mobile experience
- **Dark Mode**: Toggle between light and dark themes
- **Accessibility**: WCAG compliance for better accessibility
- **Multi-language Support**: Internationalization (i18n)
- **Custom Branding**: White-label options for enterprise users

### 📱 Mobile & Accessibility
- **Responsive Design**: Optimize for all screen sizes
- **Touch-friendly Interface**: Better mobile navigation
- **Offline Mode**: Basic functionality without internet connection
- **Voice Commands**: Voice-activated security analysis
- **Screen Reader Support**: Full accessibility compliance

### 🔄 Automation & Integration
- **CI/CD Integration**: GitHub Actions, GitLab CI, Jenkins
- **Slack/Discord Bots**: Send security alerts to team channels
- **Jira/Linear Integration**: Create tickets for security issues
- **Webhook Support**: Real-time notifications to external systems
- **API Documentation**: Comprehensive API documentation with examples

### 📊 Data & Analytics
- **Security Score Trends**: Track website security over time
- **Industry Benchmarks**: Compare against industry standards
- **Risk Assessment**: Advanced risk scoring algorithms
- **Predictive Analysis**: Predict potential security issues
- **Performance Metrics**: Track application performance and reliability

### 🏢 Enterprise Features
- **Multi-tenant Architecture**: Support for multiple organizations
- **SSO Integration**: Single Sign-On with SAML/OAuth
- **Audit Logs**: Comprehensive audit trail
- **Custom Branding**: White-label solutions
- **SLA Monitoring**: Service Level Agreement tracking

### 🚀 Performance & Scalability
- **Caching**: Redis-based caching for faster responses
- **CDN Integration**: Content Delivery Network for static assets
- **Database Optimization**: Efficient data storage and retrieval
- **Load Balancing**: Horizontal scaling capabilities
- **Microservices**: Break down into smaller, focused services

### 🔐 Security Enhancements
- **API Security**: Rate limiting, authentication, and authorization
- **Data Encryption**: Encrypt sensitive data at rest and in transit
- **Security Headers**: Implement comprehensive security headers
- **Input Validation**: Robust input sanitization and validation
- **Logging & Monitoring**: Comprehensive security logging


## Acknowledgments

- [OpenAI](https://openai.com/) for AI-powered analysis
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Font Awesome](https://fontawesome.com/) for icons
---