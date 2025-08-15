from django.shortcuts import render

# Create your views here.

def home(request):
    """Dual Identity Landing page view - Software Developer & Businessman"""
    context = {
        'title': 'Software Developer & Businessman',
        'name': 'Abdurakhmon',
        'tagline': 'Software Developer & Strategic Businessman',
        'description': 'Building innovative solutions through code and driving business growth through strategic thinking',
        'email': 'abdurakhmon@mkhmd.uk',
        'github': 'https://github.com/abdurakhmon',
        'linkedin': 'https://linkedin.com/in/abdurakhmon',
        
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
