from django.core.management.base import BaseCommand
from website.models import Project


class Command(BaseCommand):
    help = 'Add AI Language Model Chat project to the database'

    def handle(self, *args, **kwargs):
        # Check if project already exists
        if Project.objects.filter(slug='ai-language-model').exists():
            self.stdout.write(self.style.WARNING('AI Language Model project already exists'))
            return

        # Create the AI Chat project
        project = Project.objects.create(
            title='AI Language Model Chat',
            slug='ai-language-model',
            description='Interactive AI-powered chat application using Mistral 7B Instruct model deployed on Google Cloud Run with GPU acceleration',
            detailed_description='''A full-featured ChatGPT-like application that allows registered users to have intelligent 
            conversations with an advanced AI assistant. The system maintains conversation history, supports adjustable creativity levels, 
            and provides real-time responses with superior quality compared to older models. Administrators can view all chat histories 
            and statistics through the Django admin panel.
            
            The AI backend is powered by Mistral 7B Instruct (7 billion parameters) via HuggingFace Inference API with GPU acceleration, 
            deployed on Google Cloud Run, providing scalable, fast, and high-quality AI text generation capabilities.''',
            category='machine_learning',
            status='live',
            technologies='Python, Django, Mistral 7B, HuggingFace, Google Cloud Run, JavaScript, REST API, AJAX, GPU Computing',
            features='''Real-time AI conversation with context awareness
User authentication and authorization
Conversation history management
Adjustable AI parameters (temperature, token length)
Multiple simultaneous conversations
Admin dashboard for viewing chat analytics
Responsive ChatGPT-like UI
Conversation deletion and management
API integration with external AI service
Error handling and timeout management''',
            github_url='https://github.com/abdurakhmon',
            demo_url='',
            documentation_url='',
            icon='fas fa-robot',
            lines_of_code='2,500+',
            success_rate='99%',
            availability='24/7',
            is_featured=True,
            is_active=True,
            order=2
        )

        self.stdout.write(self.style.SUCCESS(f'Successfully created project: {project.title}'))
        self.stdout.write(self.style.SUCCESS(f'Project ID: {project.id}'))
        self.stdout.write(self.style.SUCCESS(f'Status: {project.status}'))
        self.stdout.write(self.style.SUCCESS(f'Category: {project.get_category_display()}'))

