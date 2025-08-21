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
# Chrome service not needed - PythonAnywhere has pre-installed ChromeDriver
import platform
import subprocess
import time
import tempfile

# Import models
from accounts.models import User, TurnitinResult

# Turnitin Settings
TURNITIN_TEST_MODE = getattr(settings, 'TURNITIN_TEST_MODE', True)
TURNITIN_CHROME_PATH = getattr(settings, 'TURNITIN_CHROME_PATH', None)

def parse_turnitin_results(html_content, access_code):
    """Parse Turnitin results from the HTML response with enhanced parsing"""
    from bs4 import BeautifulSoup
    import re
    from datetime import datetime
    
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        print("Starting HTML parsing...")
        
        # Look for the main results container
        results_container = soup.find('div', class_='resultdata')
        if not results_container:
            print("No resultdata container found, searching for individual results...")
            # Fallback: look for individual result sections
            result_sections = soup.find_all('div', class_='flex-row items-center section_7')
        else:
            print("Found resultdata container")
            result_sections = results_container.find_all('div', class_='flex-row items-center section_7')
        
        print(f"Found {len(result_sections)} result sections")
        
        for i, section in enumerate(result_sections):
            print(f"Processing result section {i+1}")
            result_data = {}
            
            # Extract plagiarism percentage from circular charts
            plagiarism_percentage = None
            ai_percentage = None
            
            # Look for circular chart elements
            chart_circles = section.find_all('div', class_='ivu-chart-circle-inner')
            for circle in chart_circles:
                # Get the percentage text
                percentage_span = circle.find('span', class_='demo-Circle-inner font_5')
                if percentage_span:
                    percentage_text = percentage_span.get_text(strip=True)
                    print(f"Found percentage text: {percentage_text}")
                    
                    # Check if this is plagiarism (重复率) or AI (AI比率)
                    label_span = circle.find('span', class_='font_9 text_8')
                    if label_span:
                        label_text = label_span.get_text(strip=True)
                        print(f"Label text: {label_text}")
                        
                        # Extract percentage value
                        percentage_match = re.search(r'(\d+\.?\d*)%?', percentage_text)
                        if percentage_match:
                            percentage_value = float(percentage_match.group(1))
                            
                            if '重复率' in label_text or 'plagiarism' in label_text.lower():
                                plagiarism_percentage = percentage_value
                                print(f"Found plagiarism percentage: {plagiarism_percentage}%")
                            elif 'AI比率' in label_text or 'ai' in label_text.lower():
                                ai_percentage = percentage_value
                                print(f"Found AI percentage: {ai_percentage}%")
            
            # Alternative method: look for percentage in spans with specific styles
            if plagiarism_percentage is None or ai_percentage is None:
                # Look for spans with percentage values
                percentage_spans = section.find_all('span', class_='demo-Circle-inner font_5')
                for span in percentage_spans:
                    text = span.get_text(strip=True)
                    percentage_match = re.search(r'(\d+\.?\d*)%', text)
                    if percentage_match:
                        value = float(percentage_match.group(1))
                        # Try to determine if it's plagiarism or AI based on context
                        parent = span.find_parent()
                        if parent:
                            parent_text = parent.get_text()
                            if '重复率' in parent_text and plagiarism_percentage is None:
                                plagiarism_percentage = value
                            elif 'AI比率' in parent_text and ai_percentage is None:
                                ai_percentage = value
            
            # Look for AI percentage in spans with black color style
            if ai_percentage is None:
                ai_spans = section.find_all('span', style=lambda x: x and 'color: black' in x)
                for span in ai_spans:
                    ai_text = span.get_text(strip=True)
                    if '%' in ai_text:
                        ai_match = re.search(r'(\d+)%', ai_text)
                        if ai_match:
                            ai_percentage = float(ai_match.group(1))
                            print(f"Found AI percentage from black span: {ai_percentage}%")
                            break
            
            # Extract title
            title = None
            title_spans = section.find_all('span', class_='font_8')
            for span in title_spans:
                text = span.get_text(strip=True)
                if text and text not in ['检测完成', 'Turnitin UK']:
                    title = text
                    print(f"Found title: {title}")
                    break
            
            # Extract date and status
            submission_date = None
            status = '检测完成'  # Default status
            
            date_spans = section.find_all('span', class_='font_3')
            for span in date_spans:
                text = span.get_text(strip=True)
                # Look for date pattern
                date_match = re.match(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2})', text)
                if date_match:
                    try:
                        submission_date = datetime.strptime(date_match.group(1), '%Y-%m-%d %H:%M')
                        print(f"Found submission date: {submission_date}")
                    except:
                        print(f"Could not parse date: {text}")
                        pass
            
            # Check for status in green colored spans
            status_spans = section.find_all('span', style=lambda x: x and 'color: green' in x)
            for span in status_spans:
                text = span.get_text(strip=True)
                if text:
                    status = text
                    print(f"Found status: {status}")
                    break
            
            # Extract Turnitin type
            turnitin_type = 'Turnitin UK'  # Default
            type_spans = section.find_all('span', class_='font_7')
            for span in type_spans:
                text = span.get_text(strip=True)
                if 'Turnitin' in text:
                    turnitin_type = text
                    print(f"Found Turnitin type: {turnitin_type}")
                    break
            
            # Check for download availability
            ai_report_available = bool(section.find(attrs={'title': 'AI检测报告'})) or bool(section.find(string=re.compile('下载AI报告')))
            plagiarism_report_available = bool(section.find(attrs={'title': '下载查重报告'})) or bool(section.find(string=re.compile('下载查重报告')))
            english_guide_available = bool(section.find(attrs={'title': '下载英文秘籍'})) or bool(section.find(string=re.compile('下载英文秘籍')))
            
            print(f"Download availability - AI: {ai_report_available}, Plagiarism: {plagiarism_report_available}, English: {english_guide_available}")
            
            # Build result data
            if title or plagiarism_percentage is not None or ai_percentage is not None:
                result_data = {
                    'access_code': access_code,
                    'title': title or 'Unknown Document',
                    'plagiarism_percentage': plagiarism_percentage,
                    'ai_percentage': ai_percentage,
                    'submission_date': submission_date,
                    'status': status,
                    'turnitin_type': turnitin_type,
                    'ai_report_available': ai_report_available,
                    'plagiarism_report_available': plagiarism_report_available,
                    'english_guide_available': english_guide_available
                }
                
                results.append(result_data)
                print(f"Added result: {result_data}")
            else:
                print(f"Skipping result section {i+1} - no meaningful data found")
        
        print(f"Parsing completed. Found {len(results)} valid results.")
        return results
    
    except Exception as e:
        print(f"Error parsing Turnitin results: {e}")
        import traceback
        traceback.print_exc()
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
            print(f"User {request.user.id} checking access code: {access_code}")
            results = scrape_turnitin_results(access_code)
            
            if results:
                # Save all results found (not just user ID matches)
                saved_results = []
                for result_data in results:
                    try:
                        # Check if this specific result already exists
                        existing = TurnitinResult.objects.filter(
                            user=request.user,
                            access_code=access_code,
                            title=result_data.get('title', 'Unknown')
                        ).first()
                        
                        if not existing:
                            turnitin_result = TurnitinResult.objects.create(
                                user=request.user,
                                access_code=access_code,
                                title=result_data.get('title', 'Unknown Document'),
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
                            print(f"Saved new result: {turnitin_result.title}")
                        else:
                            # Update existing result with latest data
                            existing.plagiarism_percentage = result_data.get('plagiarism_percentage')
                            existing.ai_percentage = result_data.get('ai_percentage')
                            existing.status = result_data.get('status', '检测完成')
                            existing.ai_report_available = result_data.get('ai_report_available', False)
                            existing.plagiarism_report_available = result_data.get('plagiarism_report_available', False)
                            existing.english_guide_available = result_data.get('english_guide_available', False)
                            existing.save()
                            saved_results.append(existing)
                            print(f"Updated existing result: {existing.title}")
                            
                    except Exception as e:
                        print(f"Error saving result: {e}")
                        continue
                
                if saved_results:
                    return JsonResponse({
                        'success': True,
                        'message': f'✅ Found and saved {len(saved_results)} result(s) for access code {access_code}',
                        'results': [{
                            'id': r.id,
                            'title': r.title,
                            'plagiarism_percentage': r.plagiarism_percentage,
                            'ai_percentage': r.ai_percentage,
                            'submission_date': r.submission_date.isoformat() if r.submission_date else None,
                            'status': r.status,
                            'turnitin_type': r.turnitin_type,
                            'ai_report_available': r.ai_report_available,
                            'plagiarism_report_available': r.plagiarism_report_available,
                            'english_guide_available': r.english_guide_available,
                            'access_code': r.access_code
                        } for r in saved_results]
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'message': '⚠️ Results were found but all were already in your history. Check your results list.'
                    })
            else:
                return JsonResponse({
                    'success': False,
                    'message': '❌ Could not retrieve results. Please check the access code and try again. The document may still be processing.'
                })
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def scrape_turnitin_results(access_code):
    """Scrape results from Turnitin website using PythonAnywhere-compatible setup"""
    try:
        # Set up Chrome options for PythonAnywhere
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Initialize WebDriver - PythonAnywhere has Chrome/ChromeDriver pre-installed
        driver = webdriver.Chrome(options=chrome_options)
        print(f"Scraping results for access code: {access_code}")
        
        try:
            # Create screenshots directory for debugging
            screenshot_dir = tempfile.mkdtemp()
            print(f"Results screenshots will be saved to: {screenshot_dir}")
            
            # Navigate to Turnitin results page
            print("Navigating to Turnitin results page...")
            driver.get('https://www.byturnitin.com/buk/#/chakanbaogao')
            
            # Wait for page to load
            wait = WebDriverWait(driver, 15)
            time.sleep(3)
            
            # Take initial screenshot
            screenshot_path = f'{screenshot_dir}/01_results_page_initial.png'
            driver.save_screenshot(screenshot_path)
            print(f"Initial results page screenshot: {screenshot_path}")
            
            # Find and fill the access code input
            print("Looking for access code input field...")
            access_input = None
            
            # Try multiple selectors for the input field
            input_selectors = [
                'input[placeholder="请输入订单编号查询检测结果"]',
                'input[placeholder*="订单编号"]',
                '.ivu-input[placeholder*="订单"]',
                'input[type="text"]'
            ]
            
            for selector in input_selectors:
                try:
                    access_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    if access_input and access_input.is_displayed():
                        print(f"Found access input with selector: {selector}")
                        break
                except:
                    continue
            
            if not access_input:
                print("Could not find access code input field")
                screenshot_path = f'{screenshot_dir}/02_no_input_found.png'
                driver.save_screenshot(screenshot_path)
                return []
            
            # Clear and enter access code
            access_input.clear()
            time.sleep(0.5)
            access_input.send_keys(access_code)
            print(f"Entered access code: {access_code}")
            
            # Screenshot after entering code
            screenshot_path = f'{screenshot_dir}/03_after_entering_code.png'
            driver.save_screenshot(screenshot_path)
            print(f"After entering code screenshot: {screenshot_path}")
            
            # Find and click the search button
            print("Looking for search button...")
            search_clicked = False
            
            # Try multiple selectors for search button
            search_selectors = [
                '.flex-row.items-center.section_6',
                'span:contains("查询结果")',
                '.font_2:contains("查询结果")',
                'img[src*="data:image/png"] + span'
            ]
            
            for selector in search_selectors:
                try:
                    if 'contains' in selector:
                        # Use XPath for contains
                        search_button = driver.find_element(By.XPATH, f"//span[contains(text(), '查询结果')]/..")
                    else:
                        search_button = driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if search_button and search_button.is_displayed():
                        driver.execute_script("arguments[0].click();", search_button)
                        print("Clicked search button")
                        search_clicked = True
                        break
                except Exception as e:
                    print(f"Search button selector failed: {selector} - {e}")
                    continue
            
            if not search_clicked:
                print("Could not find or click search button")
                screenshot_path = f'{screenshot_dir}/04_search_button_not_found.png'
                driver.save_screenshot(screenshot_path)
                return []
            
            # Wait for results to load
            print("Waiting for results to load...")
            time.sleep(8)
            
            # Screenshot after search
            screenshot_path = f'{screenshot_dir}/05_after_search.png'
            driver.save_screenshot(screenshot_path)
            print(f"After search screenshot: {screenshot_path}")
            
            # Check if results are loaded by looking for result data
            try:
                # Wait for result data to appear
                result_data = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.resultdata, .flex-row.items-center.section_7')))
                print("Results data found on page")
            except:
                print("No results data found, checking for error messages...")
                # Take screenshot of potential error state
                screenshot_path = f'{screenshot_dir}/06_no_results_found.png'
                driver.save_screenshot(screenshot_path)
            
            # Get page HTML for parsing
            html_content = driver.page_source
            
            # Take final screenshot
            screenshot_path = f'{screenshot_dir}/07_final_results_page.png'
            driver.save_screenshot(screenshot_path)
            print(f"Final results page screenshot: {screenshot_path}")
            
            # Parse results using enhanced parser
            print("Parsing results from HTML...")
            results = parse_turnitin_results(html_content, access_code)
            
            if results:
                print(f"Successfully parsed {len(results)} result(s)")
                for i, result in enumerate(results):
                    print(f"Result {i+1}: {result.get('title', 'No title')} - {result.get('plagiarism_percentage', 'N/A')}% plagiarism, {result.get('ai_percentage', 'N/A')}% AI")
            else:
                print("No results found in parsed HTML")
            
            return results
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"Error scraping Turnitin results: {e}")
        return []

