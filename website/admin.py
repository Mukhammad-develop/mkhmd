from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Project, TimeSlot, Booking, ChatSession, ChatMessage


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


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    fields = ('message_preview', 'sender_badge', 'created_at', 'is_read')
    readonly_fields = ('message_preview', 'sender_badge', 'created_at', 'is_read')
    can_delete = False
    
    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Message'
    
    def sender_badge(self, obj):
        if obj.is_from_admin:
            return format_html('<span style="background: #8b5cf6; color: white; padding: 2px 8px; border-radius: 8px;">Admin</span>')
        return format_html('<span style="background: #10b981; color: white; padding: 2px 8px; border-radius: 8px;">Visitor</span>')
    sender_badge.short_description = 'From'


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('visitor_info', 'unread_badge', 'last_message_preview', 'is_active', 'updated_at')
    list_filter = ('is_active', 'is_read_by_admin', 'created_at')
    search_fields = ('visitor_name', 'visitor_email', 'user__username', 'user__email')
    readonly_fields = ('session_id', 'created_at', 'updated_at', 'conversation_summary')
    inlines = [ChatMessageInline]
    actions = ['mark_as_read', 'close_chat']
    
    fieldsets = (
        ('Conversation Overview', {
            'fields': ('conversation_summary',),
            'classes': ('wide',)
        }),
        ('Session Info', {
            'fields': ('session_id', 'user', 'visitor_name', 'visitor_email')
        }),
        ('Status', {
            'fields': ('is_active', 'is_read_by_admin')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def visitor_info(self, obj):
        if obj.user:
            return format_html('<strong>{}</strong><br><small>📧 {}</small>', obj.user.username, obj.user.email)
        elif obj.visitor_name:
            return format_html('<strong>{}</strong><br><small>📧 {}</small>', obj.visitor_name, obj.visitor_email or 'No email')
        return format_html('<small>Anonymous #{}</small>', obj.session_id.hex[:8])
    visitor_info.short_description = 'Visitor'
    
    def unread_badge(self, obj):
        count = obj.unread_messages_count
        if count > 0:
            return format_html(
                '<span style="background: #ef4444; color: white; padding: 4px 10px; '
                'border-radius: 12px; font-weight: 600;">{} New</span>',
                count
            )
        return format_html('<span style="color: #6b7280;">All read</span>')
    unread_badge.short_description = 'Status'
    
    def last_message_preview(self, obj):
        last_msg = obj.last_message
        if last_msg:
            sender = "You" if last_msg.is_from_admin else obj.visitor_name or "Visitor"
            preview = last_msg.message[:60] + '...' if len(last_msg.message) > 60 else last_msg.message
            return format_html('<strong>{}:</strong> {}', sender, preview)
        return format_html('<small style="color: #6b7280;">No messages yet</small>')
    last_message_preview.short_description = 'Last Message'
    
    def conversation_summary(self, obj):
        messages = obj.messages.all()
        total = messages.count()
        unread = obj.unread_messages_count
        
        html = f'''
        <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; border-left: 4px solid #8b5cf6;">
            <h3 style="margin-top: 0; color: #8b5cf6;">💬 Chat Session Summary</h3>
            <p><strong>Visitor:</strong> {obj.visitor_name or obj.user.username if obj.user else 'Anonymous'}</p>
            <p><strong>Contact:</strong> {obj.visitor_email or (obj.user.email if obj.user else 'N/A')}</p>
            <p><strong>Total Messages:</strong> {total}</p>
            <p><strong>Unread Messages:</strong> {unread}</p>
            <p><strong>Status:</strong> {'🟢 Active' if obj.is_active else '🔴 Closed'}</p>
            <p><strong>Started:</strong> {obj.created_at.strftime("%B %d, %Y at %H:%M")}</p>
            <p><strong>Last Activity:</strong> {obj.updated_at.strftime("%B %d, %Y at %H:%M")}</p>
        </div>
        '''
        return format_html(html)
    conversation_summary.short_description = 'Chat Overview'
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read_by_admin=True)
        # Mark all messages as read
        for session in queryset:
            session.messages.filter(is_from_admin=False).update(is_read=True)
        self.message_user(request, f'{updated} chat session(s) marked as read.')
    mark_as_read.short_description = "✅ Mark selected as Read"
    
    def close_chat(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} chat session(s) closed.')
    close_chat.short_description = "🔒 Close selected chats"


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session_info', 'sender_badge', 'message_preview', 'created_at', 'is_read')
    list_filter = ('is_from_admin', 'is_read', 'created_at')
    search_fields = ('message', 'session__visitor_name', 'session__visitor_email')
    readonly_fields = ('session', 'created_at')
    
    def session_info(self, obj):
        return obj.session
    session_info.short_description = 'Chat Session'
    
    def sender_badge(self, obj):
        if obj.is_from_admin:
            return format_html('<span style="background: #8b5cf6; color: white; padding: 4px 12px; border-radius: 12px;">Admin</span>')
        return format_html('<span style="background: #10b981; color: white; padding: 4px 12px; border-radius: 12px;">Visitor</span>')
    sender_badge.short_description = 'From'
    
    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Message'
