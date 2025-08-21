from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, EmailVerification, UserProfile, TurnitinResult

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('is_email_verified', 'bio', 'location', 'website', 'avatar', 'turnitin_balance')
        }),
    )
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_email_verified', 'turnitin_balance', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_email_verified', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name() or '-'
    get_full_name.short_description = 'Full Name'

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'code', 'created_at', 'is_used', 'expires_at')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__email', 'email', 'code')
    ordering = ('-created_at',)
    readonly_fields = ('code', 'created_at', 'expires_at')
    
    def is_expired_display(self, obj):
        if obj.is_expired():
            return format_html('<span style="color: red;">Expired</span>')
        return format_html('<span style="color: green;">Valid</span>')
    is_expired_display.short_description = 'Status'

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'phone', 'date_of_birth', 'company', 'job_title',
        'github', 'linkedin', 'twitter',
        'email_notifications', 'profile_visibility'
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'company', 'job_title', 'profile_visibility', 'created_at')
    list_filter = ('profile_visibility', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__username', 'company', 'job_title')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Personal Info', {'fields': ('phone', 'date_of_birth')}),
        ('Professional', {'fields': ('company', 'job_title')}),
        ('Social Links', {'fields': ('github', 'linkedin', 'twitter')}),
        ('Preferences', {'fields': ('email_notifications', 'profile_visibility')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    readonly_fields = ('created_at', 'updated_at')

@admin.register(TurnitinResult)
class TurnitinResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'access_code', 'plagiarism_percentage', 'ai_percentage', 'submission_date', 'status')
    list_filter = ('status', 'turnitin_type', 'submission_date', 'created_at')
    search_fields = ('user__email', 'user__username', 'title', 'access_code')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'access_code', 'title', 'submission_date', 'status', 'turnitin_type')
        }),
        ('Results', {
            'fields': ('plagiarism_percentage', 'ai_percentage')
        }),
        ('Reports Available', {
            'fields': ('ai_report_available', 'plagiarism_report_available', 'english_guide_available')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Add UserProfile inline to User admin
UserAdmin.inlines = [UserProfileInline]
