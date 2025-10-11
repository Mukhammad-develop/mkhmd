# Admin Dashboard Guide

## Overview

As an admin, you have full access to manage all aspects of your website through the Django admin interface at `/admin/`.

## What You Can Manage

### 1. 📅 Scheduled Meetings (Bookings)

**Location:** `/admin/website/booking/`

#### Features:
- **Rich Display**: See client info, meeting details, status badges, and time until meeting
- **Color-Coded Status**:
  - 🟠 **Pending** (Orange) - Awaiting your confirmation
  - 🟢 **Confirmed** (Green) - Meeting confirmed
  - 🔴 **Cancelled** (Red) - Meeting cancelled
  - ⚫ **Completed** (Gray) - Past meeting completed
  
- **Quick Info View**:
  - Client name, email, phone, company
  - Meeting date & time with duration
  - Meeting type (Consultation, Project Discussion, etc.)
  - Subject and full message
  - Time remaining until meeting

#### Admin Actions:
1. **Bulk Confirm**: Select multiple bookings and mark as confirmed
2. **Bulk Complete**: Mark past meetings as completed
3. **Bulk Cancel**: Cancel multiple bookings at once

#### Filtering:
- Filter by status, booking type, date range
- Date hierarchy for easy navigation
- Search by name, email, company, subject

#### Detail View:
- Full meeting summary with all details
- Client information section
- Appointment details
- Meeting purpose and message
- Status and admin notes section
- Timestamps (created/updated)

### 2. 👥 Users & Their Information

**Location:** `/admin/accounts/user/`

#### What You Can See:
- **User List**:
  - Email, username, full name
  - Email verification status
  - Turnitin balance
  - Staff/superuser status
  - Registration date

- **User Details**:
  - Personal info (name, email, bio, location, website)
  - Authentication (password, last login, date joined)
  - Permissions (staff status, active status, groups)
  - Profile information (inline):
    - Phone, date of birth
    - Company, job title
    - Social links (GitHub, LinkedIn, Twitter)
    - Email preferences
    - Profile visibility

#### User Filters:
- Staff status
- Superuser status
- Active status
- Email verified status
- Registration date

#### User Search:
Search by email, username, first name, or last name

### 3. 👤 User Profiles

**Location:** `/admin/accounts/userprofile/`

#### Information Available:
- Personal details (phone, birth date)
- Professional info (company, job title)
- Social media links
- Notification preferences
- Profile visibility settings
- Creation and update timestamps

### 4. 📧 Email Verifications

**Location:** `/admin/accounts/emailverification/`

#### Track:
- User email verifications
- Verification codes
- Expiration status (color-coded: green=valid, red=expired)
- Usage status
- Creation and expiration times

### 5. 📄 Turnitin Submissions

**Location:** `/admin/accounts/turnitinsubmission/`

#### Monitor:
- Submission IDs and access codes
- User who submitted
- Submission status (✅ Completed / ⏳ Ongoing)
- Similarity and AI percentages
- Submission dates
- Result files (similarity & AI reports)

### 6. ⏰ Time Slots (Your Availability)

**Location:** `/admin/website/timeslot/`

#### Manage Your Schedule:
- Weekday availability (Monday-Sunday)
- Start and end times
- Appointment duration (in minutes)
- Active/inactive status (quick edit from list)
- Creation timestamps

#### Quick Edit:
Toggle time slots on/off directly from the list view

### 7. 🚀 Projects

**Location:** `/admin/website/project/`

#### Project Management:
- Title, slug, descriptions
- Category and status
- Technologies and features
- Links (GitHub, demo, docs)
- Media (icon, images)
- Statistics (lines of code, success rate, availability)
- Display options (featured, active, order)

#### Features:
- Quick edit: featured status, active status, and display order
- Auto-populate slug from title
- Organized fieldsets for easy editing
- Filter by status, category, featured status
- Search by title, description, technologies

## Quick Access URLs

When logged in as admin:

```
Main Admin Dashboard:     /admin/
Bookings (Meetings):      /admin/website/booking/
Users:                    /admin/accounts/user/
User Profiles:            /admin/accounts/userprofile/
Email Verifications:      /admin/accounts/emailverification/
Turnitin Submissions:     /admin/accounts/turnitinsubmission/
Time Slots:               /admin/website/timeslot/
Projects:                 /admin/website/project/
```

## Common Admin Tasks

### Managing Scheduled Meetings

