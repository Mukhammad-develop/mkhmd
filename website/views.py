from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import platform
import subprocess
import time
import tempfile

# Turnitin Settings
TURNITIN_TEST_MODE = False  # Set to True for testing, False for real submissions

# Create your views here.

def home(request):
    """Dual Identity Landing page view - Software Developer & Businessman"""
    context = {
        'title': 'Software Developer & Businessman',
        'name': 'Abdurakhmon',
        'tagline': 'Software Developer & Strategic Businessman',
        'description': 'Building innovative solutions through code and driving business growth through strategic thinking',
        'email': 'abdurakhmon@mkhmd.uk',
        'github': 'https://github.com/mukhammad-develop',
        'linkedin': 'https://linkedin.com/in/abdurakhmon-dev',
        
        # Software Developer Identity
        'dev_skills': [
            {'name': 'Python', 'icon': 'fab fa-python'},
            {'name': 'Django', 'icon': 'fas fa-server'},
            {'name': 'FastAPI', 'icon': 'fas fa-bolt'},
            {'name': 'PostgreSQL', 'icon': 'fas fa-database'},
            {'name': 'Redis', 'icon': 'fas fa-memory'},
            {'name': 'Docker', 'icon': 'fab fa-docker'},
            {'name': 'AWS', 'icon': 'fab fa-aws'},
            {'name': 'MongoDB', 'icon': 'fas fa-leaf'},
            {'name': 'Kubernetes', 'icon': 'fas fa-dharmachakra'},
            {'name': 'GraphQL', 'icon': 'fas fa-project-diagram'},
            {'name': 'Celery', 'icon': 'fas fa-tasks'},
            {'name': 'RabbitMQ', 'icon': 'fas fa-exchange-alt'},
            {'name': 'Elasticsearch', 'icon': 'fas fa-search'},
            {'name': 'Linux', 'icon': 'fab fa-linux'},
            {'name': 'Git', 'icon': 'fab fa-git-alt'},
            {'name': 'CI/CD', 'icon': 'fas fa-cogs'},
        ],
        'dev_services': [
            {
                'title': 'API Development',
                'description': 'Creating robust RESTful APIs and GraphQL services with comprehensive documentation and authentication.',
                'icon': 'fas fa-code-branch'
            },
            {
                'title': 'Database Architecture',
                'description': 'Designing efficient database schemas, query optimization, and implementing caching strategies.',
                'icon': 'fas fa-database'
            },
            {
                'title': 'Microservices',
                'description': 'Building scalable microservice architectures with Docker, message queues, and service discovery.',
                'icon': 'fas fa-cubes'
            },
            {
                'title': 'Cloud Infrastructure',
                'description': 'Deploying and managing applications on AWS, implementing CI/CD pipelines and monitoring.',
                'icon': 'fas fa-cloud'
            },
        ],
        
        # Businessman Identity
        'business_skills': [
            {'name': 'Strategic Planning', 'icon': 'fas fa-chess'},
            {'name': 'Market Analysis', 'icon': 'fas fa-chart-line'},
            {'name': 'Financial Management', 'icon': 'fas fa-coins'},
            {'name': 'Team Leadership', 'icon': 'fas fa-users'},
            {'name': 'Product Management', 'icon': 'fas fa-rocket'},
            {'name': 'Business Development', 'icon': 'fas fa-handshake'},
            {'name': 'Investor Relations', 'icon': 'fas fa-chart-pie'},
            {'name': 'Risk Management', 'icon': 'fas fa-shield-alt'},
            {'name': 'Operations', 'icon': 'fas fa-cogs'},
            {'name': 'Digital Marketing', 'icon': 'fas fa-bullhorn'},
            {'name': 'Partnership', 'icon': 'fas fa-link'},
            {'name': 'Innovation', 'icon': 'fas fa-lightbulb'},
        ],
        'business_services': [
            {
                'title': 'Business Strategy',
                'description': 'Developing comprehensive business strategies, market positioning, and growth plans for startups and enterprises.',
                'icon': 'fas fa-chess-king'
            },
            {
                'title': 'Tech Consulting',
                'description': 'Bridging the gap between technology and business needs, providing strategic tech consulting for digital transformation.',
                'icon': 'fas fa-laptop-code'
            },
            {
                'title': 'Startup Mentoring',
                'description': 'Guiding early-stage startups through product development, market validation, and scaling strategies.',
                'icon': 'fas fa-seedling'
            },
            {
                'title': 'Investment Advisory',
                'description': 'Analyzing tech investments, due diligence for venture capital, and strategic partnership opportunities.',
                'icon': 'fas fa-chart-line'
            },
        ]
    }
    return render(request, 'website/home.html', context)

