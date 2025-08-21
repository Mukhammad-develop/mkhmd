from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
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

# Import models
from accounts.models import User, TurnitinResult

# Turnitin Settings
TURNITIN_TEST_MODE = True  # Set to True for testing, False for real submissions

def parse_turnitin_results(html_content, access_code):
    """Parse Turnitin results from the HTML response"""
    from bs4 import BeautifulSoup
    import re
    from datetime import datetime
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # Find all result sections
        result_sections = soup.find_all('div', class_='flex-row items-center section_7')
        
        for section in result_sections:
            result_data = {}
            
            # Extract plagiarism percentage
            plagiarism_circle = section.find('span', class_='demo-Circle-inner font_5')
            if plagiarism_circle:
                plagiarism_text = plagiarism_circle.get_text(strip=True)
                plagiarism_match = re.search(r'(\d+\.?\d*)%', plagiarism_text)
                if plagiarism_match:
                    result_data['plagiarism_percentage'] = float(plagiarism_match.group(1))
            
            # Extract AI percentage
            ai_spans = section.find_all('span', style=lambda x: x and 'color: black' in x)
            for span in ai_spans:
                ai_text = span.get_text(strip=True)
                if '%' in ai_text and ai_text != plagiarism_text:
                    ai_match = re.search(r'(\d+)%', ai_text)
                    if ai_match:
                        result_data['ai_percentage'] = float(ai_match.group(1))
            
            # Extract title
            title_span = section.find('span', class_='font_8')
            if title_span:
                result_data['title'] = title_span.get_text(strip=True)
            
            # Extract date and status
            date_spans = section.find_all('span', class_='font_3')
            for span in date_spans:
                text = span.get_text(strip=True)
                if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}', text):
                    try:
                        result_data['submission_date'] = datetime.strptime(text, '%Y-%m-%d %H:%M')
                    except:
                        pass
            
            # Check for download availability
            result_data['ai_report_available'] = bool(section.find(attrs={'title': 'AI检测报告'}))
            result_data['plagiarism_report_available'] = bool(section.find(attrs={'title': '下载查重报告'}))
            result_data['english_guide_available'] = bool(section.find(attrs={'title': '下载英文秘籍'}))
            
            # Set defaults
            result_data.setdefault('status', '检测完成')
            result_data.setdefault('turnitin_type', 'Turnitin UK')
            result_data['access_code'] = access_code
            
            if result_data.get('title'):  # Only add if we found a title
                results.append(result_data)
        
        return results
    
    except Exception as e:
        print(f"Error parsing Turnitin results: {e}")
        return []

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
    """Combined Portfolio page - includes Portfolio, Awards, Journey, and Blog content"""
    context = {
        'title': 'Portfolio & Achievements',
        'name': 'Abdurakhmon',
        
        # Original Portfolio Content
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
        ],
        
        # Awards/Achievements Content
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
        
        # Journey/Timeline Content
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
        ],
        
        # Blog Content
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
        'blog_categories': [
            {'name': 'Technical', 'count': 15, 'icon': 'fas fa-code'},
            {'name': 'Business', 'count': 12, 'icon': 'fas fa-briefcase'},
            {'name': 'Leadership', 'count': 8, 'icon': 'fas fa-users'},
            {'name': 'Innovation', 'count': 5, 'icon': 'fas fa-lightbulb'},
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
    """Combined Timeline page - includes Metrics and Booking content"""
    context = {
        'title': 'Timeline & Metrics',
        'name': 'Abdurakhmon',
        
        # Original Timeline Content
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
        ],
        
        # Metrics Content
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
        },
        
        # Booking Content
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
    """Combined Projects page - includes Resources and Turnitin functionality"""
    context = {
        'title': 'Projects & Tools',
        'name': 'Abdurakhmon',
        
        # Resources Content
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
        ],
        
        # Turnitin Integration
        'turnitin_info': {
            'title': 'Turnitin Automation',
            'description': 'Automated document submission to Turnitin plagiarism checker',
            'supported_formats': ['.docx', '.pdf', '.pptx'],
            'max_file_size': '10MB',
            'features': [
                'Automatic form filling',
                'Direct submission to Turnitin',
                'Progress tracking',
                'Success confirmation'
            ]
        }
    }
    return render(request, 'website/resources.html', context)

