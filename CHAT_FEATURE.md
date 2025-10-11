# Live Chat Feature Documentation

## Overview

Your website now has a professional live chat system where visitors can message you directly. All conversations are managed through the Django admin interface.

## Features

### For Visitors:
- ✅ Floating chat widget on all pages (bottom-right corner)
- ✅ Optional name/email before starting chat
- ✅ Real-time messaging
- ✅ Persistent chat sessions (saves in browser)
- ✅ Unread message notifications
- ✅ Mobile-responsive design
- ✅ Beautiful purple gradient design matching your brand

### For Admin (You):
- ✅ View all chat conversations in `/admin/website/chatsession/`
- ✅ Rich admin interface with:
  - Visitor information (name, email)
  - Unread message badges
  - Last message preview
  - Conversation summaries
  - Full chat history
- ✅ Bulk actions (mark as read, close chats)
- ✅ Reply to visitors directly from admin
- ✅ Search and filter conversations
- ✅ Track active vs closed chats

## How It Works

### For Visitors:

1. **Chat Button**: Purple circular button appears on bottom-right of every page
2. **Start Chat**: Click button → optionally enter name/email → start chatting
3. **Send Messages**: Type message and press Enter or click send button
4. **Receive Replies**: Admin replies appear automatically (polls every 3 seconds)
5. **Persistent**: Chat session saves in browser, can continue later

### For Admin:

1. **View Chats**: Go to `/admin/website/chatsession/`
2. **See Unread**: Red badges show new unread messages
3. **Open Chat**: Click on any chat to see full conversation
4. **Read Messages**: All messages displayed inline
5. **Mark as Read**: Use bulk action or individual chat status

## Admin Interface

### Chat Sessions (`/admin/website/chatsession/`)

**List View Shows:**
- Visitor info (name, email, or anonymous ID)
- Unread message count with red badge
- Last message preview
- Active/closed status
- Last activity time

**Detail View Shows:**
- Conversation summary box with:
  - Total messages
  - Unread count
  - Status (active/closed)
  - Start time
  - Last activity
- All messages in chronological order
- Visitor details
- Admin notes field

**Bulk Actions:**
- ✅ Mark selected as Read
- 🔒 Close selected chats

**Filters:**
- Active/Closed status
- Read/Unread by admin
- Creation date

### Chat Messages (`/admin/website/chatmessage/`)

- View individual messages
- Filter by sender (Admin/Visitor)
- Filter by read status
- Search message content

## Usage Instructions

### As a Visitor:

```
1. Visit any page on the website
2. Look for purple chat button (bottom-right)
3. Click to open chat window
4. (Optional) Enter your name and email
5. Click "Start Chat"
6. Type your message
7. Press Enter or click send button
8. Wait for admin response (appears automatically)
```

### As Admin:

**Viewing New Messages:**
```
1. Go to /admin/website/chatsession/
2. Look for red "X New" badges
3. Click on chat to view
4. Read messages in detail view
5. Messages auto-mark as read when you view them
```

**Replying to Chats:**
Currently, you need to reply via the frontend chat widget:
```
1. Open your website in a browser
2. Log in as admin
3. Open chat widget
4. Your messages will be marked as "from admin"
```

**Alternative - Admin Reply Feature** (Future Enhancement):
You can add a reply box directly in the admin interface.

**Managing Conversations:**
```
# Mark multiple chats as read:
1. Select chats using checkboxes
2. Choose "Mark selected as Read" from Actions dropdown
3. Click "Go"

# Close conversations:
1. Select chats
2. Choose "Close selected chats"
3. Click "Go"
```

## API Endpoints

The chat system uses these endpoints:

- `POST /api/chat/init/` - Initialize or resume chat session
- `POST /api/chat/send/` - Send a message
- `GET /api/chat/messages/` - Poll for new messages

## Database Models

### ChatSession
```python
- session_id: UUID (unique identifier)
- user: ForeignKey to User (if logged in)
- visitor_name: CharField (for anonymous users)
- visitor_email: EmailField (for anonymous users)
- is_active: Boolean (active/closed)
- is_read_by_admin: Boolean (has admin seen this?)
- created_at, updated_at: DateTime
```

