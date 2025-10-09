# Schedule System Deployment Guide

## What's New

This update adds a complete scheduling and booking system to replace the timeline page:

### New Features
1. **All Active Projects Display** - The `/projects/` page now shows ALL active projects dynamically
2. **Schedule Page** - New `/schedule/` page replaces `/timeline/`
3. **Booking System** - Users can view your availability and book appointments
4. **Time Slot Management** - Admin can define weekly availability slots
5. **Booking Management** - Track and manage all appointment requests

### New Models
- `TimeSlot` - Define your weekly availability
- `Booking` - Store client appointment requests

## Deployment Commands for PythonAnywhere

Run these commands in order on your PythonAnywhere bash console:

```bash
# 1. Navigate to project directory
cd ~/mkhmd

# 2. Pull latest changes
git pull origin main

# 3. Run migrations to create new tables
python3.10 manage.py migrate

# 4. Add default time slots (Monday-Friday, 9 AM - 5 PM)
python3.10 manage.py add_time_slots

# 5. Collect static files
python3.10 manage.py collectstatic --noinput

# 6. Reload web app
touch /var/www/mkhmd_uk_pythonanywhere_com_wsgi.py

echo "✅ Deployment complete!"
```

## Quick One-Liner

```bash
cd ~/mkhmd && git pull origin main && python3.10 manage.py migrate && python3.10 manage.py add_time_slots && python3.10 manage.py collectstatic --noinput && touch /var/www/mkhmd_uk_pythonanywhere_com_wsgi.py && echo "✅ All done!"
```

## Post-Deployment Steps

### 1. Configure Your Availability

Go to Django Admin → Time Slots:
- Default slots are Monday-Friday, 9 AM - 5 PM
- Edit existing slots or add custom ones
- Set `is_active` to control which slots are available
- Customize `duration_minutes` for different slot lengths

### 2. Customize Booking Types (Optional)

The booking types are currently hardcoded in the view. You can customize them in `website/views.py` in the `schedule()` function.

### 3. Test the Booking System

1. Visit `/schedule/` on your site
2. Select a date from the calendar
3. Choose a booking type
4. Fill out the booking form
5. Submit and check Django Admin → Bookings

### 4. Set Up Email Notifications (Optional)

To get notified when someone books an appointment, you can:
1. Add a signal in `website/signals.py`
2. Send email on `Booking` creation
3. Use your existing email configuration

Example signal:
```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking
from django.core.mail import send_mail

@receiver(post_save, sender=Booking)
def notify_new_booking(sender, instance, created, **kwargs):
    if created:
        send_mail(
            f'New Booking Request: {instance.subject}',
            f'New booking from {instance.name} ({instance.email})\n'
            f'Date: {instance.date} at {instance.start_time}\n'
            f'Type: {instance.get_booking_type_display()}\n'
            f'Message: {instance.message}',
            'noreply@mkhmd.uk',
            ['your-email@example.com'],
            fail_silently=True,
        )
```

## Managing Bookings

### Via Django Admin
1. Go to `/admin/website/booking/`
2. View all bookings sorted by date
3. Update status: pending → confirmed/cancelled/completed
4. Add notes for internal tracking
5. Use filters to find specific bookings

### Common Admin Actions
- **Confirm booking**: Change status to "confirmed"
- **Cancel booking**: Change status to "cancelled" and add notes
- **Complete booking**: After meeting, change to "completed"
- **View upcoming**: Filter by date >= today, status = confirmed

## URL Changes

| Old URL | New URL | Description |
|---------|---------|-------------|
| `/timeline/` | `/schedule/` | Main schedule page |
| N/A | `/schedule/book/` | Booking submission endpoint |

## Navigation Update

The navigation bar has been updated:
- "Timeline" link → "Schedule" link
- Points to the new schedule page
- Active state works correctly

## Database Schema

### TimeSlot Table
```
- id: Primary Key
- weekday: Integer (0=Monday, 6=Sunday)
- start_time: Time field
- end_time: Time field
- duration_minutes: Integer (default 60)
- is_active: Boolean (default True)
- created_at: DateTime
- updated_at: DateTime
```

### Booking Table
```
- id: Primary Key
- name: CharField (client name)
- email: EmailField
- phone: CharField (optional)
- company: CharField (optional)
- date: DateField
- start_time: TimeField
- end_time: TimeField
- duration_minutes: Integer
- subject: CharField
- message: TextField
- booking_type: CharField (consultation, project_discussion, etc.)
- status: CharField (pending, confirmed, cancelled, completed)
- notes: TextField (admin only)
- created_at: DateTime
- updated_at: DateTime
```

## Troubleshooting

### If migrations fail:
```bash
python3.10 manage.py showmigrations
python3.10 manage.py migrate website --fake-initial
```

### If time slots don't show:
```bash
python3.10 manage.py shell
>>> from website.models import TimeSlot
>>> TimeSlot.objects.count()  # Should be > 0
>>> TimeSlot.objects.all()  # View all slots
```

### If bookings don't save:
- Check browser console for JavaScript errors
- Check Django logs
- Verify CSRF token is working
- Test with curl:
```bash
curl -X POST https://www.mkhmd.uk/schedule/book/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@test.com","date":"2025-10-15","start_time":"10:00","end_time":"11:00","duration_minutes":60,"subject":"Test","message":"Test","booking_type":"consultation"}'
```

## Features to Add Later (Optional)

1. **Email Confirmation** - Send confirmation emails to clients
2. **Calendar Integration** - Export to Google Calendar, iCal
3. **Payment Integration** - For paid consultations
4. **Timezone Handling** - Auto-detect client timezone
5. **Video Call Links** - Auto-generate Zoom/Meet links
6. **Reminders** - Send reminder emails before appointments
7. **Recurring Availability** - Easier bulk time slot creation
8. **Conflict Detection** - Prevent double bookings automatically

## Support

If you encounter issues:
1. Check Django error logs on PythonAnywhere
2. Check browser console for frontend errors
3. Verify database migrations are applied
4. Test in local environment first

## Summary

✅ Projects page now shows ALL active projects
✅ Timeline replaced with Schedule
✅ Full booking system with calendar UI
✅ Admin interface to manage availability and bookings
✅ Professional, modern design matching site aesthetic
✅ Mobile-responsive interface
✅ Real-time availability checking

Your site now has a professional scheduling system where clients can book appointments directly!

