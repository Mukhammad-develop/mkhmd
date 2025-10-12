# AI Chat Feature - Deployment Guide

## Overview

This guide covers deploying the AI Chat feature to PythonAnywhere. The feature provides a ChatGPT-like interface using a GPT-2 language model API.

---

## Features

✅ **User Authentication Required** - Only logged-in users can access  
✅ **Multiple Conversations** - Users can have multiple chat sessions  
✅ **Conversation History** - All chats are saved and retrievable  
✅ **Adjustable AI Parameters** - Temperature and token length controls  
✅ **Admin Dashboard** - View all user conversations and statistics  
✅ **Real-time Responses** - Streaming-like experience with typing indicators  
✅ **GPT-2 Integration** - Uses external AI API hosted on Google Cloud Run  

---

## Deployment Steps for PythonAnywhere

### 1. Pull Latest Code

```bash
cd ~/mkhmd
git stash  # If you have local changes to db.sqlite3
git pull origin main
```

### 2. Run Migrations

```bash
python3.10 manage.py migrate
```

Expected output:
```
Running migrations:
  Applying website.0004_aichat_aichatmessage... OK
```

### 3. Add the AI Chat Project

```bash
python3.10 manage.py add_ai_chat_project
```

This will:
- Create a new "AI Language Model Chat" project
- Set it as featured
- Add it to your projects page

### 4. Verify Admin Access

1. Go to your admin panel: `http://yourdomain.com/admin/`
2. Check for new sections:
   - **AI Chat Conversations** - View all user chats
   - **AI Chat Messages** - View individual messages
3. Check **Projects** - Verify "AI Language Model Chat" is there

### 5. Test the Feature

1. Log in as a regular user (not admin)
2. You should see "AI Chat" in the navigation menu (with robot icon 🤖)
3. Click "AI Chat" to access the chat interface
4. Start a new conversation
5. Send a message and wait for AI response (may take 30-60 seconds on first request - cold start)

### 6. Reload Web App

```bash
# PythonAnywhere console
touch /var/www/yourusername_pythonanywhere_com_wsgi.py
```

Or use the "Reload" button in the PythonAnywhere Web tab.

---

## API Information

**API Endpoint**: `https://language-ai-api-atnpjnu3rq-nw.a.run.app/generate`

**Model**: GPT-2 (124M parameters)

**Performance**:
- **Cold Start**: 30-60 seconds (first request)
- **Warm Requests**: 2-10 seconds
- **No Authentication Required**: Public API

**Parameters**:
- `temperature`: 0.3 (focused) to 1.0 (creative)
- `max_tokens`: 50 (short) to 300 (long)
- `top_k`: 50 (default)
- `top_p`: 0.95 (default)

---

## Admin Features

### Viewing Chat Histories

1. Go to **Admin Panel** → **AI Chat Conversations**
2. You'll see:
   - User information
   - Chat title (auto-generated from first message)
   - Number of messages
   - Last activity time
   - Active/Inactive status

3. Click on a conversation to view:
   - Full conversation history
   - All messages with timestamps
   - AI generation parameters (temperature, tokens)
   - Response times
   - Statistics (average temperature, tokens, response time)

### Bulk Actions

- **Mark as Inactive**: Close multiple conversations
- **Mark as Active**: Reopen conversations
- **Export** (coming soon): Export conversations to JSON/TXT

### Filtering & Search

- Filter by: Active status, Creation date, Update date
- Search by: Username, Email, Chat title
- Sort by: Last activity, Creation date, Number of messages

---

## User Features

### Starting a Conversation

1. Click "New Conversation" button
2. Type your message
3. Click "Send" or press `Ctrl+Enter`
4. Wait for AI response

### Managing Conversations

- **Switch Chats**: Click on any chat in the sidebar
- **Delete Chat**: Click "Delete" button in chat header
- **Adjust Settings**:
  - **Creativity** (Temperature): Low (focused) to High (creative)
  - **Length** (Max Tokens): Short, Medium, or Long responses

### Conversation History

- All conversations are saved automatically
- Title is generated from the first message
- Click on any conversation in the sidebar to resume
- Conversations maintain context (last 5 message pairs)

