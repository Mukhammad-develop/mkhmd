from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone
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
from accounts.models import User, TurnitinSubmission
from .models import Project

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
            
            # Check for status in colored spans - both green (completed) and red (ongoing)
            status = None
            
            # Check for completed status (green color)
            status_spans = section.find_all('span', style=lambda x: x and 'color: green' in x)
            for span in status_spans:
                text = span.get_text(strip=True)
                if text == '检测完成':
                    status = text
                    print(f"Found completed status: {status}")
                    break
            
            # Check for ongoing status (red color or specific text)
            if not status:
                red_status_spans = section.find_all('span', style=lambda x: x and 'color: red' in x)
                for span in red_status_spans:
                    text = span.get_text(strip=True)
                    if 'AI检测中' in text or '检测中' in text:
                        status = 'AI检测中...'
                        print(f"Found ongoing status: {status}")
                        break
            
            # If no status found in colored spans, check all spans for status text
            if not status:
                all_spans = section.find_all('span')
                for span in all_spans:
                    text = span.get_text(strip=True)
                    if text == '检测完成' or 'AI检测中' in text or '检测中' in text:
                        status = text
                        print(f"Found status in regular span: {status}")
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
            
            # Check for download availability based on the HTML structure you provided
            ai_report_available = bool(section.find(attrs={'title': 'AI检测报告'})) or bool(section.find(string=re.compile('下载AI报告')))
            plagiarism_report_available = bool(section.find(attrs={'title': '下载查重报告'})) or bool(section.find(string=re.compile('下载查重报告')))
            english_guide_available = bool(section.find(attrs={'title': '下载英文秘籍'})) or bool(section.find(string=re.compile('下载英文秘籍')))
            
            print(f"Download availability - AI: {ai_report_available}, Similarity: {plagiarism_report_available}, English: {english_guide_available}")
            
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
    """Software Developer & Web-Scraper Engineer Landing page"""
    
    # Get featured project (only one featured project for home page)
    featured_project = Project.objects.filter(is_featured=True, is_active=True).first()
    
    # Get coming soon projects (not featured, but active)
    coming_soon_projects = Project.objects.filter(
        is_active=True, 
        is_featured=False,
        status__in=['development', 'planning', 'research']
    )[:3]
    
    context = {
        'title': 'Software Developer & Web-Scraper Engineer',
        'name': 'Abdurakhmon',
        'tagline': 'Software Developer & Web-Scraping Specialist',
        'description': 'Building innovative software solutions and extracting valuable data through advanced web-scraping techniques',
        'email': 'abdurakhmon@mkhmd.uk',
        'github': 'https://github.com/mukhammad-develop',
        'linkedin': 'https://linkedin.com/in/abdurakhmon-dev',
        
        # Dynamic Projects
        'featured_project': featured_project,
        'coming_soon_projects': coming_soon_projects,
    }
    return render(request, 'website/home.html', context)

