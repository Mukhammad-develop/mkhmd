# Generated manually for AI Chat feature

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('website', '0003_chatsession_chatmessage'),
    ]

    operations = [
        migrations.CreateModel(
            name='AIChat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='New Conversation', help_text='Chat title (auto-generated from first message)', max_length=200)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True, help_text='Is this conversation still active?')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_chats', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'AI Chat Conversation',
                'verbose_name_plural': 'AI Chat Conversations',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='AIChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt', models.TextField(help_text="User's message/prompt")),
                ('response', models.TextField(help_text="AI's response")),
                ('temperature', models.FloatField(default=0.7, help_text='Temperature used for generation')),
                ('max_tokens', models.IntegerField(default=150, help_text='Max tokens used for generation')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('response_time_ms', models.IntegerField(blank=True, help_text='API response time in milliseconds', null=True)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_messages', to='website.aichat')),
            ],
            options={
                'verbose_name': 'AI Chat Message',
                'verbose_name_plural': 'AI Chat Messages',
                'ordering': ['created_at'],
            },
        ),
    ]

