from django.shortcuts import render

# Create your views here.

def home(request):
    """Software Developer Landing page view"""
    context = {
        'title': 'Software Developer',
        'name': 'Abdurakhmon',
        'tagline': 'Full-Stack Developer & Problem Solver',
        'description': 'Crafting elegant solutions through clean code and innovative thinking',
        'skills': [
            {'name': 'Python', 'icon': 'fab fa-python', 'level': 90},
            {'name': 'Django', 'icon': 'fas fa-server', 'level': 85},
            {'name': 'JavaScript', 'icon': 'fab fa-js-square', 'level': 80},
            {'name': 'React', 'icon': 'fab fa-react', 'level': 75},
            {'name': 'PostgreSQL', 'icon': 'fas fa-database', 'level': 80},
            {'name': 'Docker', 'icon': 'fab fa-docker', 'level': 70},
        ],
        'services': [
            {
                'title': 'Web Development',
                'description': 'Building responsive, scalable web applications using modern frameworks and best practices.',
                'icon': 'fas fa-globe'
            },
            {
                'title': 'Backend Development',
                'description': 'Creating robust APIs and server-side solutions with Django, FastAPI, and microservices.',
                'icon': 'fas fa-server'
            },
            {
                'title': 'Database Design',
                'description': 'Designing efficient database schemas and optimizing query performance.',
                'icon': 'fas fa-database'
            },
        ]
    }
    return render(request, 'website/home.html', context)
