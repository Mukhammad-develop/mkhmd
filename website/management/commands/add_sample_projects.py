from django.core.management.base import BaseCommand
from website.models import Project


class Command(BaseCommand):
    help = 'Add sample coming soon projects'

    def handle(self, *args, **options):
        sample_projects = [
            {
                'title': 'E-commerce Price Monitor',
                'slug': 'ecommerce-price-monitor',
                'description': 'Real-time price tracking across multiple e-commerce platforms with automated alerts and proxy rotation for undetected monitoring.',
                'category': 'web_scraping',
                'status': 'development',
                'technologies': 'Python, Scrapy, Redis, PostgreSQL, Celery',
                'icon': 'fas fa-shopping-cart',
                'is_featured': False,
                'is_active': True,
                'order': 1
            },
            {
                'title': 'Data Analytics Dashboard',
                'slug': 'data-analytics-dashboard',
                'description': 'Interactive dashboard for visualizing web scraping results and trends with real-time data processing and beautiful charts.',
                'category': 'web_development',
                'status': 'planning',
                'technologies': 'Django, React, D3.js, PostgreSQL, WebSockets',
                'icon': 'fas fa-chart-line',
                'is_featured': False,
                'is_active': True,
                'order': 2
            },
            {
                'title': 'Anti-Detection Framework',
                'slug': 'anti-detection-framework',
                'description': 'Advanced toolkit for bypassing bot detection and CAPTCHA systems with machine learning-based fingerprint randomization.',
                'category': 'automation',
                'status': 'research',
                'technologies': 'Python, Playwright, ML Models, Proxy Networks',
                'icon': 'fas fa-shield-alt',
                'is_featured': False,
                'is_active': True,
                'order': 3
            }
        ]
        
        created_count = 0
        for project_data in sample_projects:
            # Check if project already exists
            if not Project.objects.filter(slug=project_data['slug']).exists():
                Project.objects.create(**project_data)
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {project_data['title']}"))
            else:
                self.stdout.write(self.style.WARNING(f"Already exists: {project_data['title']}"))
        
        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {created_count} sample projects!'))

