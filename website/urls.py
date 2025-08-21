from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('timeline/', views.timeline, name='timeline'),
    path('projects/', views.projects, name='projects'),
    path('turnitin/', views.turnitin, name='turnitin'),
    
    # Legacy routes (redirect to combined pages)
    path('achievements/', views.portfolio, name='achievements'),
    path('blog/', views.portfolio, name='blog'),
    path('metrics/', views.timeline, name='metrics'),
    path('booking/', views.timeline, name='booking'),
    path('resources/', views.projects, name='resources'),
] 