#### Confirm a New Booking:
1. Go to `/admin/website/booking/`
2. Find pending bookings (orange status)
3. Click on booking to view details
4. Review meeting summary
5. Change status dropdown to "Confirmed"
6. Add any notes for yourself
7. Click "Save"

#### Bulk Actions:
1. Select multiple bookings using checkboxes
2. Choose action from dropdown:
   - "✅ Mark selected as Confirmed"
   - "✔️ Mark selected as Completed"
   - "❌ Mark selected as Cancelled"
3. Click "Go"

#### View Today's Meetings:
1. Go to `/admin/website/booking/`
2. Bookings marked "TODAY" are highlighted in orange
3. See "Time Until" column for upcoming meetings

### Managing Users

#### View User Details:
1. Go to `/admin/accounts/user/`
2. Click on any user's email
3. View all information including:
   - Personal details
   - Profile information (inline)
   - Permissions
   - Important dates

#### Give User Staff Access:
1. Open user in admin
2. Scroll to "Permissions" section
3. Check "Staff status"
4. Save

#### Check User's Turnitin Usage:
1. Go to `/admin/accounts/turnitinsubmission/`
2. Filter by user or search their email
3. View all submissions and results

### Managing Your Availability

#### Add New Time Slot:
1. Go to `/admin/website/timeslot/`
2. Click "Add Time Slot"
3. Select weekday (0=Monday, 6=Sunday)
4. Set start time and end time
5. Set duration per appointment slot
6. Check "Is active"
7. Save

#### Disable Time Slot Temporarily:
1. Go to `/admin/website/timeslot/`
2. Uncheck "Is active" for that slot (editable from list)
3. Changes save automatically

### Managing Projects

#### Feature a Project:
1. Go to `/admin/website/project/`
2. Find your project
3. Check "Is featured" column (editable from list)
4. Set lower "Order" number for higher priority
5. Changes save automatically

#### Add New Project:
1. Click "Add Project"
2. Fill in basic information (title auto-generates slug)
3. Add project details (category, status, technologies)
4. Add links and media
5. Set display options
6. Save

## Dashboard Tips

### Color Codes to Know:

**Booking Status:**
- 🟠 Orange = Pending (needs your action)
- 🟢 Green = Confirmed
- 🔴 Red = Cancelled
- ⚫ Gray = Completed

**Time Until Meeting:**
- Green = Days away
- Orange = Hours away
- Red = Minutes away (urgent!)

**Email Verification:**
- Green = Valid code
- Red = Expired code

**Turnitin Status:**
- ✅ Green = Completed
- ⏳ Orange = Ongoing

### Best Practices:

1. **Check bookings daily** for new pending requests
2. **Confirm bookings promptly** to notify clients
3. **Add notes** to bookings for context
4. **Mark completed** after meetings for record-keeping
5. **Update time slots** when schedule changes
6. **Review user profiles** before important meetings
7. **Monitor Turnitin balance** for active users

## Permissions & Security

### Admin Levels:

1. **Superuser** (You):
   - Full access to everything
   - Can create other admins
   - Can manage all models

2. **Staff Users**:
   - Access to admin interface
   - Limited permissions (configured per user)
   - Cannot access everything by default

3. **Regular Users**:
   - No admin access
   - Use public website only

### Security Tips:
- Keep admin credentials secure
- Use strong passwords
- Log out when done
- Review staff permissions regularly
- Monitor user activity through logs

## Troubleshooting

### Can't see bookings?
- Check if you're logged in as admin
- Verify URL: `/admin/website/booking/`
- Check if any bookings exist in database

### Status not updating?
- Click "Save" after changing status
- Check if you have edit permissions
- Refresh the page

### Time slots not showing on schedule page?
- Go to `/admin/website/timeslot/`
- Verify "Is active" is checked
- Confirm start_time < end_time
- Check weekday is set correctly

### Projects not displaying?
- Verify "Is active" is checked
- Check display order (lower = higher priority)
- Ensure project has required fields filled

## Support

For any issues or questions:
1. Check this guide first
2. Review Django admin documentation
3. Check application logs
4. Contact system administrator

---

## Summary

As an admin, you have complete control over:
- ✅ All scheduled meetings and bookings
- ✅ All user accounts and their information
- ✅ User profiles and preferences
- ✅ Email verifications and security
- ✅ Turnitin submissions and results
- ✅ Your availability schedule
- ✅ Portfolio projects display

The admin interface is designed to give you comprehensive oversight and efficient management tools. Everything is searchable, filterable, and organized for quick access.

**Your admin dashboard is your command center - use it to stay organized and responsive!** 🚀