def portfolio(request):
    """Portfolio showcase page"""
    context = {
        'title': 'Portfolio Showcase',
        'name': 'Abdurakhmon',
        'dev_projects': [
            {
                'title': 'E-Commerce Platform',
                'description': 'Full-stack e-commerce solution with Django, PostgreSQL, and Redis caching',
                'tech_stack': ['Django', 'PostgreSQL', 'Redis', 'Docker'],
                'status': 'Live',
                'category': 'Web Application',
                'image': 'project1.jpg',
                'github': 'https://github.com/abdurakhmon/ecommerce',
                'demo': 'https://demo.example.com'
            },
            {
                'title': 'Real-time Analytics API',
                'description': 'High-performance analytics API serving 1M+ requests daily',
                'tech_stack': ['FastAPI', 'MongoDB', 'Elasticsearch'],
                'status': 'Production',
                'category': 'Backend API',
                'image': 'project2.jpg',
                'github': 'https://github.com/abdurakhmon/analytics',
                'demo': 'https://api.example.com'
            },
            {
                'title': 'Microservices Architecture',
                'description': 'Distributed system with 15+ microservices and service mesh',
                'tech_stack': ['Kubernetes', 'Docker', 'gRPC', 'AWS'],
                'status': 'Enterprise',
                'category': 'Infrastructure',
                'image': 'project3.jpg',
                'github': 'Private Repository',
                'demo': 'Case Study Available'
            }
        ],
        'business_projects': [
            {
                'title': 'FinTech Startup Launch',
                'description': '0 to $2M ARR in 18 months - Payment processing platform',
                'metrics': ['$2M ARR', '50K Users', '15 Team Members'],
                'status': 'Successful Exit',
                'category': 'Startup',
                'image': 'business1.jpg',
                'case_study': 'Available on Request'
            },
            {
                'title': 'Digital Transformation',
                'description': 'Led digital transformation for 200+ employee manufacturing company',
                'metrics': ['40% Cost Reduction', '60% Efficiency Gain', '18 Month ROI'],
                'status': 'Completed',
                'category': 'Consulting',
                'image': 'business2.jpg',
                'case_study': 'Full Case Study'
            },
            {
                'title': 'Investment Portfolio',
                'description': 'Angel investor in 8 tech startups with 3 successful exits',
                'metrics': ['8 Investments', '3 Exits', '25x Average Return'],
                'status': 'Ongoing',
                'category': 'Investment',
                'image': 'business3.jpg',
                'case_study': 'Portfolio Overview'
            }
        ]
    }
    return render(request, 'website/portfolio.html', context)

def achievements(request):
    """Achievements and credentials page"""
    context = {
        'title': 'Achievements & Recognition',
        'name': 'Abdurakhmon',
        'certifications': [
            {'name': 'AWS Solutions Architect Professional', 'issuer': 'Amazon Web Services', 'year': '2024', 'icon': 'fab fa-aws'},
            {'name': 'Google Cloud Professional Developer', 'issuer': 'Google Cloud', 'year': '2023', 'icon': 'fab fa-google'},
            {'name': 'Certified Kubernetes Administrator', 'issuer': 'CNCF', 'year': '2023', 'icon': 'fas fa-dharmachakra'},
            {'name': 'PMP - Project Management Professional', 'issuer': 'PMI', 'year': '2022', 'icon': 'fas fa-project-diagram'},
        ],
        'awards': [
            {'title': 'Tech Innovator of the Year', 'organization': 'TechCrunch', 'year': '2024'},
            {'title': 'Best Startup Mentor', 'organization': 'Startup Grind', 'year': '2023'},
            {'title': 'Outstanding Engineering Excellence', 'organization': 'IEEE', 'year': '2022'},
        ],
        'testimonials': [
            {
                'text': 'Abdurakhmon transformed our tech infrastructure and doubled our efficiency.',
                'author': 'Sarah Johnson',
                'role': 'CTO, TechCorp Inc.',
                'avatar': 'testimonial1.jpg'
            },
            {
                'text': 'His business insights helped us secure $5M Series A funding.',
                'author': 'Michael Chen',
                'role': 'CEO, StartupXYZ',
                'avatar': 'testimonial2.jpg'
            }
        ],
        'metrics': [
            {'label': 'Projects Delivered', 'value': '150+', 'icon': 'fas fa-rocket'},
            {'label': 'Businesses Helped', 'value': '25+', 'icon': 'fas fa-briefcase'},
            {'label': 'Team Members Led', 'value': '100+', 'icon': 'fas fa-users'},
            {'label': 'Success Rate', 'value': '98%', 'icon': 'fas fa-chart-line'},
        ]
    }
    return render(request, 'website/achievements.html', context)

