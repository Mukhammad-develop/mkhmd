from django.contrib import admin
from mkhmd.admin_site import FriendlyAdminMixin
from django.utils.html import format_html, format_html_join, escape
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.utils import timezone
from django.db import models
from .models import Project, TimeSlot, Booking, ChatSession, ChatMessage, AIChat, AIChatMessage, GitHubRepo, Experience, Education, Skill


@admin.register(Project)
class ProjectAdmin(FriendlyAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'is_featured', 'is_active', 'order', 'links')
    list_display_links = ('title',)
    save_on_top = True
    list_filter = ('status', 'category', 'is_featured', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'technologies')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_featured', 'is_active', 'order')
    
    fieldsets = (
        ('1. The basics', {
            'description': 'The title and a one or two sentence summary. This is what visitors read on the project card.',
            'fields': ('title', 'slug', 'description', 'detailed_description')
        }),
        ('2. Where and how it is shown', {
            'description': '"Visible on website" shows the project on the Portfolio and Projects pages. '
                           '"Featured" makes it the big card on the homepage (only the first featured project is used). '
                           'Lower position numbers are shown first.',
            'fields': ('is_active', 'is_featured', 'order')
        }),
        ('3. Details', {
            'description': 'Status and category appear as small badges. Technologies are comma-separated, e.g. "Python, Django, Selenium". '
                           'Features: one per line.',
            'fields': ('category', 'status', 'technologies', 'features')
        }),
        ('4. Links', {
            'description': 'Leave empty if there is no link. Each filled link becomes a button on the card.',
            'fields': ('github_url', 'demo_url', 'documentation_url')
        }),
        ('5. Icon and image (optional)', {
            'description': 'Icon uses Font Awesome names, e.g. "fas fa-robot", "fas fa-spider", "fab fa-telegram". Browse icons at fontawesome.com/icons.',
            'fields': ('icon', 'image'),
            'classes': ('collapse',)
        }),
        ('6. Numbers (optional)', {
            'description': 'Shown under the featured project only. Use real numbers, e.g. "2,000+" lines of code.',
            'fields': ('lines_of_code', 'success_rate', 'availability'),
            'classes': ('collapse',)
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        labels = {
            'is_active': 'Visible on website',
            'is_featured': 'Featured on homepage',
            'order': 'Position',
            'slug': 'Web address name',
            'description': 'Short summary',
            'detailed_description': 'Longer description',
        }
        for field, label in labels.items():
            if field in form.base_fields:
                form.base_fields[field].label = label
        if 'slug' in form.base_fields:
            form.base_fields['slug'].help_text = 'Filled in automatically from the title. Letters, numbers and dashes only.'
        return form

    @admin.display(description='Links')
    def links(self, obj):
        parts = []
        if obj.github_url:
            parts.append(format_html('<a href="{}" target="_blank" rel="noopener">GitHub</a>', obj.github_url))
        if obj.demo_url:
            parts.append(format_html('<a href="{}" target="_blank" rel="noopener">Demo</a>', obj.demo_url))
        return mark_safe(' · '.join(parts)) if parts else '—'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(TimeSlot)
class TimeSlotAdmin(FriendlyAdminMixin, admin.ModelAdmin):
    list_display = ('weekday', 'start_time', 'end_time', 'duration_minutes', 'is_active')
    list_filter = ('weekday', 'is_active')
    list_editable = ('is_active',)
    ordering = ('weekday', 'start_time')
    fieldsets = (
        (None, {
            'description': 'Add one row per block of free time, e.g. Monday 09:00 to 12:00. '
                           'Times are in UTC (UK winter time; subtract 1 hour in UK summer time). '
                           'Visitors can only book inside these hours. Untick "active" to pause a slot without deleting it.',
            'fields': ('weekday', 'start_time', 'end_time', 'duration_minutes', 'is_active'),
        }),
    )


@admin.register(Booking)
class BookingAdmin(FriendlyAdminMixin, admin.ModelAdmin):
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
            'description': 'To answer this request: change "Status" below to Confirmed or Cancelled, then click Save. '
                           'Email the client to let them know. Use the "Reply by email" link.',
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
        html = format_html('<strong>{}</strong><br><small>📧 {}</small><br>', obj.name, obj.email)
        if obj.phone:
            html += format_html('<small>📞 {}</small><br>', obj.phone)
        if obj.company:
            html += format_html('<small>🏢 {}</small>', obj.company)
        return html
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
        
        return mark_safe(f'{date_str}<br>{time_str} {duration_str}')
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
            '{} <strong>{}</strong><br><small>{}</small>',
            icon, obj.get_booking_type_display(), obj.subject
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
            return mark_safe('<span style="color: #6b7280;">Past</span>')
        
        now = timezone.now()
        meeting_dt = timezone.make_aware(timezone.datetime.combine(obj.date, obj.start_time))
        delta = meeting_dt - now
        
        if delta.days > 0:
            return format_html('<span style="color: #10b981;">In {} days</span>', delta.days)
        else:
            hours = delta.seconds // 3600
            if hours > 0:
                return format_html('<span style="color: #f59e0b;">In {} hours</span>', hours)
            else:
                minutes = delta.seconds // 60
                return format_html('<span style="color: #ef4444;">In {} minutes</span>', minutes)
    time_until_meeting.short_description = 'Time Until'
    
    def meeting_summary(self, obj):
        """Comprehensive meeting summary for detail view"""
        html = f'''
        <div style="background: #f3f4f6; color: #111; padding: 20px; border-radius: 8px; border-left: 4px solid #8b5cf6;">
            <h3 style="margin-top: 0; color: #8b5cf6;">📅 Meeting Summary</h3>
            <p><strong>Client:</strong> {escape(obj.name)} ({escape(obj.email)})</p>
            {f'<p><strong>Company:</strong> {escape(obj.company)}</p>' if obj.company else ''}
            {f'<p><strong>Phone:</strong> {escape(obj.phone)}</p>' if obj.phone else ''}
            <p><strong>Meeting Type:</strong> {obj.get_booking_type_display()}</p>
            <p><strong>Subject:</strong> {escape(obj.subject)}</p>
            <p><strong>Date:</strong> {obj.date.strftime("%A, %B %d, %Y")}</p>
            <p><strong>Time:</strong> {obj.start_time.strftime("%H:%M")} - {obj.end_time.strftime("%H:%M")} ({obj.duration_minutes} minutes)</p>
            <p><strong>Status:</strong> {obj.get_status_display()}</p>
            <p><strong>Message:</strong></p>
            <p style="background: white; color: #111; padding: 10px; border-radius: 4px; white-space: pre-wrap;">{escape(obj.message)}</p>
            <p><a href="mailto:{escape(obj.email)}?subject={escape(obj.subject)}">✉️ Reply by email</a></p>
        </div>
        '''
        return mark_safe(html)
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
class ChatSessionAdmin(FriendlyAdminMixin, admin.ModelAdmin):
    def has_add_permission(self, request):
        # Conversations are started by visitors on the website, not here.
        return False

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
        <div style="background: #f3f4f6; color: #111; padding: 20px; border-radius: 8px; border-left: 4px solid #8b5cf6;">
            <h3 style="margin-top: 0; color: #8b5cf6;">💬 Chat Session Summary</h3>
            <p><strong>Visitor:</strong> {escape(obj.visitor_name or (obj.user.username if obj.user else 'Anonymous'))}</p>
            <p><strong>Contact:</strong> {escape(obj.visitor_email or (obj.user.email if obj.user else 'N/A'))}</p>
            <p><strong>Total Messages:</strong> {total}</p>
            <p><strong>Unread Messages:</strong> {unread}</p>
            <p><strong>Status:</strong> {'🟢 Active' if obj.is_active else '🔴 Closed'}</p>
            <p><strong>Started:</strong> {obj.created_at.strftime("%B %d, %Y at %H:%M")}</p>
            <p><strong>Last Activity:</strong> {obj.updated_at.strftime("%B %d, %Y at %H:%M")}</p>
            <p><a href="{reverse('website:support_chat')}">💬 Open the Support Chat page to reply</a></p>
        </div>
        '''
        return mark_safe(html)
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
class ChatMessageAdmin(FriendlyAdminMixin, admin.ModelAdmin):
    def has_add_permission(self, request):
        # Conversations are started by visitors on the website, not here.
        return False

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


class AIChatMessageInline(admin.TabularInline):
    model = AIChatMessage
    extra = 0
    fields = ('prompt_preview', 'response_preview', 'temperature', 'max_tokens', 'response_time_ms', 'created_at')
    readonly_fields = ('prompt_preview', 'response_preview', 'temperature', 'max_tokens', 'response_time_ms', 'created_at')
    can_delete = False
    
    def prompt_preview(self, obj):
        return obj.prompt[:80] + '...' if len(obj.prompt) > 80 else obj.prompt
    prompt_preview.short_description = 'User Prompt'
    
    def response_preview(self, obj):
        return obj.response[:100] + '...' if len(obj.response) > 100 else obj.response
    response_preview.short_description = 'AI Response'


@admin.register(AIChat)
class AIChatAdmin(FriendlyAdminMixin, admin.ModelAdmin):
    def has_add_permission(self, request):
        # Conversations are started by visitors on the website, not here.
        return False

    list_display = ('user_info', 'title', 'message_count_display', 'last_activity', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'title')
    readonly_fields = ('created_at', 'updated_at', 'conversation_stats', 'message_count')
    inlines = [AIChatMessageInline]
    actions = ['mark_as_inactive', 'mark_as_active']
    
    fieldsets = (
        ('Conversation Overview', {
            'fields': ('conversation_stats',),
            'classes': ('wide',)
        }),
        ('Chat Info', {
            'fields': ('user', 'title', 'is_active', 'message_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_info(self, obj):
        return format_html(
            '<strong>{}</strong><br><small>📧 {}</small>', 
            obj.user.username, 
            obj.user.email
        )
    user_info.short_description = 'User'
    
    def message_count_display(self, obj):
        count = obj.message_count
        return format_html(
            '<span style="background: #3b82f6; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-weight: 600;">{} messages</span>',
            count
        )
    message_count_display.short_description = 'Messages'
    
    def last_activity(self, obj):
        last_msg = obj.last_message
        if last_msg:
            return format_html(
                '<small>{}</small>',
                last_msg.created_at.strftime("%b %d, %Y %H:%M")
            )
        return format_html('<small style="color: #6b7280;">No messages</small>')
    last_activity.short_description = 'Last Activity'
    
    def conversation_stats(self, obj):
        messages = obj.ai_messages.all()
        total = messages.count()
        avg_temp = messages.aggregate(models.Avg('temperature'))['temperature__avg'] or 0
        avg_tokens = messages.aggregate(models.Avg('max_tokens'))['max_tokens__avg'] or 0
        avg_response_time = messages.aggregate(models.Avg('response_time_ms'))['response_time_ms__avg'] or 0
        
        html = f'''
        <div style="background: #f3f4f6; color: #111; padding: 20px; border-radius: 8px; border-left: 4px solid #3b82f6;">
            <h3 style="margin-top: 0; color: #3b82f6;">🤖 AI Chat Statistics</h3>
            <p><strong>User:</strong> {escape(obj.user.username)} ({escape(obj.user.email)})</p>
            <p><strong>Conversation Title:</strong> {escape(obj.title)}</p>
            <p><strong>Total Messages:</strong> {total}</p>
            <p><strong>Average Temperature:</strong> {avg_temp:.2f}</p>
            <p><strong>Average Max Tokens:</strong> {avg_tokens:.0f}</p>
            <p><strong>Average Response Time:</strong> {avg_response_time:.0f}ms</p>
            <p><strong>Status:</strong> {'🟢 Active' if obj.is_active else '🔴 Inactive'}</p>
            <p><strong>Started:</strong> {obj.created_at.strftime("%B %d, %Y at %H:%M")}</p>
            <p><strong>Last Updated:</strong> {obj.updated_at.strftime("%B %d, %Y at %H:%M")}</p>
        </div>
        '''
        return mark_safe(html)
    conversation_stats.short_description = 'Conversation Overview'
    
    def mark_as_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} conversation(s) marked as inactive.')
    mark_as_inactive.short_description = "🔒 Mark selected as Inactive"
    
    def mark_as_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} conversation(s) marked as active.')
    mark_as_active.short_description = "✅ Mark selected as Active"
    
    def export_conversation(self, request, queryset):
        # Future enhancement: export to JSON/TXT
        self.message_user(request, "Export feature coming soon!")
    export_conversation.short_description = "📥 Export conversations"


@admin.register(AIChatMessage)
class AIChatMessageAdmin(FriendlyAdminMixin, admin.ModelAdmin):
    def has_add_permission(self, request):
        # Conversations are started by visitors on the website, not here.
        return False

    list_display = ('chat_info', 'user_prompt_preview', 'ai_response_preview', 'temperature', 'max_tokens', 'response_time_display', 'created_at')
    list_filter = ('created_at', 'temperature')
    search_fields = ('prompt', 'response', 'chat__user__username')
    readonly_fields = ('chat', 'prompt', 'response', 'temperature', 'max_tokens', 'response_time_ms', 'created_at')
    
    fieldsets = (
        ('Conversation', {
            'fields': ('chat',)
        }),
        ('Exchange', {
            'fields': ('prompt', 'response')
        }),
        ('Generation Parameters', {
            'fields': ('temperature', 'max_tokens', 'response_time_ms'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def chat_info(self, obj):
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.chat.user.username,
            obj.chat.title
        )
    chat_info.short_description = 'Chat'
    
    def user_prompt_preview(self, obj):
        return obj.prompt[:100] + '...' if len(obj.prompt) > 100 else obj.prompt
    user_prompt_preview.short_description = 'User Message'
    
    def ai_response_preview(self, obj):
        return obj.response[:100] + '...' if len(obj.response) > 100 else obj.response
    ai_response_preview.short_description = 'AI Response'
    
    def response_time_display(self, obj):
        if obj.response_time_ms:
            seconds = obj.response_time_ms / 1000
            if seconds < 1:
                return format_html('<span style="color: #10b981;">{}ms</span>', f'{obj.response_time_ms:.0f}')
            else:
                return format_html('<span style="color: #f59e0b;">{}s</span>', f'{seconds:.2f}')
        return mark_safe('<span style="color: #6b7280;">N/A</span>')
    response_time_display.short_description = 'Response Time'


@admin.register(GitHubRepo)
class GitHubRepoAdmin(FriendlyAdminMixin, admin.ModelAdmin):
    """The list page sends you to the friendlier GitHub repos manager."""
    list_display = ('name', 'visible', 'pinned', 'order', 'title')

    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect
        return redirect('admin:mkhmd_github')

    def has_add_permission(self, request):
        return False


@admin.register(Experience)
class ExperienceAdmin(FriendlyAdminMixin, admin.ModelAdmin):
    list_display = ('role', 'company', 'start_date', 'end_date', 'visible', 'order')
    list_editable = ('visible', 'order')
    list_display_links = ('role',)
    fieldsets = (
        ('The job', {
            'description': 'Shown in the Experience timeline on the Portfolio page, newest first.',
            'fields': ('role', 'company', 'company_url', 'location'),
        }),
        ('Dates', {
            'description': 'Pick any day in the month. Leave "End date" empty if you still work there. It will show "Present" and a "Now" badge.',
            'fields': ('start_date', 'end_date'),
        }),
        ('What you did', {
            'description': 'Write one achievement per line; each line becomes a bullet point. Technologies are comma-separated.',
            'fields': ('description', 'technologies'),
        }),
        ('Display', {'fields': ('visible', 'order')}),
    )


@admin.register(Education)
class EducationAdmin(FriendlyAdminMixin, admin.ModelAdmin):
    list_display = ('school', 'degree', 'field', 'start_date', 'end_date', 'visible')
    list_editable = ('visible',)
    fieldsets = (
        (None, {
            'description': 'Shown under Education on the Portfolio page. An end date in the future shows an "In progress" badge.',
            'fields': ('school', 'degree', 'field', 'location', 'start_date', 'end_date', 'description', 'visible', 'order'),
        }),
    )


@admin.register(Skill)
class SkillAdmin(FriendlyAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'category', 'visible', 'order')
    list_editable = ('category', 'visible', 'order')
    list_filter = ('category',)
    search_fields = ('name',)