def submit_to_turnitin(user_id, file_path, filename):
    """Automate submission to Turnitin using Selenium"""
    try:
        # Set up Chrome options for PythonAnywhere
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Initialize WebDriver - PythonAnywhere has Chrome/ChromeDriver pre-installed
        driver = webdriver.Chrome(options=chrome_options)
        print("Successfully initialized WebDriver")
        
        wait = WebDriverWait(driver, 30)
        
        try:
            # Create screenshots directory
            screenshot_dir = tempfile.mkdtemp()
            print(f"Screenshots will be saved to: {screenshot_dir}")
            
            # Navigate to Turnitin
            print(f"Navigating to Turnitin...")
            driver.get('https://www.byturnitin.com/buk/#/')
            
            # Wait for page to load
            time.sleep(5)
            
            # Take initial screenshot
            screenshot_path = f'{screenshot_dir}/01_turnitin_initial.png'
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
                    screenshot_path = f'{screenshot_dir}/02_no_file_input_error.png'
                    driver.save_screenshot(screenshot_path)
                    print(f"Error screenshot saved: {screenshot_path}")
                    return {
                        'success': False,
                        'error': 'Could not find file upload input on Turnitin website',
                        'screenshot': screenshot_path,
                        'debug_info': f'Screenshots available at: {screenshot_dir}'
                    }
            
            # Upload the file
            print(f"Uploading file: {file_path}")
            file_input.send_keys(file_path)
            time.sleep(3)
            
            # Screenshot after file upload
            screenshot_path = f'{screenshot_dir}/03_after_file_upload.png'
            driver.save_screenshot(screenshot_path)
            print(f"After file upload screenshot: {screenshot_path}")
            
            # Wait for file upload to process
            print("Waiting for file upload to process...")
            time.sleep(8)
            
            # Screenshot after processing wait
            screenshot_path = f'{screenshot_dir}/04_after_upload_processing.png'
            driver.save_screenshot(screenshot_path)
            print(f"After processing screenshot: {screenshot_path}")
            
            # Fill form fields - use user_id as title
            form_fields = [
                {
                    'value': str(user_id),
                    'selectors': ['input[placeholder="请输入文章标题"]'],
                    'name': 'title'
                },
                {
                    'value': 'User',
                    'selectors': ['input[placeholder="请输入作者姓氏"]'],
                    'name': 'lastname'
                },
                {
                    'value': str(user_id),
                    'selectors': ['input[placeholder="请输入作者名字"]'],
                    'name': 'firstname'
                }
            ]
            
            # Fill each form field
            fields_filled = 0
            for field in form_fields:
                field_filled = False
                for selector in field['selectors']:
                    try:
                        element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                        if element.is_displayed() and element.is_enabled():
                            element.clear()
                            time.sleep(0.5)
                            element.send_keys(field['value'])
                            print(f"Filled {field['name']} field with '{field['value']}'")
                            field_filled = True
                            fields_filled += 1
                            break
                    except Exception as e:
                        print(f"Could not fill {field['name']} field: {e}")
                        continue
                
                if not field_filled:
                    print(f"WARNING: Could not fill {field['name']} field")
            
            # Screenshot after filling fields
            screenshot_path = f'{screenshot_dir}/05_after_filling_fields.png'
            driver.save_screenshot(screenshot_path)
            print(f"After filling fields screenshot: {screenshot_path}")
            print(f"Successfully filled {fields_filled}/3 form fields")
            
            # Look for "下一步" (Next Step) button and click
            print("Looking for '下一步' (Next Step) button...")
            next_step_clicked = False
            try:
                # Try multiple selectors for the next step button
                next_step_selectors = [
                    'button.next_step',
                    'button:contains("下一步")',
                    '.next_step',
                    'button[class*="next_step"]'
                ]
                
                next_step_button = None
                for selector in next_step_selectors:
                    try:
                        next_step_button = driver.find_element(By.CSS_SELECTOR, selector)
                        if next_step_button and next_step_button.is_displayed() and next_step_button.is_enabled():
                            print(f"Found next step button with selector: {selector}")
                            break
                    except:
                        continue
                
                if not next_step_button:
                    # Try XPath approach
                    try:
                        next_step_button = driver.find_element(By.XPATH, "//button[contains(text(), '下一步')]")
                        print("Found next step button with XPath")
                    except:
                        print("Could not find next step button")
                
                if next_step_button and next_step_button.is_displayed() and next_step_button.is_enabled():
                    driver.execute_script("arguments[0].click();", next_step_button)
                    print("Clicked '下一步' (Next Step) button successfully")
                    next_step_clicked = True
                    time.sleep(5)
                else:
                    print("Next step button found but not clickable")
                    
            except Exception as e:
                print(f"Could not find or click next step button: {e}")
            
            # Screenshot after next step
            screenshot_path = f'{screenshot_dir}/06_after_next_step.png'
            driver.save_screenshot(screenshot_path)
            print(f"After next step screenshot: {screenshot_path}")
            
            if not next_step_clicked:
                print("WARNING: Could not proceed to next step")
                return {
                    'success': False,
                    'error': f'Could not find or click the "下一步" (Next Step) button',
                    'screenshots': screenshot_dir,
                    'debug_info': {
                        'fields_filled': f'{fields_filled}/3',
                        'next_step_clicked': next_step_clicked
                    }
                }
            
            # Wait for the order/payment page to load
            print("Waiting for order page to load...")
            time.sleep(8)
            
            # Screenshot of order page
            screenshot_path = f'{screenshot_dir}/07_order_page.png'
            driver.save_screenshot(screenshot_path)
            print(f"Order page screenshot: {screenshot_path}")
            
            # Look for the order number input field and enter the test access code
            print("Looking for order number input field...")
            access_code_entered = False
            test_access_code = "2884078633760879499"  # The provided test access code
            
            try:
                # Try multiple selectors for the order input
                order_input_selectors = [
                    'input[placeholder*="订单编号"]',
                    'input[placeholder*="请输入订单编号"]',
                    '.ivu-input[placeholder*="订单"]',
                    'input[type="text"]'  # Fallback to any text input
                ]
                
                order_input = None
                for selector in order_input_selectors:
                    try:
                        order_inputs = driver.find_elements(By.CSS_SELECTOR, selector)
                        for inp in order_inputs:
                            if inp.is_displayed() and inp.is_enabled():
                                # Check if this looks like the order input
                                placeholder = inp.get_attribute('placeholder') or ''
                                if '订单' in placeholder or '编号' in placeholder or not order_input:
                                    order_input = inp
                                    print(f"Found order input with selector: {selector}, placeholder: {placeholder}")
                                    break
                        if order_input:
                            break
                    except:
                        continue
                
                if order_input and order_input.is_displayed() and order_input.is_enabled():
                    order_input.clear()
                    time.sleep(0.5)
                    order_input.send_keys(test_access_code)
                    print(f"Entered access code: {test_access_code}")
                    access_code_entered = True
                    time.sleep(2)
                else:
                    print("Could not find order input field")
                    
            except Exception as e:
                print(f"Error entering access code: {e}")
            
            # Screenshot after entering access code
            screenshot_path = f'{screenshot_dir}/08_after_access_code.png'
            driver.save_screenshot(screenshot_path)
            print(f"After access code screenshot: {screenshot_path}")
            
            # Look for "立即检测" (Start Detection) button and click
            print("Looking for '立即检测' (Start Detection) button...")
            detection_clicked = False
            
            if access_code_entered:
                try:
                    # Try multiple selectors for the detection button
                    detection_selectors = [
                        'button:contains("立即检测")',
                        '.ivu-btn-primary:contains("立即检测")',
                        'button.ivu-btn-primary',
                        '.section_11'
                    ]
                    
                    detection_button = None
                    for selector in detection_selectors:
                        try:
                            if 'contains' in selector:
                                # Use XPath for contains
                                xpath_selector = f"//button[contains(text(), '立即检测')]"
                                detection_button = driver.find_element(By.XPATH, xpath_selector)
                            else:
                                detection_button = driver.find_element(By.CSS_SELECTOR, selector)
                            
                            if detection_button and detection_button.is_displayed() and detection_button.is_enabled():
                                print(f"Found detection button")
                                break
                        except:
                            continue
                    
                    if detection_button and detection_button.is_displayed() and detection_button.is_enabled():
                        driver.execute_script("arguments[0].click();", detection_button)
                        print("Clicked '立即检测' (Start Detection) button successfully")
                        detection_clicked = True
                        time.sleep(10)  # Wait for processing
                    else:
                        print("Detection button found but not clickable")
                        
                except Exception as e:
                    print(f"Could not find or click detection button: {e}")
            
            # Final screenshot
            screenshot_path = f'{screenshot_dir}/09_final_result.png'
            driver.save_screenshot(screenshot_path)
            print(f"Final screenshot saved: {screenshot_path}")
            
            # Get current URL and page info for debugging
            current_url = driver.current_url
            page_title = driver.title
            print(f"Final URL: {current_url}")
            print(f"Final page title: {page_title}")
            
            # Try to find any success indicators or new access codes
            success_found = False
            new_access_code = None
            
            try:
                page_text = driver.page_source
                import re
                
                # Look for success indicators
                success_patterns = [
                    r'检测完成',
                    r'提交成功',
                    r'订单.*成功',
                    r'success',
                    r'complete'
                ]
                
                for pattern in success_patterns:
                    if re.search(pattern, page_text, re.IGNORECASE):
                        success_found = True
                        print(f"Found success indicator: {pattern}")
                        break
                
                # Look for new access codes
                code_patterns = [
                    r'订单编号[：:]\s*([A-Za-z0-9]{10,})',
                    r'([0-9]{15,})',
                    r'Access Code[：:]\s*([A-Za-z0-9]{10,})',
                    r'Code[：:]\s*([A-Za-z0-9]{10,})'
                ]
                
                for pattern in code_patterns:
                    matches = re.findall(pattern, page_text)
                    for match in matches:
                        if match != test_access_code:  # Don't return the same code we entered
                            new_access_code = match
                            print(f"Found new access code: {new_access_code}")
                            break
                    if new_access_code:
                        break
                        
            except Exception as e:
                print(f"Error searching for success indicators: {e}")
            
            # Determine final result
            if detection_clicked and (success_found or current_url != 'https://www.byturnitin.com/buk/#/'):
                return {
                    'success': True,
                    'message': f'🎉 File successfully submitted to Turnitin! Used test access code: {test_access_code}',
                    'access_code': new_access_code or test_access_code,
                    'filename': filename,
                    'screenshots': screenshot_dir,
                    'debug_info': {
                        'fields_filled': f'{fields_filled}/3',
                        'next_step_clicked': next_step_clicked,
                        'access_code_entered': access_code_entered,
                        'detection_clicked': detection_clicked,
                        'success_found': success_found,
                        'final_url': current_url,
                        'page_title': page_title,
                        'test_access_code_used': test_access_code
                    }
                }
            elif not detection_clicked:
                return {
                    'success': False,
                    'error': f'Could not complete submission. Reached order page but could not click detection button.',
                    'filename': filename,
                    'screenshots': screenshot_dir,
                    'debug_info': {
                        'fields_filled': f'{fields_filled}/3',
                        'next_step_clicked': next_step_clicked,
                        'access_code_entered': access_code_entered,
                        'detection_clicked': detection_clicked,
                        'final_url': current_url,
                        'page_title': page_title,
                        'test_access_code_used': test_access_code
                    }
                }
            else:
                return {
                    'success': True,
                    'message': f'✅ File submitted! Process completed but final status unclear. Check screenshots.',
                    'filename': filename,
                    'screenshots': screenshot_dir,
                    'debug_info': {
                        'fields_filled': f'{fields_filled}/3',
                        'next_step_clicked': next_step_clicked,
                        'access_code_entered': access_code_entered,
                        'detection_clicked': detection_clicked,
                        'final_url': current_url,
                        'page_title': page_title,
                        'test_access_code_used': test_access_code,
                        'note': 'Process completed but success unclear'
                    }
                }
        
        finally:
            # Always close the driver
            driver.quit()
    
    except Exception as e:
        return {
            'success': False,
            'error': f'Failed to submit to Turnitin: {str(e)}'
        }