---

## Troubleshooting

### Issue: "Failed to connect to AI service"

**Cause**: API might be down or network issue

**Solution**:
1. Test API health: `curl https://language-ai-api-atnpjnu3rq-nw.a.run.app/`
2. Check network connectivity
3. Wait a few minutes and try again

### Issue: "The AI model is taking too long to respond"

**Cause**: Cold start (model loading) or timeout

**Solution**:
1. First request after idle time takes 30-60 seconds
2. Wait and try again
3. Subsequent requests will be faster

### Issue: AI Chat not showing in navigation

**Cause**: User not logged in

**Solution**:
- AI Chat is only available to authenticated users
- Log in first, then check navigation

### Issue: Empty or short AI responses

**Cause**: GPT-2 limitations or prompt issues

**Solution**:
1. Try rephrasing your question
2. Provide more context
3. Increase "Length" setting
4. Use a more specific prompt

### Issue: Migration failed

**Error**: `django.db.utils.OperationalError: no such table`

**Solution**:
```bash
python3.10 manage.py migrate website 0004 --fake
python3.10 manage.py migrate
```

---

## Database Schema

### AIChat Model

```python
- user (ForeignKey to User)
- title (CharField, max 200)
- created_at (DateTime)
- updated_at (DateTime, auto)
- is_active (Boolean)
```

### AIChatMessage Model

```python
- chat (ForeignKey to AIChat)
- prompt (TextField) - User's message
- response (TextField) - AI's response
- temperature (Float, default 0.7)
- max_tokens (Integer, default 150)
- response_time_ms (Integer, nullable)
- created_at (DateTime)
```

---

## Security Notes

1. **Authentication Required**: Only logged-in users can access
2. **User Isolation**: Users can only see their own chats
3. **Admin Access**: Admins can view all chats (for moderation)
4. **CSRF Protection**: All POST requests are CSRF-protected
5. **Rate Limiting**: Consider adding if users abuse the service

---

## Performance Optimization

### Recommended Settings

For PythonAnywhere:
- **Default Temperature**: 0.7 (balanced)
- **Default Max Tokens**: 150 (medium length)
- **Context Window**: Last 5 message pairs

### Database Maintenance

```bash
# Clean up old conversations (optional)
python3.10 manage.py shell
>>> from website.models import AIChat
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> old_date = timezone.now() - timedelta(days=90)
>>> old_chats = AIChat.objects.filter(updated_at__lt=old_date, is_active=False)
>>> old_chats.delete()
```

---

## Future Enhancements

Possible improvements:
- [ ] Conversation export (JSON, TXT, PDF)
- [ ] Conversation sharing between users
- [ ] Voice input/output
- [ ] Code syntax highlighting in responses
- [ ] Markdown formatting support
- [ ] File uploads for context
- [ ] Integration with better models (GPT-3.5, GPT-4)
- [ ] Custom system prompts
- [ ] Conversation templates
- [ ] Usage statistics and analytics

---

## API Documentation

Full API documentation is available in: `LLM_API_DOCUMENTATION.md`

Quick reference:
- **Health Check**: `GET /`
- **Generate Text**: `POST /generate`
- **Batch Generation**: `POST /batch-generate`

---

## Support

For issues:
1. Check Django logs: `/var/log/yourusername.pythonanywhere.com.error.log`
2. Check AI API status: `curl https://language-ai-api-atnpjnu3rq-nw.a.run.app/health`
3. Review admin panel for error messages
4. Test with simple prompts first

---

## Success Checklist

After deployment, verify:
- [x] Migrations ran successfully
- [x] AI Chat project is in Projects page
- [x] Navigation shows "AI Chat" for logged-in users
- [x] Can create new conversation
- [x] Can send messages and receive responses
- [x] Conversations appear in sidebar
- [x] Can switch between conversations
- [x] Admin can view all chats
- [x] Can delete conversations
- [x] Settings (temperature, tokens) work

---

**🎉 Your AI Chat feature is now live!**

Users can access it at: `http://yourdomain.com/ai-chat/`

Admin panel at: `http://yourdomain.com/admin/website/aichat/`

