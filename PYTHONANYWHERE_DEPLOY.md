# PythonAnywhere Deployment Guide

## Complete Deployment Command

Run this **ONE command** in your PythonAnywhere bash console to deploy all updates:

```bash
cd ~/mkhmd && \
git pull origin main && \
python3.10 manage.py migrate && \
python3.10 manage.py add_time_slots && \
python3.10 manage.py sync_github_projects && \
python3.10 manage.py collectstatic --noinput && \
touch /var/www/mkhmd_uk_pythonanywhere_com_wsgi.py && \
echo "✅ Deployment complete!"
```

## What This Does:

1. **`cd ~/mkhmd`** - Navigate to your project directory
2. **`git pull origin main`** - Pull latest code from GitHub
3. **`python3.10 manage.py migrate`** - Create new database tables (TimeSlot, Booking, ChatSession, ChatMessage)
4. **`python3.10 manage.py add_time_slots`** - Add default availability schedule
5. **`python3.10 manage.py sync_github_projects`** - Sync GitHub projects to database
6. **`python3.10 manage.py collectstatic --noinput`** - Collect static files
7. **`touch /var/www/mkhmd_uk_pythonanywhere_com_wsgi.py`** - Reload web app
8. **`echo "✅ Deployment complete!"`** - Show success message

## Step-by-Step (If You Prefer):

```bash
# 1. Go to project directory
cd ~/mkhmd

# 2. Pull latest code
git pull origin main

# 3. Run migrations (CREATE NEW TABLES)
python3.10 manage.py migrate

# 4. Add default time slots (OPTIONAL - only if you want default schedule)
python3.10 manage.py add_time_slots

# 5. Sync GitHub projects (OPTIONAL - only if you want GitHub projects in database)
python3.10 manage.py sync_github_projects

# 6. Collect static files
python3.10 manage.py collectstatic --noinput

# 7. Reload web app
touch /var/www/mkhmd_uk_pythonanywhere_com_wsgi.py

echo "✅ Done!"
```

## Quick Deploy (Minimal - Just Fix the Error):

If you just want to fix the current error and deploy quickly:

```bash
cd ~/mkhmd && git pull origin main && python3.10 manage.py migrate && touch /var/www/mkhmd_uk_pythonanywhere_com_wsgi.py && echo "✅ Fixed!"
```

## Troubleshooting

### If `git pull` fails with "local changes" error:

```bash
cd ~/mkhmd
git stash
git pull origin main
git stash pop
```

### If migrations fail:

```bash
# Check which migrations are missing
python3.10 manage.py showmigrations

# Run migrations again
python3.10 manage.py migrate
```

### If you get "command not found" errors:

Make sure you're using `python3.10` not `python3` or `python`:
```bash
python3.10 --version  # Should show Python 3.10.x
```

### To verify tables were created:

```bash
python3.10 manage.py shell
>>> from website.models import TimeSlot, Booking, ChatSession
>>> TimeSlot.objects.count()  # Should return 0 or more
>>> Booking.objects.count()   # Should return 0 or more
>>> ChatSession.objects.count() # Should return 0 or more
>>> exit()
```

## What's New in This Deployment:

### 1. Schedule/Booking System
- **Models**: TimeSlot, Booking
- **URLs**: `/schedule/`, `/schedule/book/`
- **Admin**: Manage bookings and availability
- **Tables**: `website_timeslot`, `website_booking`

### 2. Dynamic Portfolio
- **Updated**: Projects fetched from database
- **Command**: `sync_github_projects` to populate
- **Admin**: Manage projects at `/admin/website/project/`

### 3. Live Chat System
- **Models**: ChatSession, ChatMessage
- **URLs**: `/api/chat/init/`, `/api/chat/send/`, `/api/chat/messages/`
- **Widget**: Purple chat button on all pages
- **Admin**: Manage chats at `/admin/website/chatsession/`
- **Tables**: `website_chatsession`, `website_chatmessage`

### 4. Enhanced Admin Interface
- Better booking management with bulk actions
- Chat session management with unread badges
- Rich displays with colors and summaries

## Regular Deployment Workflow

Whenever you make changes locally and push to GitHub:

1. **Local**: 
   ```bash
   git add -A
   git commit -m "Your changes"
   git push origin main
   ```

2. **PythonAnywhere**:
   ```bash
   cd ~/mkhmd && git pull origin main && python3.10 manage.py migrate && python3.10 manage.py collectstatic --noinput && touch /var/www/mkhmd_uk_pythonanywhere_com_wsgi.py
   ```

## Important Notes

### Database on PythonAnywhere:
- Your PythonAnywhere database is separate from local
- `db.sqlite3` is in `.gitignore` (not tracked)
- Migrations create tables on each server independently
- Data doesn't transfer automatically between local and production

### After First Deployment:
You may want to:
1. Go to `/admin/website/timeslot/` and customize your availability
2. Go to `/admin/website/project/` and mark projects as featured
3. Test the chat widget on your live site
4. Test the booking form at `/schedule/`

### Static Files:
- Always run `collectstatic` after pulling code
- This copies CSS/JS to the static directory
- Required for new templates/styles to work

## Automation (Optional)

To avoid manual deployment, you can set up automatic deployment:

### Option 1: GitHub Webhook
Set up a webhook that auto-deploys when you push to GitHub
(Requires paid PythonAnywhere account)

### Option 2: Scheduled Task
Create a PythonAnywhere scheduled task that runs every hour:
```bash
cd ~/mkhmd && git pull origin main && python3.10 manage.py migrate && python3.10 manage.py collectstatic --noinput && touch /var/www/mkhmd_uk_pythonanywhere_com_wsgi.py
```

### Option 3: Deploy Script
Create a file `~/deploy.sh`:
```bash
#!/bin/bash
cd ~/mkhmd
git pull origin main
python3.10 manage.py migrate
python3.10 manage.py collectstatic --noinput
touch /var/www/mkhmd_uk_pythonanywhere_com_wsgi.py
echo "✅ Deployed!"
```

Make it executable:
```bash
chmod +x ~/deploy.sh
```

Then just run:
```bash
~/deploy.sh
```

## Summary

**Current Issue**: Database tables don't exist
**Solution**: Run migrations with `python3.10 manage.py migrate`

**Full deployment command**:
```bash
cd ~/mkhmd && git pull origin main && python3.10 manage.py migrate && python3.10 manage.py collectstatic --noinput && touch /var/www/mkhmd_uk_pythonanywhere_com_wsgi.py
```

This will:
✅ Pull latest code
✅ Create all missing database tables
✅ Collect static files
✅ Reload your website

Your site should then work perfectly at https://www.mkhmd.uk/