### ChatMessage
```python
- session: ForeignKey to ChatSession
- message: TextField (message content)
- is_from_admin: Boolean (who sent it?)
- is_read: Boolean (has recipient seen it?)
- created_at: DateTime
```

## Customization

### Change Chat Colors:
Edit `website/templates/website/chat_widget.html`:
```css
background: linear-gradient(135deg, var(--primary-purple), var(--light-purple));
```

### Change Poll Interval:
In `chat_widget.html`, find:
```javascript
pollInterval = setInterval(async () => {
    // ...
}, 3000); // Change 3000 to desired milliseconds
```

### Change Widget Position:
In `chat_widget.html`, find `.chat-widget`:
```css
.chat-widget {
    bottom: 20px;  /* Change this */
    right: 20px;   /* Change this */
}
```

### Add Welcome Message:
In admin, you can manually add a ChatSession with an initial message from admin.

## Deployment to PythonAnywhere

```bash
cd ~/mkhmd && \
git pull origin main && \
python3.10 manage.py migrate && \
python3.10 manage.py collectstatic --noinput && \
touch /var/www/mkhmd_uk_pythonanywhere_com_wsgi.py && \
echo "✅ Chat feature deployed!"
```

## Testing Locally

1. **Start Server**: `python3 manage.py runserver`
2. **Open Site**: Visit `http://localhost:8000/`
3. **Test Chat**: Click chat button, send message
4. **Check Admin**: Go to `http://localhost:8000/admin/website/chatsession/`
5. **View Message**: Should see your test message

## Troubleshooting

### Chat button not appearing:
- Check browser console for errors
- Verify `chat_widget.html` is included in `base.html`
- Clear browser cache

### Messages not sending:
- Check browser console for API errors
- Verify CSRF token is working
- Check Django logs

### Admin not seeing messages:
- Go to `/admin/website/chatsession/`
- Refresh page
- Check if chat session was created
- Look in `/admin/website/chatmessage/` for individual messages

### Poll not working:
- Check browser console
- Verify `/api/chat/messages/` endpoint is accessible
- Check network tab in browser dev tools

## Security Considerations

1. **CSRF Protection**: All POST requests use `@csrf_exempt` for simplicity
   - In production, consider implementing proper CSRF tokens
   
2. **Rate Limiting**: Consider adding rate limiting to prevent spam
   - Install `django-ratelimit`
   - Add to chat endpoints

3. **Admin Verification**: Admin replies require `is_staff` status

4. **Session Storage**: Chat sessions stored in browser localStorage
   - Cleared if user clears browser data
   - Secure for temporary conversations

## Future Enhancements

### Recommended Additions:

1. **Admin Reply from Admin Panel**
   - Add reply form directly in admin interface
   - No need to open frontend widget

2. **Email Notifications**
   - Send email to admin when new message arrives
   - Send email to visitor when admin replies

3. **WebSocket Support**
   - Real-time updates without polling
   - Use Django Channels
   - More efficient than HTTP polling

4. **File Attachments**
   - Allow image/file sharing
   - Add file upload to chat widget

5. **Chat History Export**
   - Export conversations as PDF/text
   - For record keeping

6. **Typing Indicators**
   - Show "Admin is typing..." when admin is replying
   - Show "Visitor is typing..." in admin panel

7. **Read Receipts**
   - Show checkmarks when messages are read
   - Double checkmark for read by both parties

8. **Chat Transcripts**
   - Auto-email transcript to visitor after chat closes
   - Save for customer support records

## Summary

✅ **Live chat widget** on all pages
✅ **Beautiful UI** matching your brand
✅ **Admin interface** to view/manage all chats
✅ **Real-time messaging** with automatic polling
✅ **Persistent sessions** saved in browser
✅ **Unread notifications** with badges
✅ **Mobile responsive** works on all devices
✅ **Easy to use** for both visitors and admin

Your website now has professional live chat capabilities! Visitors can reach you instantly, and you can manage all conversations from the Django admin panel.

**Access your chat admin at**: `http://localhost:8000/admin/website/chatsession/` (or `https://www.mkhmd.uk/admin/website/chatsession/` on production)

