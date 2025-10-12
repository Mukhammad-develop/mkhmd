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
    
    # Chat API endpoints (support chat)
    path('api/chat/init/', views.chat_init, name='chat_init'),
    path('api/chat/send/', views.chat_send_message, name='chat_send_message'),
    path('api/chat/messages/', views.chat_get_messages, name='chat_get_messages'),
    
    # AI Chat endpoints (GPT-2)
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path('api/ai-chat/init/', views.ai_chat_init, name='ai_chat_init'),
    path('api/ai-chat/send/', views.ai_chat_send, name='ai_chat_send'),
    path('api/ai-chat/history/', views.ai_chat_get_history, name='ai_chat_get_history'),
    path('api/ai-chat/delete/', views.ai_chat_delete, name='ai_chat_delete'),
] 