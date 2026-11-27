from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import random
import string

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    
    # Profile fields
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Turnitin balance
    turnitin_balance = models.IntegerField(default=0, help_text="Number of Turnitin checks available")
    
    # Account metadata
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def get_short_name(self):
        return self.first_name or self.username

class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def generate_code(self):
        return ''.join(random.choices(string.digits, k=6))
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Verification for {self.email} - {self.code}"
    
    class Meta:
        ordering = ['-created_at']

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    company = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    
    # Social links
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    profile_visibility = models.CharField(
        max_length=10,
        choices=[
            ('public', 'Public'),
            ('private', 'Private'),
        ],
        default='public'
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email}'s Profile"


class TurnitinSubmission(models.Model):
    # Submission ID starts from 3432 and increments
    submission_id = models.IntegerField(unique=True, help_text="Submission ID starting from 3432")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='turnitin_submissions')
    
    # Submission status: False = ongoing (AI检测中...), True = completed (检测完成)
    submission_status = models.BooleanField(default=False, help_text="False = ongoing, True = completed")
    
    # Results - retrieved when available
    similarity_percentage = models.CharField(max_length=10, blank=True, null=True, help_text="Similarity percentage as string")
    ai_percentage = models.CharField(max_length=10, blank=True, null=True, help_text="AI percentage as string")
    
    # Files - downloaded when available
    similarity_file = models.FileField(upload_to='turnitin/similarity/', blank=True, null=True, help_text="Similarity report file")
    ai_file = models.FileField(upload_to='turnitin/ai/', blank=True, null=True, help_text="AI report file")
    
    # Additional fields from old TurnitinResult for compatibility
    access_code = models.CharField(max_length=50, blank=True, null=True, help_text="Turnitin access code")
    submission_date = models.DateTimeField(blank=True, null=True, help_text="Original submission date from Turnitin")
    turnitin_type = models.CharField(max_length=50, default='Turnitin UK')
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        status = "completed" if self.submission_status else "ongoing"
        return f"Submission {self.submission_id} - {self.owner.email} ({status})"
    
    @classmethod
    def get_next_submission_id(cls):
        """Get the next available submission ID starting from 3432"""
        last_submission = cls.objects.order_by('-submission_id').first()
        if last_submission:
            return last_submission.submission_id + 1
        return 3432
    
    def is_ongoing(self):
        """Check if submission is still ongoing"""
        return not self.submission_status
    
    def is_completed(self):
        """Check if submission is completed"""
        return self.submission_status


class Notification(models.Model):
    """A message for one user, shown under the bell icon on the website."""

    LEVEL_CHOICES = [
        ('info', 'Info'),
        ('success', 'Good news'),
        ('warning', 'Important'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=150)
    message = models.TextField(blank=True)
    link = models.CharField(max_length=300, blank=True, help_text="Optional page to open, e.g. /projects/")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='info')
    is_read = models.BooleanField(default=False)
    emailed = models.BooleanField(default=False)
    batch = models.UUIDField(null=True, blank=True, db_index=True,
                             help_text="Notifications sent together share a batch id")
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} → {self.user.email}"
