from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
import uuid

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


class TimeSlot(models.Model):
    """Model for defining available time slots for booking"""
    
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    weekday = models.IntegerField(choices=WEEKDAY_CHOICES, help_text="Day of the week")
    start_time = models.TimeField(help_text="Start time of availability")
    end_time = models.TimeField(help_text="End time of availability")
    is_active = models.BooleanField(default=True, help_text="Is this time slot currently available?")
    duration_minutes = models.IntegerField(default=60, help_text="Duration of each appointment slot in minutes")
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['weekday', 'start_time']
        verbose_name = 'Time Slot'
        verbose_name_plural = 'Time Slots'
    
    def __str__(self):
        return f"{self.get_weekday_display()} {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
    
    def clean(self):
        """Validate that end_time is after start_time"""
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time")


class Booking(models.Model):
    """Model for storing client bookings"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    # Client Information
    name = models.CharField(max_length=200, help_text="Client's full name")
    email = models.EmailField(help_text="Client's email address")
    phone = models.CharField(max_length=20, blank=True, help_text="Client's phone number (optional)")
    company = models.CharField(max_length=200, blank=True, help_text="Company name (optional)")
    
    # Booking Details
    date = models.DateField(help_text="Date of the appointment")
    start_time = models.TimeField(help_text="Start time of the appointment")
    end_time = models.TimeField(help_text="End time of the appointment")
    duration_minutes = models.IntegerField(default=60, help_text="Duration in minutes")
    
    # Purpose
    subject = models.CharField(max_length=300, help_text="Meeting subject")
    message = models.TextField(help_text="Additional details or requirements")
    booking_type = models.CharField(
        max_length=50,
        choices=[
            ('consultation', 'Consultation'),
            ('project_discussion', 'Project Discussion'),
            ('technical_support', 'Technical Support'),
            ('collaboration', 'Collaboration Opportunity'),
            ('other', 'Other'),
        ],
        default='consultation'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, help_text="Admin notes (not visible to client)")
    
    class Meta:
        ordering = ['-date', '-start_time']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
    
    def __str__(self):
        return f"{self.name} - {self.date} {self.start_time.strftime('%H:%M')}"
    
    def clean(self):
        """Validate booking"""
        # Check that end_time is after start_time
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time")
        
        # Check that booking is not in the past
        booking_datetime = datetime.combine(self.date, self.start_time)
        if timezone.make_aware(booking_datetime) < timezone.now():
            raise ValidationError("Cannot book appointments in the past")
    
    @property
    def is_upcoming(self):
        """Check if booking is in the future"""
        booking_datetime = datetime.combine(self.date, self.start_time)
        return timezone.make_aware(booking_datetime) > timezone.now()
    
    @property
    def is_today(self):
        """Check if booking is today"""
        return self.date == timezone.now().date()


class ChatSession(models.Model):
    """Model for chat sessions - each visitor gets a session"""
    
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_sessions')
    visitor_name = models.CharField(max_length=100, blank=True, help_text="Name for anonymous visitors")
    visitor_email = models.EmailField(blank=True, help_text="Email for anonymous visitors")
    is_active = models.BooleanField(default=True, help_text="Is this chat session still active?")
    is_read_by_admin = models.BooleanField(default=False, help_text="Has admin read this conversation?")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'
    
    def __str__(self):
        if self.user:
            return f"Chat with {self.user.username}"
        elif self.visitor_name:
            return f"Chat with {self.visitor_name}"
        return f"Chat #{self.session_id.hex[:8]}"
    
    @property
    def unread_messages_count(self):
        """Count unread messages from visitor"""
        return self.messages.filter(is_from_admin=False, is_read=False).count()
    
    @property
    def last_message(self):
        """Get the last message in this session"""
        return self.messages.order_by('-created_at').first()


class ChatMessage(models.Model):
    """Model for individual chat messages"""
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message = models.TextField(help_text="Message content")
    is_from_admin = models.BooleanField(default=False, help_text="Is this message from admin?")
    is_read = models.BooleanField(default=False, help_text="Has the message been read?")
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
    
    def __str__(self):
        sender = "Admin" if self.is_from_admin else "Visitor"
        return f"{sender}: {self.message[:50]}"
