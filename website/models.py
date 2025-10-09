from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Project(models.Model):
    """Model for showcasing projects on the website"""
    
    STATUS_CHOICES = [
        ('live', 'Live'),
        ('production', 'Production'),
        ('development', 'In Development'),
        ('planning', 'Planning'),
        ('research', 'Research'),
        ('completed', 'Completed'),
    ]
    
    CATEGORY_CHOICES = [
        ('web_scraping', 'Web Scraping'),
        ('automation', 'Automation'),
        ('web_development', 'Web Development'),
        ('data_extraction', 'Data Extraction'),
        ('api_development', 'API Development'),
        ('machine_learning', 'Machine Learning'),
        ('other', 'Other'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200, help_text="Project title")
    slug = models.SlugField(max_length=200, unique=True, help_text="URL-friendly version of title")
    description = models.TextField(help_text="Short description of the project")
    detailed_description = models.TextField(blank=True, help_text="Detailed project description (optional)")
    
    # Project Details
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    
    # Technologies (comma-separated)
    technologies = models.CharField(max_length=500, help_text="Comma-separated list of technologies (e.g., Python, Django, Selenium)")
    
    # Features (stored as JSON or comma-separated)
    features = models.TextField(blank=True, help_text="One feature per line")
    
    # Links
    github_url = models.URLField(blank=True, help_text="GitHub repository URL")
    demo_url = models.URLField(blank=True, help_text="Live demo URL")
    documentation_url = models.URLField(blank=True, help_text="Documentation URL")
    
    # Media
    icon = models.CharField(max_length=100, default='fas fa-code', help_text="Font Awesome icon class (e.g., fas fa-robot)")
    image = models.ImageField(upload_to='projects/', blank=True, null=True, help_text="Project screenshot or logo")
    
    # Statistics
    lines_of_code = models.CharField(max_length=20, blank=True, help_text="e.g., 2,000+")
    success_rate = models.CharField(max_length=20, blank=True, help_text="e.g., 99%")
    availability = models.CharField(max_length=20, blank=True, help_text="e.g., 24/7")
    
    # Display Options
    is_featured = models.BooleanField(default=False, help_text="Show as featured project on home page")
    is_active = models.BooleanField(default=True, help_text="Display on website")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers first)")
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_projects')
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
    
    def __str__(self):
        return self.title
    
    def get_technologies_list(self):
        """Return technologies as a list"""
        if self.technologies:
            return [tech.strip() for tech in self.technologies.split(',')]
        return []
    
    def get_features_list(self):
        """Return features as a list"""
        if self.features:
            return [feature.strip() for feature in self.features.split('\n') if feature.strip()]
        return []
    
    def get_stats_dict(self):
        """Return statistics as a dictionary"""
        stats = []
        if self.lines_of_code:
            stats.append({'value': self.lines_of_code, 'label': 'Lines of Code'})
        if self.success_rate:
            stats.append({'value': self.success_rate, 'label': 'Success Rate'})
        if self.availability:
            stats.append({'value': self.availability, 'label': 'Availability'})
        return stats