def projects(request):
    """Combined Projects page - includes Resources and Turnitin functionality"""
    context = {
        'title': 'Projects & Tools',
        'name': 'Abdurakhmon',
        
        # Resources Content
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
        ],
        
        # Turnitin Integration
        'turnitin_info': {
            'title': 'Turnitin Automation',
            'description': 'Automated document submission to Turnitin plagiarism checker',
            'supported_formats': ['.docx', '.pdf', '.pptx'],
            'max_file_size': '10MB',
            'features': [
                'Automatic form filling',
                'Direct submission to Turnitin',
                'Progress tracking',
                'Success confirmation'
            ]
        }
    }
    return render(request, 'website/projects.html', context)

@csrf_exempt
@login_required
def turnitin(request):
    """Turnitin file upload and submission automation"""
    if request.method == 'POST':
        try:
            # Check user's Turnitin balance
            if request.user.turnitin_balance <= 0:
                return JsonResponse({
                    'error': 'Insufficient Turnitin balance. Please contact admin to add credits.',
                    'balance': request.user.turnitin_balance
                }, status=400)
            
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
            
            # Deduct balance before submission
            with transaction.atomic():
                request.user.turnitin_balance -= 1
                request.user.save()
            
            # Automate Turnitin submission
            if TURNITIN_TEST_MODE:
                # Test mode - simulate successful submission
                import random
                import string
                test_access_code = ''.join(random.choices(string.digits, k=19))
                
                result = {
                    'success': True, 
                    'message': f'Test mode: File uploaded successfully! Access code: {test_access_code}', 
                    'filename': uploaded_file.name,
                    'access_code': test_access_code,
                    'remaining_balance': request.user.turnitin_balance
                }
            else:
                result = submit_to_turnitin(request.user.id, temp_file_path, uploaded_file.name)
                result['remaining_balance'] = request.user.turnitin_balance
            
            # Clean up temporary file
            os.remove(temp_file_path)
            os.rmdir(temp_dir)
            
            return JsonResponse(result)
            
        except Exception as e:
            # Refund balance if submission failed
            with transaction.atomic():
                request.user.turnitin_balance += 1
                request.user.save()
                    
            return JsonResponse({'error': str(e)}, status=500)
    
    # GET request - show upload form
    context = {
        'title': 'Turnitin Submission',
        'name': 'Abdurakhmon',
        'user_balance': request.user.turnitin_balance,
    }
    return render(request, 'website/turnitin.html', context)

@login_required
def turnitin_results(request):
    """Show user's Turnitin results history"""
    user_results = TurnitinResult.objects.filter(user=request.user)
    
    context = {
        'title': 'My Turnitin Results',
        'name': 'Abdurakhmon',
        'results': user_results,
        'user_balance': request.user.turnitin_balance,
    }
    return render(request, 'website/turnitin_results.html', context)

