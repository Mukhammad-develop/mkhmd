from django.contrib import admin
from .models import Project


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
