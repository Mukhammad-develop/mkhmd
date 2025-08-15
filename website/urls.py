from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('achievements/', views.achievements, name='achievements'),
    path('timeline/', views.timeline, name='timeline'),
    path('blog/', views.blog, name='blog'),
    path('metrics/', views.metrics, name='metrics'),
    path('booking/', views.booking, name='booking'),
    path('resources/', views.resources, name='resources'),
] 