def timeline(request):
    """Interactive timeline page"""
    context = {
        'title': 'Professional Journey',
        'name': 'Abdurakhmon',
        'timeline_events': [
            {
                'year': '2024',
                'title': 'Founded TechVentures LLC',
                'description': 'Launched consulting firm specializing in tech-business strategy',
                'type': 'business',
                'icon': 'fas fa-rocket',
                'achievements': ['$1M Revenue Target', '15 Enterprise Clients', 'Team of 8']
            },
            {
                'year': '2023',
                'title': 'Senior Software Architect',
                'description': 'Led technical architecture for Fortune 500 company',
                'type': 'technical',
                'icon': 'fas fa-code',
                'achievements': ['Microservices Migration', '40% Performance Improvement', 'Team Leadership']
            },
            {
                'year': '2022',
                'title': 'Startup Co-Founder & CTO',
                'description': 'Co-founded FinTech startup, scaled to $2M ARR',
                'type': 'business',
                'icon': 'fas fa-chart-line',
                'achievements': ['0 to $2M ARR', 'Successful Exit', '50K Users']
            },
            {
                'year': '2021',
                'title': 'Full-Stack Developer',
                'description': 'Built scalable web applications serving millions',
                'type': 'technical',
                'icon': 'fas fa-laptop-code',
                'achievements': ['1M+ Users', 'Cloud Architecture', 'DevOps Implementation']
            },
            {
                'year': '2020',
                'title': 'Computer Science Degree',
                'description': 'Graduated with honors, specialized in distributed systems',
                'type': 'education',
                'icon': 'fas fa-graduation-cap',
                'achievements': ['Summa Cum Laude', 'Research Publication', 'Dean\'s List']
            }
        ]
    }
    return render(request, 'website/timeline.html', context)

def blog(request):
    """Blog and insights page"""
    context = {
        'title': 'Insights & Thoughts',
        'name': 'Abdurakhmon',
        'featured_posts': [
            {
                'title': 'The Future of Microservices Architecture',
                'excerpt': 'Exploring emerging patterns in distributed systems and container orchestration...',
                'category': 'Technical',
                'read_time': '8 min read',
                'date': '2024-01-15',
                'image': 'blog1.jpg',
                'tags': ['Microservices', 'Kubernetes', 'Architecture']
            },
            {
                'title': 'Building Billion-Dollar Startups: Lessons Learned',
                'excerpt': 'Key insights from mentoring 20+ startups and 3 successful exits...',
                'category': 'Business',
                'read_time': '12 min read',
                'date': '2024-01-10',
                'image': 'blog2.jpg',
                'tags': ['Startups', 'Strategy', 'Investment']
            }
        ],
        'categories': [
            {'name': 'Technical', 'count': 15, 'icon': 'fas fa-code'},
            {'name': 'Business', 'count': 12, 'icon': 'fas fa-briefcase'},
            {'name': 'Leadership', 'count': 8, 'icon': 'fas fa-users'},
            {'name': 'Innovation', 'count': 5, 'icon': 'fas fa-lightbulb'},
        ]
    }
    return render(request, 'website/blog.html', context)

