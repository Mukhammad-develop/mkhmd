from django.contrib import admin
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
    list_display = ('name', 'email', 'date', 'start_time', 'booking_type', 'status', 'created_at')
    list_filter = ('status', 'booking_type', 'date', 'created_at')
    search_fields = ('name', 'email', 'company', 'subject', 'message')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
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
