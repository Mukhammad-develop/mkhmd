from django.shortcuts import render

# Create your views here.

def home(request):
    """Backend Developer Landing page view"""
    context = {
        'title': 'Backend Developer',
        'name': 'Abdurakhmon',
        'tagline': 'Backend Developer & API Architect',
        'description': 'Building robust server-side solutions and scalable architectures',
        'email': 'abdurakhmon@mkhmd.uk',
        'github': 'https://github.com/abdurakhmon',
        'linkedin': 'https://linkedin.com/in/abdurakhmon',
        'skills': [
            {'name': 'Python', 'icon': 'fab fa-python', 'level': 95},
            {'name': 'Django', 'icon': 'fas fa-server', 'level': 90},
            {'name': 'FastAPI', 'icon': 'fas fa-bolt', 'level': 85},
            {'name': 'PostgreSQL', 'icon': 'fas fa-database', 'level': 88},
            {'name': 'Redis', 'icon': 'fas fa-memory', 'level': 80},
            {'name': 'Docker', 'icon': 'fab fa-docker', 'level': 85},
            {'name': 'AWS', 'icon': 'fab fa-aws', 'level': 75},
            {'name': 'MongoDB', 'icon': 'fas fa-leaf', 'level': 70},
        ],
        'services': [
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
        ]
    }
    return render(request, 'website/home.html', context)