def portfolio(request):
    """GitHub-friendly Portfolio page - Web-Scraping Engineer focused"""
    
    # Get all active projects for portfolio (from database)
    all_portfolio_projects = Project.objects.filter(is_active=True).order_by('order', '-created_at')
    
    # Separate by category and feature status for different sections
    featured_projects = all_portfolio_projects.filter(is_featured=True)
    scraping_projects = all_portfolio_projects.filter(category='web_scraping')
    automation_projects = all_portfolio_projects.filter(category='automation')
    
    # Get GitHub projects from database (projects with GitHub URLs)
    github_projects_db = all_portfolio_projects.filter(
        github_url__isnull=False
    ).exclude(github_url='')
    
    # Format for template compatibility
    github_projects = []
    for project in github_projects_db:
        github_projects.append({
            'name': project.title,
            'description': project.description,
            'html_url': project.github_url,
            'homepage': project.demo_url,
            'language': project.get_technologies_list()[0] if project.get_technologies_list() else 'Python',
            'stars': 0,  # Can be updated if you track stars
            'forks': 0,  # Can be updated if you track forks
        })
    
    context = {
        'title': 'Portfolio & Projects',
        'name': 'Abdurakhmon',
        
        # Dynamic Projects from Database
        'dev_projects': featured_projects,
        'scraping_projects': scraping_projects,
        'all_projects': all_portfolio_projects,
        
        # GitHub Projects from Database
        'github_projects': github_projects,
        
        # GitHub Integration
        'github_stats': {
            'username': 'mukhammad-develop',
            'total_repos': github_projects_db.count(),
            'total_stars': 0,  # Can be calculated if tracking stars
            'total_commits': '2,847',
            'languages': list(set(tech for project in github_projects_db for tech in project.get_technologies_list()))[:6]
        },
        
        # Awards/Achievements Content - Web-Scraping Focused
        'certifications': [
            {'name': 'AWS Solutions Architect Professional', 'issuer': 'Amazon Web Services', 'year': '2024', 'icon': 'fab fa-aws'},
            {'name': 'Google Cloud Professional Developer', 'issuer': 'Google Cloud', 'year': '2023', 'icon': 'fab fa-google'},
            {'name': 'Certified Kubernetes Administrator', 'issuer': 'CNCF', 'year': '2023', 'icon': 'fas fa-dharmachakra'},
            {'name': 'Certified Ethical Hacker (CEH)', 'issuer': 'EC-Council', 'year': '2022', 'icon': 'fas fa-shield-alt'},
        ],
        'awards': [
            {'title': 'Best Web Scraping Innovation', 'organization': 'DataCon 2024', 'year': '2024'},
            {'title': 'Outstanding Data Engineering', 'organization': 'PyData Conference', 'year': '2023'},
            {'title': 'Top Contributor - Scrapy Framework', 'organization': 'Open Source Awards', 'year': '2022'},
        ],
        'testimonials': [
            {
                'text': 'Abdurakhmon built our entire data collection infrastructure, processing millions of records daily.',
                'author': 'Sarah Johnson',
                'role': 'CTO, DataCorp Inc.',
                'avatar': 'testimonial1.jpg'
            },
            {
                'text': 'His web scraping solutions increased our data accuracy by 300% while reducing costs.',
                'author': 'Michael Chen',
                'role': 'Head of Analytics, TechStartup',
                'avatar': 'testimonial2.jpg'
            }
        ],
        
        # Journey/Timeline Content - Web-Scraping Focused
        'timeline_events': [
            {
                'year': '2024',
                'title': 'Senior Web-Scraping Engineer',
                'description': 'Leading data extraction initiatives for enterprise clients with complex anti-bot systems',
                'type': 'technical',
                'icon': 'fas fa-robot',
                'achievements': ['10M+ Records/Day', '99.9% Success Rate', 'Zero Detection']
            },
            {
                'year': '2023',
                'title': 'Full-Stack Developer & Scraping Specialist',
                'description': 'Built comprehensive web scraping platforms serving Fortune 500 companies',
                'type': 'technical',
                'icon': 'fas fa-spider',
                'achievements': ['Multi-Platform Scraping', '50+ Websites', 'Real-time Processing']
            },
            {
                'year': '2022',
                'title': 'Data Engineering Consultant',
                'description': 'Specialized in web scraping and data pipeline architecture for various industries',
                'type': 'technical',
                'icon': 'fas fa-database',
                'achievements': ['5+ Industries Served', 'Custom Solutions', 'Scalable Architecture']
            },
            {
                'year': '2021',
                'title': 'Python Developer',
                'description': 'Focused on web scraping automation and data extraction projects',
                'type': 'technical',
                'icon': 'fas fa-laptop-code',
                'achievements': ['Automation Scripts', 'Data Pipelines', 'API Development']
            },
            {
                'year': '2020',
                'title': 'Computer Science Degree',
                'description': 'Graduated with honors, specialized in distributed systems and data engineering',
                'type': 'education',
                'icon': 'fas fa-graduation-cap',
                'achievements': ['Summa Cum Laude', 'Data Science Research', 'Dean\'s List']
            }
        ],
        
        # Blog Content - Web-Scraping Focused
        'featured_posts': [
            {
                'title': 'Advanced Anti-Bot Detection Bypass Techniques',
                'excerpt': 'Exploring modern methods to overcome sophisticated bot detection systems...',
                'category': 'Web Scraping',
                'read_time': '10 min read',
                'date': '2024-01-15',
                'image': 'blog1.jpg',
                'tags': ['Selenium', 'Anti-Bot', 'Proxy Management']
            },
            {
                'title': 'Building Scalable Web Scraping Architectures',
                'excerpt': 'Design patterns and best practices for enterprise-level data extraction systems...',
                'category': 'Architecture',
                'read_time': '12 min read',
                'date': '2024-01-10',
                'image': 'blog2.jpg',
                'tags': ['Scrapy', 'Microservices', 'Data Pipeline']
            }
        ],
        'blog_categories': [
            {'name': 'Web Scraping', 'count': 18, 'icon': 'fas fa-spider'},
            {'name': 'Data Engineering', 'count': 12, 'icon': 'fas fa-database'},
            {'name': 'Browser Automation', 'count': 10, 'icon': 'fas fa-robot'},
            {'name': 'Anti-Detection', 'count': 8, 'icon': 'fas fa-shield-alt'},
        ]
    }
    return render(request, 'website/portfolio.html', context)