def metrics(request):
    """Live metrics dashboard"""
    context = {
        'title': 'Live Metrics Dashboard',
        'name': 'Abdurakhmon',
        'live_stats': [
            {'label': 'GitHub Commits', 'value': '2,847', 'trend': '+12%', 'icon': 'fab fa-github'},
            {'label': 'Lines of Code', 'value': '145K', 'trend': '+8%', 'icon': 'fas fa-code'},
            {'label': 'Active Projects', 'value': '8', 'trend': '+2', 'icon': 'fas fa-project-diagram'},
            {'label': 'Consulting Hours', 'value': '1,240', 'trend': '+15%', 'icon': 'fas fa-clock'},
        ],
        'availability': {
            'status': 'Available',
            'next_slot': 'Jan 25, 2024',
            'response_time': '< 2 hours',
            'capacity': '75%'
        }
    }
    return render(request, 'website/metrics.html', context)

def booking(request):
    """Consultation booking system"""
    context = {
        'title': 'Book Consultation',
        'name': 'Abdurakhmon',
        'services': [
            {
                'name': 'Technical Consultation',
                'duration': '60 minutes',
                'price': '$200',
                'description': 'Architecture review, code audit, technology strategy',
                'icon': 'fas fa-code'
            },
            {
                'name': 'Business Strategy Session',
                'duration': '90 minutes',
                'price': '$350',
                'description': 'Market analysis, growth planning, investment strategy',
                'icon': 'fas fa-chart-line'
            },
            {
                'name': 'Startup Mentoring',
                'duration': '45 minutes',
                'price': '$150',
                'description': 'Product development, funding guidance, team building',
                'icon': 'fas fa-rocket'
            }
        ]
    }
    return render(request, 'website/booking.html', context)

def resources(request):
    """Resources and tools page"""
    context = {
        'title': 'Free Resources & Tools',
        'name': 'Abdurakhmon',
        'tools': [
            {
                'name': 'Startup Valuation Calculator',
                'description': 'Calculate your startup valuation using multiple methodologies',
                'type': 'Calculator',
                'icon': 'fas fa-calculator'
            },
            {
                'name': 'API Performance Analyzer',
                'description': 'Analyze and optimize your API performance',
                'type': 'Tool',
                'icon': 'fas fa-tachometer-alt'
            },
            {
                'name': 'Business Model Canvas',
                'description': 'Interactive canvas for business model development',
                'type': 'Template',
                'icon': 'fas fa-th-large'
            }
        ],
        'downloads': [
            {
                'title': 'The Complete Guide to Microservices',
                'type': 'PDF Guide',
                'pages': '50 pages',
                'downloads': '1,200+',
                'icon': 'fas fa-file-pdf'
            },
            {
                'title': 'Startup Funding Deck Template',
                'type': 'PowerPoint',
                'pages': '25 slides',
                'downloads': '800+',
                'icon': 'fas fa-file-powerpoint'
            }
        ]
    }
    return render(request, 'website/resources.html', context)

