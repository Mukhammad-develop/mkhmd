from django.core.management.base import BaseCommand
from django.utils.text import slugify
from website.models import Project
import requests


class Command(BaseCommand):
    help = 'Sync GitHub projects to database'

    def handle(self, *args, **options):
        username = 'mukhammad-develop'
        
        self.stdout.write(f'Fetching GitHub projects for {username}...')
        
        try:
            # Fetch from GitHub API
            response = requests.get(
                f'https://api.github.com/users/{username}/repos',
                params={'per_page': 100, 'sort': 'updated'},
                timeout=10
            )
            response.raise_for_status()
            github_repos = response.json()
            
            self.stdout.write(self.style.SUCCESS(f'✅ Found {len(github_repos)} repositories'))
            
            created_count = 0
            updated_count = 0
            
            for repo in github_repos:
                # Skip forks unless they have significant changes
                if repo.get('fork') and repo.get('stargazers_count', 0) < 5:
                    continue
                
                # Extract data
                name = repo.get('name', '')
                description = repo.get('description', '') or f'GitHub project: {name}'
                html_url = repo.get('html_url', '')
                homepage = repo.get('homepage', '')
                language = repo.get('language', 'Python') or 'Python'
                stars = repo.get('stargazers_count', 0)
                
                # Create slug
                slug = slugify(name)
                
                # Determine category based on language and description
                category = self.determine_category(language, description)
                
                # Check if project exists
                project, created = Project.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'title': name.replace('-', ' ').replace('_', ' ').title(),
                        'description': description[:500],  # Limit description length
                        'technologies': language,
                        'github_url': html_url,
                        'demo_url': homepage if homepage else '',
                        'category': category,
                        'status': 'completed' if stars > 5 else 'development',
                        'is_active': True,
                        'is_featured': False,
                        'order': 100,  # Lower priority than manually added projects
                        'icon': self.get_icon_for_language(language),
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(f'  ➕ Created: {project.title}')
                else:
                    # Update existing project
                    project.description = description[:500]
                    project.technologies = language
                    project.github_url = html_url
                    if homepage:
                        project.demo_url = homepage
                    project.save()
                    updated_count += 1
                    self.stdout.write(f'  🔄 Updated: {project.title}')
            
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Sync complete! Created: {created_count}, Updated: {updated_count}'
            ))
            
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'❌ Error fetching from GitHub: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
    
    def determine_category(self, language, description):
        """Determine project category based on language and description"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['scrap', 'crawl', 'extract', 'spider']):
            return 'web_scraping'
        elif any(word in description_lower for word in ['automat', 'bot', 'selenium']):
            return 'automation'
        elif any(word in description_lower for word in ['api', 'rest', 'graphql']):
            return 'api_development'
        elif any(word in description_lower for word in ['ml', 'machine learning', 'ai', 'neural']):
            return 'machine_learning'
        elif any(word in description_lower for word in ['data', 'extract', 'etl']):
            return 'data_extraction'
        elif language in ['JavaScript', 'TypeScript', 'HTML', 'CSS']:
            return 'web_development'
        else:
            return 'other'
    
    def get_icon_for_language(self, language):
        """Get Font Awesome icon based on language"""
        icons = {
            'Python': 'fab fa-python',
            'JavaScript': 'fab fa-js',
            'TypeScript': 'fab fa-js',
            'Java': 'fab fa-java',
            'C++': 'fas fa-code',
            'C': 'fas fa-code',
            'Go': 'fas fa-code',
            'Rust': 'fas fa-code',
            'PHP': 'fab fa-php',
            'Ruby': 'fas fa-gem',
            'Swift': 'fab fa-swift',
            'Kotlin': 'fas fa-mobile-alt',
            'HTML': 'fab fa-html5',
            'CSS': 'fab fa-css3-alt',
            'Shell': 'fas fa-terminal',
        }
        return icons.get(language, 'fas fa-code')

