from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Project, TimeSlot, Booking


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'is_featured', 'is_active', 'order', 'created_at')
    list_filter = ('status', 'category', 'is_featured', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'technologies')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_featured', 'is_active', 'order')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'detailed_description')
        }),
        ('Project Details', {
            'fields': ('category', 'status', 'technologies', 'features')
        }),
        ('Links', {
            'fields': ('github_url', 'demo_url', 'documentation_url')
        }),
        ('Media', {
            'fields': ('icon', 'image')
        }),
        ('Statistics', {
            'fields': ('lines_of_code', 'success_rate', 'availability'),
            'classes': ('collapse',)
        }),
        ('Display Options', {
            'fields': ('is_featured', 'is_active', 'order')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('weekday', 'start_time', 'end_time', 'duration_minutes', 'is_active', 'created_at')
    list_filter = ('weekday', 'is_active')
    list_editable = ('is_active',)
    ordering = ('weekday', 'start_time')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'client_info', 
        'meeting_datetime', 
        'booking_type_display',
        'status_badge',
        'time_until_meeting',
        'created_at'
    )
    list_filter = ('status', 'booking_type', 'date', 'created_at')
    search_fields = ('name', 'email', 'company', 'subject', 'message', 'phone')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at', 'meeting_summary')
    date_hierarchy = 'date'
    actions = ['mark_as_confirmed', 'mark_as_completed', 'mark_as_cancelled']
    
    fieldsets = (
        ('Meeting Summary', {
            'fields': ('meeting_summary',),
            'classes': ('wide',)
        }),
        ('Client Information', {
            'fields': ('name', 'email', 'phone', 'company')
        }),
        ('Appointment Details', {
            'fields': ('date', 'start_time', 'end_time', 'duration_minutes', 'booking_type')
        }),
        ('Purpose', {
            'fields': ('subject', 'message')
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Order by date descending"""
        qs = super().get_queryset(request)
        return qs.order_by('-date', '-start_time')
    
    def client_info(self, obj):
        """Display client information with contact details"""
        html = f'<strong>{obj.name}</strong><br>'
        html += f'<small>📧 {obj.email}</small><br>'
        if obj.phone:
            html += f'<small>📞 {obj.phone}</small><br>'
        if obj.company:
            html += f'<small>🏢 {obj.company}</small>'
        return format_html(html)
    client_info.short_description = 'Client'
    
    def meeting_datetime(self, obj):
        """Display formatted meeting date and time"""
        now = timezone.now()
        meeting_dt = timezone.make_aware(timezone.datetime.combine(obj.date, obj.start_time))
        
        if obj.is_today:
            date_str = '<strong style="color: #f59e0b;">📅 TODAY</strong>'
        elif obj.is_upcoming:
            date_str = f'📅 {obj.date.strftime("%b %d, %Y")}'
        else:
            date_str = f'📅 {obj.date.strftime("%b %d, %Y")}'
        
        time_str = f'🕐 {obj.start_time.strftime("%H:%M")} - {obj.end_time.strftime("%H:%M")}'
        duration_str = f'<small>({obj.duration_minutes} min)</small>'
        
        return format_html(f'{date_str}<br>{time_str} {duration_str}')
    meeting_datetime.short_description = 'Meeting Date & Time'
    
    def booking_type_display(self, obj):
        """Display booking type with icon"""
        icons = {
            'consultation': '💬',
            'project_discussion': '🤝',
            'technical_support': '🆘',
            'collaboration': '👥',
            'other': '📋'
        }
        icon = icons.get(obj.booking_type, '📋')
        return format_html(
            f'{icon} <strong>{obj.get_booking_type_display()}</strong><br>'
            f'<small>{obj.subject}</small>'
        )
    booking_type_display.short_description = 'Meeting Type'
    
    def status_badge(self, obj):
        """Display status with color-coded badge"""
        colors = {
            'pending': '#f59e0b',
            'confirmed': '#10b981',
            'cancelled': '#ef4444',
            'completed': '#6b7280'
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-weight: 600; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display().upper()
        )
    status_badge.short_description = 'Status'
    
    def time_until_meeting(self, obj):
        """Show time remaining until meeting"""
        if not obj.is_upcoming:
            return format_html('<span style="color: #6b7280;">Past</span>')
        
        now = timezone.now()
        meeting_dt = timezone.make_aware(timezone.datetime.combine(obj.date, obj.start_time))
        delta = meeting_dt - now
        
        if delta.days > 0:
            return format_html(f'<span style="color: #10b981;">In {delta.days} days</span>')
        else:
            hours = delta.seconds // 3600
            if hours > 0:
                return format_html(f'<span style="color: #f59e0b;">In {hours} hours</span>')
            else:
                minutes = delta.seconds // 60
                return format_html(f'<span style="color: #ef4444;">In {minutes} minutes</span>')
    time_until_meeting.short_description = 'Time Until'
    
    def meeting_summary(self, obj):
        """Comprehensive meeting summary for detail view"""
        html = f'''
        <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; border-left: 4px solid #8b5cf6;">
            <h3 style="margin-top: 0; color: #8b5cf6;">📅 Meeting Summary</h3>
            <p><strong>Client:</strong> {obj.name} ({obj.email})</p>
            {f'<p><strong>Company:</strong> {obj.company}</p>' if obj.company else ''}
            {f'<p><strong>Phone:</strong> {obj.phone}</p>' if obj.phone else ''}
            <p><strong>Meeting Type:</strong> {obj.get_booking_type_display()}</p>
            <p><strong>Subject:</strong> {obj.subject}</p>
            <p><strong>Date:</strong> {obj.date.strftime("%A, %B %d, %Y")}</p>
            <p><strong>Time:</strong> {obj.start_time.strftime("%H:%M")} - {obj.end_time.strftime("%H:%M")} ({obj.duration_minutes} minutes)</p>
            <p><strong>Status:</strong> {obj.get_status_display()}</p>
            <p><strong>Message:</strong></p>
            <p style="background: white; padding: 10px; border-radius: 4px;">{obj.message}</p>
        </div>
        '''
        return format_html(html)
    meeting_summary.short_description = 'Meeting Overview'
    
    # Admin actions
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'{updated} booking(s) marked as confirmed.')
    mark_as_confirmed.short_description = "✅ Mark selected as Confirmed"
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} booking(s) marked as completed.')
    mark_as_completed.short_description = "✔️ Mark selected as Completed"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} booking(s) marked as cancelled.')
    mark_as_cancelled.short_description = "❌ Mark selected as Cancelled"