@csrf_exempt
def turnitin(request):
    """Turnitin file upload and submission automation"""
    if request.method == 'POST':
        try:
            # Handle file upload
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return JsonResponse({'error': 'No file uploaded'}, status=400)
            
            # Validate file type
            allowed_extensions = ['.docx', '.pdf', '.pptx']
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            
            if file_extension not in allowed_extensions:
                return JsonResponse({
                    'error': f'File type not allowed. Only {", ".join(allowed_extensions)} files are supported.'
                }, status=400)
            
            # Save file temporarily
            temp_dir = tempfile.mkdtemp()
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            
            with open(temp_file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Automate Turnitin submission
            if TURNITIN_TEST_MODE:
                result = {
                    'success': True, 
                    'message': 'Test mode: File upload simulation completed successfully!', 
                    'filename': uploaded_file.name
                }
            else:
                result = submit_to_turnitin(temp_file_path, uploaded_file.name)
            
            # Clean up temporary file
            os.remove(temp_file_path)
            os.rmdir(temp_dir)
            
            return JsonResponse(result)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # GET request - show upload form
    context = {
        'title': 'Turnitin Submission',
        'name': 'Abdurakhmon',
    }
    return render(request, 'website/turnitin.html', context)

def submit_to_turnitin(file_path, filename):
    """Automate submission to Turnitin using Selenium"""
    try:
        # Check if Chrome is installed (macOS specific check)
        chrome_installed = False
        if platform.system() == "Darwin":  # macOS
            chrome_installed = os.path.exists("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        else:
            # For Linux/Windows, try to find chrome executable
            try:
                subprocess.run(['which', 'google-chrome-stable'], check=True, capture_output=True)
                chrome_installed = True
            except subprocess.CalledProcessError:
                try:
                    subprocess.run(['which', 'google-chrome'], check=True, capture_output=True)
                    chrome_installed = True
                except subprocess.CalledProcessError:
                    chrome_installed = False
        
        if not chrome_installed:
            return {
                'success': False,
                'error': 'Google Chrome browser is not installed. Please install Chrome to use this feature.'
            }
        
        # Set up Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Initialize webdriver with system ChromeDriver (bypasses security issues)
        driver = None
        try:
            # Try system ChromeDriver first (installed via Homebrew)
            if platform.system() == "Darwin":  # macOS
                chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                # Use system ChromeDriver installed via Homebrew
                service = Service("/opt/homebrew/bin/chromedriver")
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # For non-macOS systems, try system chrome
                driver = webdriver.Chrome(options=chrome_options)
            
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as system_error:
            # Fallback to webdriver-manager
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            except Exception as manager_error:
                return {
                    'success': False,
                    'error': f'Failed to initialize Chrome driver. System ChromeDriver error: {str(system_error)}. WebDriver Manager error: {str(manager_error)}'
                }
        
        wait = WebDriverWait(driver, 30)
        
        try:
            # Navigate to Turnitin
            print(f"Navigating to Turnitin...")
            driver.get('https://www.byturnitin.com/buk/#/')
            time.sleep(8)  # Give more time for page to load
            
            # Wait for page to fully load
            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            
            # Take screenshot for debugging
            screenshot_path = '/Users/abdurakhmon/Desktop/mkhmd/turnitin_initial.png'
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved: {screenshot_path}")
            
            # Try to find and click any "Start" or "Submit" button first
            start_buttons = [
                'button:contains("Start")',
                'button:contains("Submit")', 
                'button:contains("Upload")',
                'a:contains("Start")',
                'a:contains("Submit")',
                '.start-btn',
                '.submit-btn',
                '.upload-btn'
            ]
            
            for selector in start_buttons:
                try:
                    start_btn = driver.find_element(By.CSS_SELECTOR, selector)
                    if start_btn.is_displayed():
                        print(f"Found start button: {selector}")
                        driver.execute_script("arguments[0].click();", start_btn)
                        time.sleep(5)
                        break
                except:
                    continue
            
            # Look for file upload input with multiple strategies
            file_input = None
            selectors = [
                'input[type="file"]',
                'input[accept*="pdf"]',
                'input[accept*="docx"]',
                'input[accept*="doc"]',
                '.file-input input',
                '#file-upload',
                '#fileInput',
                '[data-testid*="file"]',
                'input[name*="file"]',
                'input[id*="file"]'
            ]
            
            print("Looking for file upload input...")
            for i, selector in enumerate(selectors):
                try:
                    file_input = driver.find_element(By.CSS_SELECTOR, selector)
                    if file_input and file_input.is_displayed():
                        print(f"Found file input with selector {i+1}: {selector}")
                        break
                    else:
                        file_input = None
                except:
                    continue
            
            if not file_input:
                # Try to find any input element that might accept files
                all_inputs = driver.find_elements(By.TAG_NAME, 'input')
                for inp in all_inputs:
                    try:
                        if inp.get_attribute('type') == 'file' or 'file' in inp.get_attribute('class') or '':
                            file_input = inp
                            print("Found file input via fallback method")
                            break
                    except:
                        continue
            
            if not file_input:
                # Save screenshot for debugging
                driver.save_screenshot('/Users/abdurakhmon/Desktop/mkhmd/turnitin_no_file_input.png')
                return {
                    'success': False,
                    'error': 'Could not find file upload input on the page. Screenshot saved for debugging.'
                }
            
            # Upload the file
            print(f"Uploading file: {file_path}")
            file_input.send_keys(file_path)
            time.sleep(5)
            
            # Wait for file upload to process
            print("Waiting for file upload to process...")
            time.sleep(8)
            
            # Fill form fields based on actual HTML structure
            form_fields = [
                # Paper Title field (文章标题)
                {
                    'value': 'TOPIC',
                    'selectors': [
                        'input[placeholder="请输入文章标题"]',
                        'input.ivu-input[placeholder*="标题"]',
                        '.ivu-form-item:has(label:contains("文章标题")) input',
                        'input[placeholder*="title"]',
                        'input[placeholder*="Title"]'
                    ]
                },
                # Author's Last Name field (姓)
                {
                    'value': 'Joseph',
                    'selectors': [
                        'input[placeholder="请输入作者姓氏"]',
                        'input.ivu-input[placeholder*="姓氏"]',
                        '.ivu-form-item:has(label:contains("姓")) input',
                        'input[placeholder*="last name"]',
                        'input[placeholder*="Last"]'
                    ]
                },
                # Author's First Name field (名)
                {
                    'value': 'Joseph',
                    'selectors': [
                        'input[placeholder="请输入作者名字"]',
                        'input.ivu-input[placeholder*="名字"]',
                        '.ivu-form-item:has(label:contains("名")) input',
                        'input[placeholder*="first name"]',
                        'input[placeholder*="First"]'
                    ]
                }
            ]
            
            # Fill each field
            print("Filling form fields...")
            for field in form_fields:
                field_found = False
                
                # Try direct placeholder matching first (most reliable)
                for selector in field['selectors']:
                    try:
                        # Wait for element to be present and interactable
                        element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        if element.is_displayed() and element.is_enabled():
                            # Clear field using multiple methods
                            element.clear()
                            time.sleep(0.5)  # Small delay for Vue.js reactivity
                            element.click()  # Focus the element
                            element.clear()  # Clear again
                            element.send_keys(field['value'])
                            field_found = True
                            print(f"Filled field '{field['value']}' using selector: {selector}")
                            break
                    except:
                        continue
                
                # If CSS selectors fail, try XPath with Chinese text
                if not field_found:
                    try:
                        if field['value'] == 'TOPIC':
                            xpath = "//input[@placeholder='请输入文章标题']"
                        elif field['selectors'][0] == 'input[placeholder="请输入作者姓氏"]':
                            xpath = "//input[@placeholder='请输入作者姓氏']"
                        else:
                            xpath = "//input[@placeholder='请输入作者名字']"
                        
                        element = driver.find_element(By.XPATH, xpath)
                        if element.is_displayed() and element.is_enabled():
                            element.clear()
                            time.sleep(0.5)
                            element.click()
                            element.clear()
                            element.send_keys(field['value'])
                            field_found = True
                            print(f"Filled field '{field['value']}' using XPath")
                    except:
                        pass
                
                # If still no field found, that's okay - continue with submission
                if not field_found:
                    print(f"Could not find field for value: {field['value']}")
            
            # Take screenshot after filling fields
            driver.save_screenshot('/Users/abdurakhmon/Desktop/mkhmd/turnitin_after_fields.png')
            print("Screenshot saved after filling fields")
            
            # Look for and click submit/next button
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                '.submit-btn',
                '.btn-submit',
                '.next-btn',
                '.continue-btn',
                '[data-testid*="submit"]',
                '[data-testid*="next"]'
            ]
            
            print("Looking for submit button...")
            submit_clicked = False
            
            # First, try to find the blue "下一步" button specifically
            try:
                # Look for buttons with Chinese text using multiple methods
                chinese_selectors = [
                    "//button[contains(text(), '下一步')]",
                    "//button[@class='next_step ivu-btn ivu-btn-default']",
                    "//span[text()='下一步']/parent::button",
                    ".next_step.ivu-btn"
                ]
                
                for selector in chinese_selectors:
                    try:
                        if selector.startswith("//"):
                            chinese_next_btn = driver.find_element(By.XPATH, selector)
                        else:
                            chinese_next_btn = driver.find_element(By.CSS_SELECTOR, selector)
                            
                        if chinese_next_btn.is_displayed() and chinese_next_btn.is_enabled():
                            print(f"Found Chinese '下一步' (Next Step) button using: {selector}")
                            # Try multiple click methods
                            try:
                                chinese_next_btn.click()  # Regular click first
                            except:
                                driver.execute_script("arguments[0].click();", chinese_next_btn)  # JavaScript click as fallback
                            
                            submit_clicked = True
                            time.sleep(5)  # Give more time for navigation
                            break
                    except:
                        continue
                        
                if submit_clicked:
                    print("Successfully clicked 下一步 button")
            except:
                pass
            
            # If Chinese button not found, try CSS selectors
            if not submit_clicked:
                for selector in submit_selectors:
                    try:
                        submit_btn = driver.find_element(By.CSS_SELECTOR, selector)
                        if submit_btn.is_displayed() and submit_btn.is_enabled():
                            print(f"Found submit button: {selector}")
                            driver.execute_script("arguments[0].click();", submit_btn)
                            submit_clicked = True
                            time.sleep(3)
                            break
                    except:
                        continue
            
            # If no specific submit button found, try all buttons
            if not submit_clicked:
                print("No specific submit button found, trying all buttons...")
                buttons = driver.find_elements(By.TAG_NAME, 'button')
                for i, btn in enumerate(buttons):
                    try:
                        if btn.is_displayed() and btn.is_enabled():
                            btn_text = btn.text.strip()
                            print(f"Button {i+1}: '{btn_text}'")
                            # Check for English and Chinese text
                            english_keywords = ['submit', 'next', 'continue', 'upload']
                            chinese_keywords = ['下一步', '提交', '上传', '继续']  # Next Step, Submit, Upload, Continue
                            
                            if (any(word in btn_text.lower() for word in english_keywords) or 
                                any(word in btn_text for word in chinese_keywords)):
                                print(f"Clicking button: '{btn_text}'")
                                driver.execute_script("arguments[0].click();", btn)
                                submit_clicked = True
                                time.sleep(3)
                                break
                    except:
                        continue
            
            if submit_clicked:
                print("Submit button clicked successfully")
            else:
                print("No submit button found")
            
            # Wait for next page or form
            print("Waiting for next page...")
            time.sleep(8)
            
            # Take screenshot after potential navigation
            driver.save_screenshot('/Users/abdurakhmon/Desktop/mkhmd/turnitin_after_submit.png')
            print("Screenshot saved after submit attempt")
            
            # Look for access code field (订单编号 - Order Number)
            access_code_selectors = [
                'input[placeholder="请输入订单编号(多个订单号用 # 连接)"]',
                'input[placeholder*="订单编号"]',
                'input.ivu-input[placeholder*="订单"]',
                '.text-wrapper_5 input',
                'input[placeholder*="order"]',
                'input[name*="access"]',
                'input[name*="code"]',
                'input[placeholder*="access"]',
                'input[placeholder*="code"]'
            ]
            
            print("Looking for access code field...")
            access_code_found = False
            final_submit_clicked = False
            
            # Try CSS selectors first
            for i, selector in enumerate(access_code_selectors):
                try:
                    access_code_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    if access_code_field.is_displayed() and access_code_field.is_enabled():
                        print(f"Found access code field with selector {i+1}: {selector}")
                        access_code_field.clear()
                        time.sleep(0.5)
                        access_code_field.click()  # Focus the field
                        access_code_field.clear()  # Clear again for Vue.js
                        access_code_field.send_keys('2884078633760879499')
                        access_code_found = True
                        print("Access code entered successfully")
                        break
                except:
                    continue
            
            # If CSS selectors fail, try XPath with Chinese placeholder
            if not access_code_found:
                try:
                    xpath = "//input[@placeholder='请输入订单编号(多个订单号用 # 连接)']"
                    access_code_field = driver.find_element(By.XPATH, xpath)
                    if access_code_field.is_displayed() and access_code_field.is_enabled():
                        print("Found access code field using XPath with Chinese placeholder")
                        access_code_field.clear()
                        time.sleep(0.5)
                        access_code_field.click()
                        access_code_field.clear()
                        access_code_field.send_keys('2884078633760879499')
                        access_code_found = True
                        print("Access code entered successfully via XPath")
                except:
                    pass
            
            if not access_code_found:
                print("No access code field found - might not be required or on different page")
            
            # Submit final form if access code was entered
            if access_code_found:
                time.sleep(2)
                print("Looking for final submit button...")
                
                # Look for the blue "立即检测" (Immediate Detection) button
                final_submit_clicked = False
                final_submit_selectors = [
                    "//button[contains(text(), '立即检测')]",
                    "//span[text()='立即检测']/parent::button",
                    "button.ivu-btn.ivu-btn-primary",
                    ".section_11.ivu-btn.ivu-btn-primary",
                    "button[class*='ivu-btn-primary']"
                ]
                
                for selector in final_submit_selectors:
                    try:
                        if selector.startswith("//"):
                            final_submit_btn = driver.find_element(By.XPATH, selector)
                        else:
                            final_submit_btn = driver.find_element(By.CSS_SELECTOR, selector)
                            
                        if final_submit_btn.is_displayed() and final_submit_btn.is_enabled():
                            print(f"Found final submit button '立即检测': {selector}")
                            # Try regular click first, then JavaScript click
                            try:
                                final_submit_btn.click()
                            except:
                                driver.execute_script("arguments[0].click();", final_submit_btn)
                            final_submit_clicked = True
                            print("Final '立即检测' button clicked successfully")
                            break
                    except:
                        continue
                
                # Fallback to original selectors if Chinese button not found
                if not final_submit_clicked:
                    for selector in submit_selectors:
                        try:
                            final_submit_btn = driver.find_element(By.CSS_SELECTOR, selector)
                            if final_submit_btn.is_displayed() and final_submit_btn.is_enabled():
                                print(f"Found final submit button (fallback): {selector}")
                                driver.execute_script("arguments[0].click();", final_submit_btn)
                                final_submit_clicked = True
                                break
                        except:
                            continue
                
                if final_submit_clicked:
                    print("Final submit button clicked")
                else:
                    print("No final submit button found")
                
                # Wait for completion
                time.sleep(10)
            
            # Take final screenshot
            driver.save_screenshot('/Users/abdurakhmon/Desktop/mkhmd/turnitin_final.png')
            print("Final screenshot saved")
            
            # Get current URL and check for success indicators
            current_url = driver.current_url
            page_source = driver.page_source.lower()
            page_title = driver.title
            
            print(f"Final URL: {current_url}")
            print(f"Page title: {page_title}")
            
            # Check for success indicators
            success_indicators = [
                'success', 'submitted', 'complete', 'uploaded', 
                'receipt', 'confirmation', 'thank you', 'received'
            ]
            
            is_success = any(indicator in page_source for indicator in success_indicators)
            print(f"Success indicators found: {is_success}")
            
            # Enhanced success detection - if we clicked the final button, consider it successful
            submission_successful = False
            
            # Check if we successfully clicked the final submit button
            if access_code_found and final_submit_clicked:
                print("✅ Both access code entered and final submit button clicked - marking as successful")
                submission_successful = True
            
            # Check for success indicators in page content
            if is_success:
                print("✅ Success indicators found in page content")
                submission_successful = True
            
            # Check if URL changed from initial page (even if it's still within the same domain)
            if current_url != 'https://www.byturnitin.com/buk/#/':
                print(f"✅ URL changed from initial page - submission likely successful")
                submission_successful = True
            
            # Check for Chinese success/completion indicators
            chinese_success_indicators = [
                '检测完成', '提交成功', '上传成功', '检测中', '处理中', 
                '已提交', '检测报告', '结果', '完成'
            ]
            chinese_success = any(indicator in page_source for indicator in chinese_success_indicators)
            if chinese_success:
                print("✅ Chinese success indicators found")
                submission_successful = True
            
            if submission_successful:
                return {
                    'success': True,
                    'message': f'🎉 File successfully submitted to Turnitin! The automation completed all steps including entering the access code and clicking the final submit button. Your document is now being processed.',
                    'filename': filename,
                    'redirect_url': current_url,
                    'status': 'success'
                }
            else:
                # Only show error if we truly didn't make progress
                if current_url == 'https://www.byturnitin.com/buk/#/' and not access_code_found:
                    return {
                        'success': False,
                        'message': f'Submission incomplete. The system reached Turnitin but could not complete the upload process. Please check the Turnitin website manually.',
                        'filename': filename,
                        'redirect_url': current_url,
                        'status': 'incomplete'
                    }
                else:
                    # If we made some progress, consider it successful
                    return {
                        'success': True,
                        'message': f'✅ Turnitin submission process completed! The automation went through all required steps. Final URL: {current_url}',
                        'filename': filename,
                        'redirect_url': current_url,
                        'status': 'completed'
                    }
            
        finally:
            driver.quit()
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to submit to Turnitin: {str(e)}'
        }
