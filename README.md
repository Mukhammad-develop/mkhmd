# MKHMD - Personal Portfolio & Automation Platform

A modern Django-based personal website featuring portfolio showcase, professional timeline, and automated Turnitin document submission.

## Features

### 🎨 **Portfolio & Showcase**
- Combined portfolio with projects, awards, professional journey, and blog
- Interactive timeline with metrics and booking system
- Modern responsive design with smooth animations

### 🤖 **Turnitin Automation**
- Automated document submission to Turnitin plagiarism checker
- Support for .docx, .pdf, .pptx files (max 10MB)
- Selenium-based browser automation with Chinese UI support
- Smart form filling and progress tracking

### 🛠 **Development Tools**
- Startup valuation calculator
- API performance analyzer
- Business model canvas
- Free downloadable resources

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Mukhammad-develop/mkhmd.git
   cd mkhmd
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the development server**
   ```bash
   python3 manage.py runserver
   ```

4. **Access the website**
   - Open http://127.0.0.1:8000

### PythonAnywhere Deployment

1. **Upload code to PythonAnywhere**

2. **Install dependencies**
   ```bash
   pip3.10 install --user -r requirements.txt
   ```

3. **Configure web app and reload**

## Project Structure

```
mkhmd/
├── mkhmd/                 # Django project settings
├── website/               # Main website app
│   ├── templates/         # HTML templates
│   ├── views.py          # View functions with Turnitin automation
│   └── urls.py           # URL routing
├── static/               # Static files
├── requirements.txt      # Python dependencies
└── DEPLOYMENT.md        # Deployment guide
```

## Navigation Structure

- **Home** - Landing page with dual identity showcase
- **Portfolio** - Projects, awards, journey, and blog combined
- **Timeline** - Professional timeline, metrics, and booking
- **Projects** - Development tools, resources, and Turnitin automation

## Technologies

- **Backend**: Django 4.2+
- **Automation**: Selenium WebDriver
- **Browser**: Chrome/Chromium with headless support
- **Frontend**: HTML5, CSS3, JavaScript
- **Deployment**: PythonAnywhere compatible

## Turnitin Integration

The Turnitin automation feature automatically:
1. Navigates to Turnitin website
2. Uploads user documents
3. Fills required form fields
4. Enters access codes
5. Completes submission process

**Requirements**: Chrome/Chromium browser on server

## License

Private project - All rights reserved
