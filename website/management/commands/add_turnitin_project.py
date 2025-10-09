from django.core.management.base import BaseCommand
from website.models import Project


class Command(BaseCommand):
    help = 'Add Turnitin Automation as the featured project'

    def handle(self, *args, **options):
        # Check if Turnitin project already exists
        turnitin_project = Project.objects.filter(slug='turnitin-automation-system').first()
        
        if turnitin_project:
            self.stdout.write(self.style.WARNING('Turnitin project already exists!'))
            return
        
        # Create the Turnitin project
        project = Project.objects.create(
            title='Turnitin Automation System',
            slug='turnitin-automation-system',
            description='A sophisticated automation system that streamlines the entire Turnitin plagiarism detection workflow. Users can upload documents, and the system automatically submits them to Turnitin, handles Chinese UI elements, tracks progress, parses results, and downloads reports—all without manual intervention.',
            detailed_description='This project demonstrates advanced web scraping and automation capabilities using Selenium WebDriver. It includes intelligent form detection, multi-language UI handling, robust error recovery, and comprehensive result parsing.',
            category='automation',
            status='live',
            technologies='Python, Django, Selenium, BeautifulSoup, WebDriver',
            features='''Automated form filling & submission
Chinese UI detection & handling
Real-time progress tracking
Automatic result parsing & downloads
Credit-based access system
Production-ready on PythonAnywhere''',
            github_url='https://github.com/mukhammad-develop/mkhmd',
            demo_url='/turnitin/',
            documentation_url='',
            icon='fas fa-robot',
            lines_of_code='2,000+',
            success_rate='99%',
            availability='24/7',
            is_featured=True,
            is_active=True,
            order=0
        )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created project: {project.title}'))
        self.stdout.write(self.style.SUCCESS('The project is now featured on the home page!'))