def achievements(request):
    """Achievements and credentials page - Web-Scraping Engineer focused"""
    context = {
        'title': 'Achievements & Recognition',
        'name': 'Abdurakhmon',
        'certifications': [
            {'name': 'AWS Solutions Architect Professional', 'issuer': 'Amazon Web Services', 'year': '2024', 'icon': 'fab fa-aws'},
            {'name': 'Google Cloud Professional Developer', 'issuer': 'Google Cloud', 'year': '2023', 'icon': 'fab fa-google'},
            {'name': 'Certified Kubernetes Administrator', 'issuer': 'CNCF', 'year': '2023', 'icon': 'fas fa-dharmachakra'},
            {'name': 'Certified Ethical Hacker (CEH)', 'issuer': 'EC-Council', 'year': '2022', 'icon': 'fas fa-shield-alt'},
        ],
        'awards': [
            {'title': 'Best Web Scraping Innovation', 'organization': 'DataCon 2024', 'year': '2024'},
            {'title': 'Outstanding Data Engineering', 'organization': 'PyData Conference', 'year': '2023'},
            {'title': 'Top Contributor - Scrapy Framework', 'organization': 'Open Source Awards', 'year': '2022'},
        ],
        'testimonials': [
            {
                'text': 'Abdurakhmon built our entire data collection infrastructure, processing millions of records daily.',
                'author': 'Sarah Johnson',
                'role': 'CTO, DataCorp Inc.',
                'avatar': 'testimonial1.jpg'
            },
            {
                'text': 'His web scraping solutions increased our data accuracy by 300% while reducing costs.',
                'author': 'Michael Chen',
                'role': 'Head of Analytics, TechStartup',
                'avatar': 'testimonial2.jpg'
            }
        ],
        'metrics': [
            {'label': 'Scrapers Deployed', 'value': '150+', 'icon': 'fas fa-robot'},
            {'label': 'Data Sources Integrated', 'value': '300+', 'icon': 'fas fa-globe'},
            {'label': 'Records Processed Daily', 'value': '10M+', 'icon': 'fas fa-database'},
            {'label': 'Success Rate', 'value': '99.9%', 'icon': 'fas fa-chart-line'},
        ]
    }
    return render(request, 'website/achievements.html', context)

def timeline(request):
    """Combined Timeline page - Web-Scraping Engineer focused"""
    context = {
        'title': 'Timeline & Metrics',
        'name': 'Abdurakhmon',
        
        # Web-Scraping Timeline Content
        'timeline_events': [
            {
                'year': '2024',
                'title': 'Senior Web-Scraping Engineer',
                'description': 'Leading data extraction initiatives for enterprise clients with complex anti-bot systems',
                'type': 'technical',
                'icon': 'fas fa-robot',
                'achievements': ['10M+ Records/Day', '99.9% Success Rate', 'Zero Detection']
            },
            {
                'year': '2023',
                'title': 'Full-Stack Developer & Scraping Specialist',
                'description': 'Built comprehensive web scraping platforms serving Fortune 500 companies',
                'type': 'technical',
                'icon': 'fas fa-spider',
                'achievements': ['Multi-Platform Scraping', '50+ Websites', 'Real-time Processing']
            },
            {
                'year': '2022',
                'title': 'Data Engineering Consultant',
                'description': 'Specialized in web scraping and data pipeline architecture for various industries',
                'type': 'technical',
                'icon': 'fas fa-database',
                'achievements': ['5+ Industries Served', 'Custom Solutions', 'Scalable Architecture']
            },
            {
                'year': '2021',
                'title': 'Python Developer',
                'description': 'Focused on web scraping automation and data extraction projects',
                'type': 'technical',
                'icon': 'fas fa-laptop-code',
                'achievements': ['Automation Scripts', 'Data Pipelines', 'API Development']
            },
            {
                'year': '2020',
                'title': 'Computer Science Degree',
                'description': 'Graduated with honors, specialized in distributed systems and data engineering',
                'type': 'education',
                'icon': 'fas fa-graduation-cap',
                'achievements': ['Summa Cum Laude', 'Data Science Research', 'Dean\'s List']
            }
        ],
        
        # Web-Scraping Metrics Content
        'live_stats': [
            {'label': 'GitHub Commits', 'value': '2,847', 'trend': '+12%', 'icon': 'fab fa-github'},
            {'label': 'Data Records Scraped', 'value': '10M+', 'trend': '+25%', 'icon': 'fas fa-database'},
            {'label': 'Active Scrapers', 'value': '15', 'trend': '+3', 'icon': 'fas fa-robot'},
            {'label': 'Websites Monitored', 'value': '120+', 'trend': '+8%', 'icon': 'fas fa-globe'},
        ],
        'availability': {
            'status': 'Available',
            'next_slot': 'Jan 25, 2024',
            'response_time': '< 2 hours',
            'capacity': '75%'
        },
        
        # Web-Scraping Services
        'services': [
            {
                'name': 'Web Scraping Consultation',
                'duration': '60 minutes',
                'price': '$200',
                'description': 'Data extraction strategy, scraping architecture, anti-detection methods',
                'icon': 'fas fa-spider'
            },
            {
                'name': 'Custom Scraper Development',
                'duration': '90 minutes',
                'price': '$350',
                'description': 'Build custom scrapers, automation scripts, data pipeline setup',
                'icon': 'fas fa-code'
            },
            {
                'name': 'Scraping Infrastructure Review',
                'duration': '45 minutes',
                'price': '$150',
                'description': 'Performance optimization, scaling strategies, maintenance planning',
                'icon': 'fas fa-cogs'
            }
        ]
    }
    return render(request, 'website/timeline.html', context)