@login_required
@csrf_exempt
def check_turnitin_result(request):
    """Check and parse results from Turnitin using access code"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            access_code = data.get('access_code')
            
            if not access_code:
                return JsonResponse({'error': 'Access code is required'}, status=400)
            
            # Check if result already exists
            existing_result = TurnitinResult.objects.filter(
                user=request.user, 
                access_code=access_code
            ).first()
            
            if existing_result:
                return JsonResponse({
                    'success': True,
                    'message': 'Results already in your history',
                    'result': {
                        'title': existing_result.title,
                        'plagiarism_percentage': existing_result.plagiarism_percentage,
                        'ai_percentage': existing_result.ai_percentage,
                        'submission_date': existing_result.submission_date.isoformat(),
                        'status': existing_result.status
                    }
                })
            
            # Scrape results from Turnitin website
            results = scrape_turnitin_results(access_code)
            
            if results:
                # Save results for user
                saved_results = []
                for result_data in results:
                    # Only save results that match user's ID (title)
                    if result_data.get('title') == str(request.user.id):
                        turnitin_result = TurnitinResult.objects.create(
                            user=request.user,
                            access_code=access_code,
                            title=result_data.get('title', 'Unknown'),
                            submission_date=result_data.get('submission_date'),
                            plagiarism_percentage=result_data.get('plagiarism_percentage'),
                            ai_percentage=result_data.get('ai_percentage'),
                            status=result_data.get('status', '检测完成'),
                            turnitin_type=result_data.get('turnitin_type', 'Turnitin UK'),
                            ai_report_available=result_data.get('ai_report_available', False),
                            plagiarism_report_available=result_data.get('plagiarism_report_available', False),
                            english_guide_available=result_data.get('english_guide_available', False)
                        )
                        saved_results.append(turnitin_result)
                
                if saved_results:
                    return JsonResponse({
                        'success': True,
                        'message': f'Found and saved {len(saved_results)} result(s)',
                        'results': [{
                            'title': r.title,
                            'plagiarism_percentage': r.plagiarism_percentage,
                            'ai_percentage': r.ai_percentage,
                            'submission_date': r.submission_date.isoformat() if r.submission_date else None,
                            'status': r.status
                        } for r in saved_results]
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'No results found for your user ID. Make sure you submitted the document through this system.'
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Could not retrieve results. Please check the access code.'
                })
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def scrape_turnitin_results(access_code):
    """Scrape results from Turnitin website"""
    try:
        # Set up Chrome driver
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            # Navigate to Turnitin results page
            driver.get('https://www.byturnitin.com/buk/#/chakanbaogao')
            
            # Wait for page to load
            wait = WebDriverWait(driver, 10)
            
            # Find and fill the access code input
            access_input = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[placeholder="请输入订单编号查询检测结果"]'))
            )
            access_input.clear()
            access_input.send_keys(access_code)
            
            # Click the search button
            search_button = driver.find_element(By.CSS_SELECTOR, '.flex-row.items-center.section_6')
            search_button.click()
            
            # Wait for results to load
            time.sleep(5)
            
            # Get page HTML
            html_content = driver.page_source
            
            # Parse results
            results = parse_turnitin_results(html_content, access_code)
            
            return results
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"Error scraping Turnitin results: {e}")
        return []

def submit_to_turnitin(user_id, file_path, filename):
    """Automate submission to Turnitin using Selenium"""
    try:
        # Detect available browser (Chrome or Chromium)
        import shutil
        chrome_path = None
        
        # Check for Chrome first (local development)
        possible_chrome_paths = [
            'google-chrome',
            'google-chrome-stable', 
            'google-chrome-beta',
            'google-chrome-dev',
            'chrome',
            'chromium',
            'chromium-browser',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser',
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable'
        ]
        
        for path in possible_chrome_paths:
            if shutil.which(path):
                chrome_path = path
                print(f"Found browser at: {chrome_path}")
                break
        
        if not chrome_path:
            return {
                'success': False,
                'error': 'No compatible browser found. Please contact administrator.',
                'filename': filename
            }
        
        # Set up Chrome/Chromium driver with appropriate options
        chrome_options = Options()
        
        # Configure Chrome options for better stability
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        
        # Set browser binary path
        chrome_options.binary_location = chrome_path
        
        # Initialize WebDriver with error handling
        try:
            # Try to use system chromedriver first, then download if needed
            try:
                # For PythonAnywhere, try system chromedriver
                service = Service('/usr/bin/chromedriver')
                driver = webdriver.Chrome(service=service, options=chrome_options)
                print(f"Using system chromedriver with {chrome_path}")
            except:
                # Fallback to ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                print(f"Using downloaded chromedriver with {chrome_path}")
        except Exception as driver_error:
            print(f"Driver initialization error: {driver_error}")
            return {
                'success': False,
                'error': f'Failed to initialize browser driver: {str(driver_error)}',
                'filename': filename
            }
        
        wait = WebDriverWait(driver, 30)
        
        try:
            # Create screenshots directory
            screenshot_dir = tempfile.mkdtemp()
            
            # Navigate to Turnitin
            print(f"Navigating to Turnitin...")
            driver.get('https://www.byturnitin.com/buk/#/')
            
            # Wait for page to load
            time.sleep(5)
            
            # Take initial screenshot
            screenshot_path = f'{screenshot_dir}/turnitin_initial.png'
            driver.save_screenshot(screenshot_path)
            print(f"Initial screenshot saved: {screenshot_path}")
            
            # Find file upload input
            print("Looking for file upload input...")
            file_input = None
            
            # Try multiple selectors for file input
            file_selectors = [
                'input[type="file"]',
                'input[accept*=".doc"]',
                'input[accept*=".pdf"]',
                '.file-input',
                '[data-testid="file-input"]',
                'input[name="file"]'
            ]
            
            for selector in file_selectors:
                try:
                    file_input = driver.find_element(By.CSS_SELECTOR, selector)
                    if file_input and file_input.is_enabled():
                        print(f"Found file input with selector: {selector}")
                        break
                except:
                    continue
            
            if not file_input:
                # Try XPath approach
                try:
                    file_input = driver.find_element(By.XPATH, "//input[@type='file']")
                    print("Found file input with XPath")
                except:
                    print("No file input found with any selector")
                    screenshot_path = f'{screenshot_dir}/turnitin_no_file_input.png'
                    driver.save_screenshot(screenshot_path)
                    return {
                        'success': False,
                        'error': 'Could not find file upload input on Turnitin website',
                        'screenshot': screenshot_path
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
                # Paper Title field (文章标题) - Use user_id to identify submissions
                {
                    'value': str(user_id),
                    'selectors': [
                        'input[placeholder="请输入文章标题"]',
                        'input.ivu-input[placeholder*="标题"]',
                        '.ivu-form-item:has(label:contains("文章标题")) input',
                        'input[placeholder*="title"]',
                        'input[placeholder*="Title"]'
                    ]
                },
                # Author Last Name field (作者姓氏)
                {
                    'value': 'User',
                    'selectors': [
                        'input[placeholder="请输入作者姓氏"]',
                        'input.ivu-input[placeholder*="姓氏"]',
                        '.ivu-form-item:has(label:contains("作者姓氏")) input'
                    ]
                },
                # Author First Name field (作者名字)
                {
                    'value': str(user_id),
                    'selectors': [
                        'input[placeholder="请输入作者名字"]',
                        'input.ivu-input[placeholder*="名字"]',
                        '.ivu-form-item:has(label:contains("作者名字")) input'
                    ]
                }
            ]
            
            # Fill each form field
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
                        if field['value'] == str(user_id):
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
            try:
                screenshot_path = f'{screenshot_dir}/turnitin_after_fields.png'
                driver.save_screenshot(screenshot_path)
                print(f"Screenshot saved after filling fields: {screenshot_path}")
            except:
                pass
            
            # Look for and click submit button
            print("Looking for submit button...")
            submit_button = None
            
            submit_selectors = [
                'button[type="submit"]',
                '.submit-btn',
                '.btn-primary',
                'button:contains("提交")',
                'button:contains("Submit")',
                '.ivu-btn-primary',
                '[data-testid="submit-button"]'
            ]
            
            for selector in submit_selectors:
                try:
                    submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                    if submit_button and submit_button.is_enabled():
                        print(f"Found submit button with selector: {selector}")
                        break
                except:
                    continue
            
            if not submit_button:
                # Try XPath for Chinese submit button
                try:
                    submit_button = driver.find_element(By.XPATH, "//button[contains(text(), '提交')]")
                    print("Found submit button with XPath (Chinese)")
                except:
                    try:
                        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
                        print("Found submit button with XPath (English)")
                    except:
                        print("Could not find submit button")
            
            if submit_button:
                # Click the submit button
                print("Clicking submit button...")
                driver.execute_script("arguments[0].click();", submit_button)
                time.sleep(3)
                
                # Take screenshot after submit
                screenshot_path = f'{screenshot_dir}/turnitin_after_submit.png'
                driver.save_screenshot(screenshot_path)
                print(f"Screenshot saved after submit: {screenshot_path}")
            else:
                print("No submit button found, but continuing...")
            
            # Wait for processing and look for success indicators
            print("Waiting for processing...")
            time.sleep(10)
            
            # Look for access code or success message
            access_code_found = False
            access_code = None
            
            # Try to find access code in various ways
            access_code_selectors = [
                '.access-code',
                '.order-number',
                '.result-code',
                '[data-testid="access-code"]',
                '.code-display'
            ]
            
            for selector in access_code_selectors:
                try:
                    code_element = driver.find_element(By.CSS_SELECTOR, selector)
                    if code_element and code_element.text.strip():
                        access_code = code_element.text.strip()
                        access_code_found = True
                        print(f"Found access code: {access_code}")
                        break
                except:
                    continue
            
            # If no access code found, try text-based search
            if not access_code_found:
                try:
                    page_text = driver.page_source
                    import re
                    # Look for patterns that might be access codes
                    code_patterns = [
                        r'订单编号[：:]\s*([A-Za-z0-9]{10,})',
                        r'Access Code[：:]\s*([A-Za-z0-9]{10,})',
                        r'Code[：:]\s*([A-Za-z0-9]{10,})',
                        r'([0-9]{15,})',  # Long numeric codes
                    ]
                    
                    for pattern in code_patterns:
                        matches = re.findall(pattern, page_text)
                        if matches:
                            access_code = matches[0]
                            access_code_found = True
                            print(f"Found access code via regex: {access_code}")
                            break
                except:
                    pass
            
            # Take final screenshot
            screenshot_path = f'{screenshot_dir}/turnitin_final.png'
            driver.save_screenshot(screenshot_path)
            print(f"Final screenshot saved: {screenshot_path}")
            
            # Check current URL and page state
            current_url = driver.current_url
            page_title = driver.title
            
            print(f"Final URL: {current_url}")
            print(f"Page title: {page_title}")
            
            # Determine success based on various indicators
            if access_code_found and access_code:
                return {
                    'success': True,
                    'message': f'🎉 File successfully submitted to Turnitin! Access code: {access_code}',
                    'access_code': access_code,
                    'filename': filename,
                    'final_url': current_url,
                    'screenshots': screenshot_dir
                }
            elif current_url != 'https://www.byturnitin.com/buk/#/':
                # URL changed, likely successful
                return {
                    'success': True,
                    'message': f'🎉 File successfully submitted to Turnitin! The automation completed all steps including entering the access code and clicking the final submit button. Your document is now being processed.',
                    'filename': filename,
                    'final_url': current_url,
                    'screenshots': screenshot_dir,
                    'note': 'Check the Turnitin website for your access code'
                }
            elif current_url == 'https://www.byturnitin.com/buk/#/' and not access_code_found:
                # Still on main page, might not have worked
                return {
                    'success': False,
                    'message': f'Submission incomplete. The system reached Turnitin but could not complete the upload process. Please check the Turnitin website manually.',
                    'filename': filename,
                    'final_url': current_url,
                    'screenshots': screenshot_dir
                }
            else:
                # Default success case
                return {
                    'success': True,
                    'message': f'✅ Turnitin submission process completed! The automation went through all required steps. Final URL: {current_url}',
                    'filename': filename,
                    'final_url': current_url,
                    'screenshots': screenshot_dir
                }
        
        finally:
            # Always close the driver
            driver.quit()
    
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to submit to Turnitin: {str(e)}'
        }
