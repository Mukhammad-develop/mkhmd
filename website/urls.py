from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('portfolio/', views.portfolio, name='portfolio'),
    # Placeholder pages (sample content) redirect to the real pages for now
    path('achievements/', RedirectView.as_view(pattern_name='website:portfolio'), name='achievements'),
    path('blog/', RedirectView.as_view(pattern_name='website:home'), name='blog'),
    path('schedule/', views.schedule, name='schedule'),
    path('schedule/book/', views.book_appointment, name='book_appointment'),
    path('metrics/', RedirectView.as_view(pattern_name='website:portfolio'), name='metrics'),
    path('booking/', RedirectView.as_view(pattern_name='website:schedule'), name='booking'),
    path('projects/', views.projects, name='projects'),
    path('resources/', RedirectView.as_view(pattern_name='website:projects'), name='resources'),
    path('turnitin/', views.turnitin, name='turnitin'),
    path('turnitin/results/', views.turnitin_results, name='turnitin_results'),
    path('turnitin/check/', views.check_turnitin_result, name='check_turnitin_result'),
    path('turnitin/check-status/', views.check_submissions_status, name='check_submissions_status'),
    path('api/github-projects/', views.github_projects, name='github_projects'),
    
    # Chat API endpoints (support chat)
    path('api/chat/init/', views.chat_init, name='chat_init'),
    path('api/chat/send/', views.chat_send_message, name='chat_send_message'),
    path('api/chat/messages/', views.chat_get_messages, name='chat_get_messages'),
    
    # Chat Hub (choose AI or Support)
    path('chat/', views.chat_hub, name='chat_hub'),
    
    # AI Chat endpoints (Mistral 7B)
    path('ai-chat/', views.ai_chat, name='ai_chat'),
    path('api/ai-chat/init/', views.ai_chat_init, name='ai_chat_init'),
    path('api/ai-chat/send/', views.ai_chat_send, name='ai_chat_send'),
    path('api/ai-chat/history/', views.ai_chat_get_history, name='ai_chat_get_history'),
    path('api/ai-chat/delete/', views.ai_chat_delete, name='ai_chat_delete'),
    
    # Support Chat endpoints (User to Admin)
    path('support-chat/', views.support_chat, name='support_chat'),
    path('api/support-chat/init/', views.support_chat_init, name='support_chat_init'),
    path('api/support-chat/send/', views.support_chat_send, name='support_chat_send'),
    path('api/support-chat/messages/', views.support_chat_messages, name='support_chat_messages'),
    path('api/support-chat/delete/', views.support_chat_delete, name='support_chat_delete'),
] 