def schedule(request):
    """Schedule & Booking page - View my availability and book time"""
    from datetime import datetime, timedelta
    from .models import TimeSlot, Booking
    
    # Get all active time slots grouped by weekday
    time_slots = TimeSlot.objects.filter(is_active=True).order_by('weekday', 'start_time')
    
    # Get upcoming bookings for the next 30 days
    today = timezone.now().date()
    upcoming_bookings = Booking.objects.filter(
        date__gte=today,
        date__lte=today + timedelta(days=30),
        status__in=['confirmed', 'pending']
    ).order_by('date', 'start_time')
    
    # Organize time slots by weekday
    slots_by_day = {}
    for slot in time_slots:
        day_name = slot.get_weekday_display()
        if day_name not in slots_by_day:
            slots_by_day[day_name] = []
        slots_by_day[day_name].append(slot)
    
    context = {
        'title': 'Schedule & Booking',
        'name': 'Abdurakhmon',
        'time_slots': time_slots,
        'slots_by_day': slots_by_day,
        'upcoming_bookings': upcoming_bookings,
        'booking_types': [
            {
                'value': 'consultation',
                'name': 'Consultation',
                'description': 'Technical consultation and advice',
                'duration': '60 minutes',
                'icon': 'fas fa-comments'
            },
            {
                'value': 'project_discussion',
                'name': 'Project Discussion',
                'description': 'Discuss potential projects and collaborations',
                'duration': '60-90 minutes',
                'icon': 'fas fa-handshake'
            },
            {
                'value': 'technical_support',
                'name': 'Technical Support',
                'description': 'Get help with existing projects',
                'duration': '30-60 minutes',
                'icon': 'fas fa-life-ring'
            },
            {
                'value': 'collaboration',
                'name': 'Collaboration',
                'description': 'Explore collaboration opportunities',
                'duration': '45-60 minutes',
                'icon': 'fas fa-users'
            },
        ]
    }
    return render(request, 'website/schedule.html', context)


@csrf_exempt
def book_appointment(request):
    """Handle appointment booking submissions"""
    from .models import Booking
    from datetime import datetime
    import json
    
    if request.method == 'POST':
        try:
            # Parse JSON data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
            
            # Create booking
            booking = Booking.objects.create(
                name=data.get('name'),
                email=data.get('email'),
                phone=data.get('phone', ''),
                company=data.get('company', ''),
                date=data.get('date'),
                start_time=data.get('start_time'),
                end_time=data.get('end_time'),
                duration_minutes=int(data.get('duration_minutes', 60)),
                subject=data.get('subject'),
                message=data.get('message'),
                booking_type=data.get('booking_type', 'consultation'),
                status='pending'
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Booking request submitted successfully! I will confirm shortly.',
                'booking_id': booking.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            }, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def blog(request):
    """Blog and insights page - Web-Scraping Engineer focused"""
    context = {
        'title': 'Insights & Thoughts',
        'name': 'Abdurakhmon',
        'featured_posts': [
            {
                'title': 'Advanced Anti-Bot Detection Bypass Techniques',
                'excerpt': 'Exploring modern methods to overcome sophisticated bot detection systems...',
                'category': 'Web Scraping',
                'read_time': '10 min read',
                'date': '2024-01-15',
                'image': 'blog1.jpg',
                'tags': ['Selenium', 'Anti-Bot', 'Proxy Management']
            },
            {
                'title': 'Building Scalable Web Scraping Architectures',
                'excerpt': 'Design patterns and best practices for enterprise-level data extraction systems...',
                'category': 'Architecture',
                'read_time': '12 min read',
                'date': '2024-01-10',
                'image': 'blog2.jpg',
                'tags': ['Scrapy', 'Microservices', 'Data Pipeline']
            }
        ],
        'categories': [
            {'name': 'Web Scraping', 'count': 18, 'icon': 'fas fa-spider'},
            {'name': 'Data Engineering', 'count': 12, 'icon': 'fas fa-database'},
            {'name': 'Browser Automation', 'count': 10, 'icon': 'fas fa-robot'},
            {'name': 'Anti-Detection', 'count': 8, 'icon': 'fas fa-shield-alt'},
        ]
    }
    return render(request, 'website/blog.html', context)

