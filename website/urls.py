from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('achievements/', views.achievements, name='achievements'),
    path('blog/', views.blog, name='blog'),
    path('schedule/', views.schedule, name='schedule'),
    path('schedule/book/', views.book_appointment, name='book_appointment'),
    path('metrics/', views.metrics, name='metrics'),
    path('booking/', views.booking, name='booking'),
    path('projects/', views.projects, name='projects'),
    path('resources/', views.resources, name='resources'),
    path('turnitin/', views.turnitin, name='turnitin'),
    path('turnitin/results/', views.turnitin_results, name='turnitin_results'),
    path('turnitin/check/', views.check_turnitin_result, name='check_turnitin_result'),
    path('turnitin/check-status/', views.check_submissions_status, name='check_submissions_status'),
    path('api/github-projects/', views.github_projects, name='github_projects'),
] 