def metrics(request):
    """Live metrics dashboard - Web-Scraping Engineer focused"""
    context = {
        'title': 'Live Metrics Dashboard',
        'name': 'Abdurakhmon',
        'live_stats': [
            {'label': 'GitHub Commits', 'value': '2,847', 'trend': '+12%', 'icon': 'fab fa-github'},
            {'label': 'Data Records Scraped', 'value': '10M+', 'trend': '+25%', 'icon': 'fas fa-database'},
            {'label': 'Active Scrapers', 'value': '15', 'trend': '+3', 'icon': 'fas fa-robot'},
            {'label': 'Websites Monitored', 'value': '120+', 'trend': '+8%', 'icon': 'fas fa-globe'},
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
    """Web-Scraping consultation booking system"""
    context = {
        'title': 'Book Consultation',
        'name': 'Abdurakhmon',
        'services': [
            {
                'name': 'Web Scraping Consultation',
                'duration': '60 minutes',
                'price': '$200',
                'description': 'Data extraction strategy, scraping architecture, anti-detection methods',
                'icon': 'fas fa-spider'
            },
            {
                'name': 'Custom Scraper Development',
                'duration': '90 minutes',
                'price': '$350',
                'description': 'Build custom scrapers, automation scripts, data pipeline setup',
                'icon': 'fas fa-code'
            },
            {
                'name': 'Scraping Infrastructure Review',
                'duration': '45 minutes',
                'price': '$150',
                'description': 'Performance optimization, scaling strategies, maintenance planning',
                'icon': 'fas fa-cogs'
            }
        ]
    }
    return render(request, 'website/booking.html', context)

def resources(request):
    """Web-Scraping Resources and Tools page"""
    context = {
        'title': 'Web-Scraping Resources',
        'name': 'Abdurakhmon',
        
        # Web-Scraping Tools
        'tools': [
            {
                'name': 'Web Scraping Framework',
                'description': 'Custom framework for building scalable web scrapers with anti-detection',
                'type': 'Framework',
                'icon': 'fas fa-spider'
            },
            {
                'name': 'Proxy Rotation Manager',
                'description': 'Advanced proxy management system with health monitoring and rotation',
                'type': 'Tool',
                'icon': 'fas fa-shield-alt'
            },
            {
                'name': 'CAPTCHA Solver Integration',
                'description': 'Automated CAPTCHA solving with multiple service providers',
                'type': 'Service',
                'icon': 'fas fa-puzzle-piece'
            },
            {
                'name': 'Data Pipeline Orchestrator',
                'description': 'Manage and monitor complex data extraction workflows',
                'type': 'Platform',
                'icon': 'fas fa-cogs'
            }
        ],
        'downloads': [
            {
                'title': 'Web Scraping Best Practices Guide',
                'type': 'PDF Guide',
                'pages': '75 pages',
                'downloads': '2,500+',
                'icon': 'fas fa-file-pdf'
            },
            {
                'title': 'Anti-Detection Techniques Handbook',
                'type': 'PDF Manual',
                'pages': '45 pages',
                'downloads': '1,800+',
                'icon': 'fas fa-shield-alt'
            },
            {
                'title': 'Scrapy Framework Templates',
                'type': 'Code Templates',
                'pages': '20 templates',
                'downloads': '3,200+',
                'icon': 'fas fa-code'
            }
        ],
        
        # Turnitin Integration (keeping existing functionality)
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
    """Combined Projects page - All active projects"""
    
    # Fetch live GitHub projects
    github_projects = fetch_github_projects('mukhammad-develop')
    
    # Get ALL active projects from database (ordered by order field, then by creation date)
    all_projects = Project.objects.filter(is_active=True).order_by('order', '-created_at')
    
    # Get Turnitin project specifically (for special section)
    turnitin_project = all_projects.filter(slug='turnitin-automation-system').first()
    
    context = {
        'title': 'Projects & Tools',
        'name': 'Abdurakhmon',
        
        # All Active Projects
        'all_projects': all_projects,
        'turnitin_project': turnitin_project,
        
        # Live GitHub Projects
        'github_projects': github_projects,
        
        # GitHub Stats
        'github_stats': {
            'username': 'mukhammad-develop',
            'total_repos': len(github_projects),
            'total_stars': sum(p.get('stars', 0) for p in github_projects),
            'total_commits': '2,847',
            'languages': list(set(p.get('language', 'Unknown') for p in github_projects if p.get('language')))[:6]
        },
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
            
            # Create new TurnitinSubmission record with next submission ID
            with transaction.atomic():
                # Deduct balance before submission
                request.user.turnitin_balance -= 1
                request.user.save()
                
                # Create new submission record
                submission = TurnitinSubmission.objects.create(
                    submission_id=TurnitinSubmission.get_next_submission_id(),
                    owner=request.user,
                    submission_status=False  # Default to ongoing
                )
            
            # Automate Turnitin submission using submission_id as title
            if TURNITIN_TEST_MODE:
                # Test mode - simulate successful submission
                import random
                import string
                test_access_code = ''.join(random.choices(string.digits, k=19))
                
                result = {
                    'success': True, 
                    'message': f'Test mode: File uploaded successfully! Submission ID: {submission.submission_id}, Access code: {test_access_code}', 
                    'filename': uploaded_file.name,
                    'access_code': test_access_code,
                    'submission_id': submission.submission_id,
                    'remaining_balance': request.user.turnitin_balance
                }
            else:
                result = submit_to_turnitin(submission.submission_id, temp_file_path, uploaded_file.name)
                result['submission_id'] = submission.submission_id
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
    """Show user's Turnitin submissions - automatically check for updates from Turnitin website"""
    
    print(f"Fetching Turnitin submissions for user {request.user.id}")
    
    # Get all user's submissions
    user_submissions = TurnitinSubmission.objects.filter(
        owner=request.user
    ).order_by('-created_at')
    
    # Check for ongoing submissions that need status updates
    ongoing_submissions = user_submissions.filter(submission_status=False)
    
    if ongoing_submissions.exists():
        print(f"Found {ongoing_submissions.count()} ongoing submissions to check")
        
        # For each ongoing submission, check if it has an access_code to query
        for submission in ongoing_submissions:
            if submission.access_code:
                try:
                    # Try to get updated results from Turnitin
                    scraped_results = scrape_turnitin_results(submission.access_code)
                    
                    if scraped_results:
                        # Look for this specific submission_id in the results
                        submission_id_str = str(submission.submission_id)
                        matching_results = [r for r in scraped_results if r.get('title') == submission_id_str]
                        
                        if matching_results:
                            result_data = matching_results[0]  # Take the first match
                            
                            # Update submission with new data
                            if result_data.get('plagiarism_percentage') is not None:
                                submission.similarity_percentage = str(result_data.get('plagiarism_percentage'))
                            if result_data.get('ai_percentage') is not None:
                                submission.ai_percentage = str(result_data.get('ai_percentage'))
                            
                            # Check if status changed to completed
                            if result_data.get('status') == '检测完成':
                                submission.submission_status = True
                                print(f"Submission {submission.submission_id} marked as completed")
                            
                            submission.submission_date = result_data.get('submission_date') or submission.submission_date
                            submission.save()
                            
                except Exception as e:
                    print(f"Error checking submission {submission.submission_id}: {e}")
                    continue
    
    context = {
        'title': 'My Turnitin Submissions',
        'name': 'Abdurakhmon',
        'submissions': user_submissions,
        'user_balance': request.user.turnitin_balance,
        'ongoing_count': ongoing_submissions.count(),
        'completed_count': user_submissions.filter(submission_status=True).count(),
        'total_submissions': user_submissions.count()
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
            existing_result = TurnitinSubmission.objects.filter(
                owner=request.user, 
                access_code=access_code
            ).first()
            
            if existing_result:
                return JsonResponse({
                    'success': True,
                    'message': 'Results already in your history',
                    'result': {
                        'submission_id': existing_result.submission_id,
                        'similarity_percentage': existing_result.similarity_percentage,
                        'ai_percentage': existing_result.ai_percentage,
                        'submission_date': existing_result.submission_date.isoformat() if existing_result.submission_date else None,
                        'status': 'completed' if existing_result.submission_status else 'ongoing'
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
                        # Get submission_id from title (assuming title contains submission_id)
                        title = result_data.get('title', '')
                        try:
                            submission_id = int(title) if title.isdigit() else None
                        except (ValueError, TypeError):
                            submission_id = None
                        
                        if not submission_id:
                            print(f"Skipping result with invalid submission_id: {title}")
                            continue
                        
                        # Check if this specific submission already exists
                        existing = TurnitinSubmission.objects.filter(
                            owner=request.user,
                            submission_id=submission_id
                        ).first()
                        
                        if not existing:
                            # Create new submission if it doesn't exist
                            turnitin_submission = TurnitinSubmission.objects.create(
                                submission_id=submission_id,
                                owner=request.user,
                                access_code=access_code,
                                submission_date=result_data.get('submission_date'),
                                similarity_percentage=str(result_data.get('plagiarism_percentage', '')) if result_data.get('plagiarism_percentage') is not None else '',
                                ai_percentage=str(result_data.get('ai_percentage', '')) if result_data.get('ai_percentage') is not None else '',
                                submission_status=result_data.get('status') == '检测完成',  # True if completed
                                turnitin_type=result_data.get('turnitin_type', 'Turnitin UK')
                            )
                            saved_results.append(turnitin_submission)
                            print(f"Saved new submission: {turnitin_submission.submission_id}")
                        else:
                            # Update existing submission with latest data
                            existing.access_code = access_code
                            existing.submission_date = result_data.get('submission_date') or existing.submission_date
                            if result_data.get('plagiarism_percentage') is not None:
                                existing.similarity_percentage = str(result_data.get('plagiarism_percentage'))
                            if result_data.get('ai_percentage') is not None:
                                existing.ai_percentage = str(result_data.get('ai_percentage'))
                            existing.submission_status = result_data.get('status') == '检测完成'
                            existing.turnitin_type = result_data.get('turnitin_type', 'Turnitin UK')
                            existing.save()
                            saved_results.append(existing)
                            print(f"Updated existing submission: {existing.submission_id}")
                            
                    except Exception as e:
                        print(f"Error saving result: {e}")
                        continue
                
                if saved_results:
                    return JsonResponse({
                        'success': True,
                        'message': f'✅ Found and saved {len(saved_results)} submission(s) for access code {access_code}',
                        'results': [{
                            'id': r.id,
                            'submission_id': r.submission_id,
                            'similarity_percentage': r.similarity_percentage,
                            'ai_percentage': r.ai_percentage,
                            'submission_date': r.submission_date.isoformat() if r.submission_date else None,
                            'status': 'completed' if r.submission_status else 'ongoing',
                            'turnitin_type': r.turnitin_type,
                            'access_code': r.access_code,
                            'similarity_file_available': bool(r.similarity_file),
                            'ai_file_available': bool(r.ai_file)
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


def check_ongoing_submissions():
    """
    Check all ongoing submissions every 3 minutes to see if they're completed.
    This function should be called by a scheduled task (like celery or cron).
    """
    ongoing_submissions = TurnitinSubmission.objects.filter(submission_status=False)
    
    if not ongoing_submissions.exists():
        print("No ongoing submissions to check")
        return
    
    print(f"Checking {ongoing_submissions.count()} ongoing submissions...")
    
    # Group submissions by access_code to minimize website scraping
    access_code_groups = {}
    for submission in ongoing_submissions:
        if submission.access_code:
            if submission.access_code not in access_code_groups:
                access_code_groups[submission.access_code] = []
            access_code_groups[submission.access_code].append(submission)
    
    for access_code, submissions in access_code_groups.items():
        try:
            print(f"Checking access code: {access_code} for {len(submissions)} submissions")
            results = scrape_turnitin_results(access_code)
            
            if results:
                for submission in submissions:
                    submission_id_str = str(submission.submission_id)
                    
                    # Find matching result for this submission
                    matching_results = [r for r in results if r.get('title') == submission_id_str]
                    
                    if matching_results:
                        result_data = matching_results[0]
                        
                        # Check if status is still ongoing (AI检测中...)
                        status = result_data.get('status', '')
                        if status == 'AI检测中...':
                            print(f"Submission {submission.submission_id} still ongoing")
                            continue
                        
                        # Check if status is completed (检测完成)
                        if status == '检测完成':
                            print(f"Submission {submission.submission_id} completed! Updating...")
                            
                            # Update submission with results
                            if result_data.get('plagiarism_percentage') is not None:
                                submission.similarity_percentage = str(result_data.get('plagiarism_percentage'))
                            if result_data.get('ai_percentage') is not None:
                                submission.ai_percentage = str(result_data.get('ai_percentage'))
                            
                            submission.submission_status = True  # Mark as completed
                            submission.submission_date = result_data.get('submission_date') or submission.submission_date
                            submission.save()
                            
                            # Download similarity and AI files if available
                            try:
                                download_results = download_turnitin_files(submission.submission_id, access_code)
                                if download_results.get('success'):
                                    save_downloaded_files_to_submission(submission, download_results)
                                    print(f"Successfully downloaded files for submission {submission.submission_id}")
                                else:
                                    print(f"Could not download files for submission {submission.submission_id}: {download_results.get('error', 'Unknown error')}")
                            except Exception as e:
                                print(f"Error downloading files for submission {submission.submission_id}: {e}")
                            
                        else:
                            print(f"Submission {submission.submission_id} has unknown status: {status}")
                    else:
                        print(f"No matching result found for submission {submission.submission_id}")
            else:
                print(f"No results found for access code: {access_code}")
                
        except Exception as e:
            print(f"Error checking access code {access_code}: {e}")
            continue
    
    print("Finished checking ongoing submissions")


@csrf_exempt
def check_submissions_status(request):
    """
    Manual endpoint to trigger checking of ongoing submissions.
    This can be called by a cron job or scheduled task.
    """
    if request.method == 'POST':
        try:
            check_ongoing_submissions()
            return JsonResponse({
                'success': True,
                'message': 'Submission status check completed'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
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

def submit_to_turnitin(submission_id, file_path, filename):
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
            
            # Fill form fields - use submission_id as title
            form_fields = [
                {
                    'value': str(submission_id),
                    'selectors': ['input[placeholder="请输入文章标题"]'],
                    'name': 'title'
                },
                {
                    'value': 'User',
                    'selectors': ['input[placeholder="请输入作者姓氏"]'],
                    'name': 'lastname'
                },
                {
                    'value': str(submission_id),
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

def download_turnitin_files(submission_id, access_code):
    """
    Download similarity and AI files for a completed submission
    Returns dict with download results
    """
    try:
        # Set up Chrome options for file downloads
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # Set download directory
        download_dir = tempfile.mkdtemp()
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        driver = webdriver.Chrome(options=chrome_options)
        print(f"Downloading files for submission {submission_id} with access code {access_code}")
        
        try:
            # Navigate to Turnitin results page
            driver.get('https://www.byturnitin.com/buk/#/chakanbaogao')
            time.sleep(3)
            
            # Find and fill access code
            wait = WebDriverWait(driver, 15)
            access_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[placeholder="请输入订单编号查询检测结果"]')))
            access_input.clear()
            access_input.send_keys(access_code)
            
            # Click search
            search_button = driver.find_element(By.XPATH, "//span[contains(text(), '查询结果')]/..")
            driver.execute_script("arguments[0].click();", search_button)
            time.sleep(5)
            
            # Find the submission section by looking for the submission_id in titles
            submission_found = False
            sections = driver.find_elements(By.CSS_SELECTOR, '.flex-row.items-center.section_7')
            
            for section in sections:
                try:
                    # Look for title spans
                    title_spans = section.find_elements(By.CSS_SELECTOR, 'span.font_8')
                    for span in title_spans:
                        if span.text.strip() == str(submission_id):
                            submission_found = True
                            print(f"Found submission {submission_id} section")
                            
                            # Look for download buttons in this section
                            download_results = {
                                'similarity_file': None,
                                'ai_file': None,
                                'success': False
                            }
                            
                            # Try to download similarity report (下载查重报告)
                            try:
                                similarity_btn = section.find_element(By.XPATH, ".//span[contains(text(), '下载查重报告')]/..")
                                if similarity_btn:
                                    print("Clicking similarity report download...")
                                    driver.execute_script("arguments[0].click();", similarity_btn)
                                    time.sleep(3)
                                    
                                    # Check if file was downloaded
                                    downloaded_files = os.listdir(download_dir)
                                    if downloaded_files:
                                        similarity_file = downloaded_files[-1]  # Get latest file
                                        download_results['similarity_file'] = os.path.join(download_dir, similarity_file)
                                        print(f"Downloaded similarity report: {similarity_file}")
                            except Exception as e:
                                print(f"Could not download similarity report: {e}")
                            
                            # Try to download AI report (下载AI报告)
                            try:
                                ai_btn = section.find_element(By.XPATH, ".//span[contains(text(), '下载AI报告')]/..")
                                if ai_btn:
                                    print("Clicking AI report download...")
                                    driver.execute_script("arguments[0].click();", ai_btn)
                                    time.sleep(3)
                                    
                                    # Check if file was downloaded
                                    downloaded_files = os.listdir(download_dir)
                                    new_files = [f for f in downloaded_files if f not in (download_results.get('similarity_file', '').split('/')[-1:] or [])]
                                    if new_files:
                                        ai_file = new_files[-1]  # Get latest new file
                                        download_results['ai_file'] = os.path.join(download_dir, ai_file)
                                        print(f"Downloaded AI report: {ai_file}")
                            except Exception as e:
                                print(f"Could not download AI report: {e}")
                            
                            download_results['success'] = bool(download_results['similarity_file'] or download_results['ai_file'])
                            return download_results
                            
                except Exception as e:
                    continue
            
            if not submission_found:
                print(f"Submission {submission_id} not found in results")
                return {'success': False, 'error': 'Submission not found'}
                
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"Error downloading files for submission {submission_id}: {e}")
        return {'success': False, 'error': str(e)}


def save_downloaded_files_to_submission(submission, download_results):
    """
    Save downloaded files to the TurnitinSubmission model
    """
    try:
        from django.core.files import File
        from django.core.files.storage import default_storage
        
        if download_results.get('similarity_file'):
            similarity_path = download_results['similarity_file']
            if os.path.exists(similarity_path):
                with open(similarity_path, 'rb') as f:
                    file_name = f"similarity_{submission.submission_id}_{os.path.basename(similarity_path)}"
                    submission.similarity_file.save(file_name, File(f), save=False)
                print(f"Saved similarity file for submission {submission.submission_id}")
        
        if download_results.get('ai_file'):
            ai_path = download_results['ai_file']
            if os.path.exists(ai_path):
                with open(ai_path, 'rb') as f:
                    file_name = f"ai_{submission.submission_id}_{os.path.basename(ai_path)}"
                    submission.ai_file.save(file_name, File(f), save=False)
                print(f"Saved AI file for submission {submission.submission_id}")
        
        submission.save()
        
        # Clean up temporary files
        if download_results.get('similarity_file') and os.path.exists(download_results['similarity_file']):
            os.remove(download_results['similarity_file'])
        if download_results.get('ai_file') and os.path.exists(download_results['ai_file']):
            os.remove(download_results['ai_file'])
            
        return True
        
    except Exception as e:
        print(f"Error saving files for submission {submission.submission_id}: {e}")
        return False

def fetch_github_projects(username='mukhammad-develop'):
    """Fetch GitHub projects dynamically using GitHub API"""
    try:
        # GitHub API endpoint for user repositories
        url = f'https://api.github.com/users/{username}/repos'
        
        # Add parameters to get more information and sort by recent activity
        params = {
            'sort': 'updated',
            'direction': 'desc',
            'per_page': 20,
            'type': 'public'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            repos = response.json()
            
            # Filter and format repositories
            github_projects = []
            for repo in repos:
                if not repo.get('fork', False):  # Skip forked repositories
                    project = {
                        'title': repo.get('name', '').replace('-', ' ').title(),
                        'description': repo.get('description', 'No description available'),
                        'github_url': repo.get('html_url', ''),
                        'homepage': repo.get('homepage', ''),
                        'language': repo.get('language', 'Unknown'),
                        'stars': repo.get('stargazers_count', 0),
                        'forks': repo.get('forks_count', 0),
                        'updated_at': repo.get('updated_at', ''),
                        'created_at': repo.get('created_at', ''),
                        'topics': repo.get('topics', []),
                        'size': repo.get('size', 0),
                        'open_issues': repo.get('open_issues_count', 0)
                    }
                    github_projects.append(project)
            
            return github_projects[:12]  # Return top 12 projects
        else:
            print(f"GitHub API error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error fetching GitHub projects: {e}")
        return []

@csrf_exempt
def github_projects(request):
    """GitHub projects API endpoint"""
    if request.method == 'GET':
        try:
            username = request.GET.get('username', 'mukhammad-develop')
            projects = fetch_github_projects(username)
            
            return JsonResponse({
                'success': True,
                'projects': projects,
                'count': len(projects)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)
