# Portfolio Page - Dynamic Implementation

## What Changed

The portfolio page now fetches all project data from the database instead of using hardcoded lists. GitHub projects are synced to the database rather than fetched from the API on each page load.

## Key Changes

### 1. Updated `website/views.py` - portfolio() function
- Removed hardcoded `dev_projects` and `scraping_projects` lists
- Now fetches projects from the `Project` model:
  - `featured_projects`: Projects marked as featured
  - `scraping_projects`: Projects in the web_scraping category
  - `all_portfolio_projects`: All active projects
- GitHub projects now pulled from database (projects with github_url)
- Certifications, awards, testimonials, timeline events remain hardcoded (as requested)

### 2. Updated `website/templates/website/portfolio.html`
- Updated project loops to use Project model fields:
  - `project.title` - Title
  - `project.description` - Description
  - `project.get_technologies_list()` - Technologies as list
  - `project.get_status_display()` - Human-readable status
  - `project.get_category_display()` - Human-readable category
  - `project.github_url` - GitHub link
  - `project.demo_url` - Demo link
  - `project.icon` - Font Awesome icon class

### 3. New Management Command: `sync_github_projects`
**File:** `website/management/commands/sync_github_projects.py`

**Purpose:** Fetch projects from GitHub API and store them in the database

**Features:**
- Fetches repositories from GitHub API
- Skips forks with low activity
- Auto-detects category based on language and description
- Auto-assigns appropriate icons
- Creates or updates projects in database
- Marks GitHub projects with lower priority (order = 100)

**Usage:**
```bash
python3 manage.py sync_github_projects
```

## Deployment Steps for PythonAnywhere

### Quick Deploy Command:
```bash
cd ~/mkhmd && git pull origin main && python3.10 manage.py sync_github_projects && python3.10 manage.py collectstatic --noinput && touch /var/www/mkhmd_uk_pythonanywhere_com_wsgi.py && echo "✅ Portfolio updated!"
```

### Step-by-Step:
```bash
# 1. Navigate to project
cd ~/mkhmd

# 2. Pull latest changes
git pull origin main

# 3. Sync GitHub projects to database
python3.10 manage.py sync_github_projects

# 4. Collect static files
python3.10 manage.py collectstatic --noinput

# 5. Reload web app
touch /var/www/mkhmd_uk_pythonanywhere_com_wsgi.py

echo "✅ Done!"
```

## Managing Portfolio Projects

### Via Django Admin
1. Go to `/admin/website/project/`
2. View all projects (including synced GitHub projects)
3. Edit any project to customize:
   - Title, description, technologies
   - Category and status
   - Featured status
   - Display order (lower numbers show first)
   - Icons and images

### Featured Projects
To feature a project on the portfolio page:
1. Open project in admin
2. Check "is_featured" checkbox
3. Set lower "order" number for higher priority
4. Save

### Adding Manual Projects
You can still add projects manually via:
1. Django admin interface
2. Management commands (`add_turnitin_project`, `add_sample_projects`)
3. Django shell

### Re-syncing GitHub Projects
Run the sync command anytime to update projects from GitHub:
```bash
python3.10 manage.py sync_github_projects
```

This will:
- Add new repositories
- Update existing ones
- Not delete manual projects
- Not override featured status of existing projects

## Project Categories

The system auto-categorizes GitHub projects based on:
- **web_scraping**: Keywords like "scrap", "crawl", "extract", "spider"
- **automation**: Keywords like "automat", "bot", "selenium"
- **api_development**: Keywords like "api", "rest", "graphql"
- **data_extraction**: Keywords like "data", "extract", "etl"
- **machine_learning**: Keywords like "ml", "ai", "neural"
- **web_development**: JavaScript/TypeScript/HTML/CSS projects
- **other**: Everything else

## Local Testing Results

Successfully synced 10 GitHub repositories:
- Lang Scrape
- Itaat Byd Voice
- Restaurant Business Directory Scraper
- Smart Price Tracker
- Linkedin Scraper
- Grobovsheke Smsbomber
- Hix Bot
- Head Polling
- Yoki Yoki
- Coffee Shop

All projects are now visible in the admin and portfolio page.

## Troubleshooting

### Portfolio shows no projects
```bash
# Check if projects exist
python3.10 manage.py shell
>>> from website.models import Project
>>> Project.objects.filter(is_active=True).count()
```

If count is 0, run:
```bash
python3.10 manage.py sync_github_projects
python3.10 manage.py add_turnitin_project
python3.10 manage.py add_sample_projects
```

### GitHub sync fails
- Check internet connection
- Verify GitHub username in sync command
- Check GitHub API rate limits
- Projects will still display if already in database

### Projects don't show icons
- Verify icon field has Font Awesome class (e.g., "fas fa-code")
- Check Font Awesome CDN is loaded in template
- Default icon is "fas fa-code"

## Future Enhancements

Optional improvements you can add later:

1. **Track GitHub Stars/Forks**
   - Add fields to Project model
   - Update sync command to store them
   - Display in portfolio

2. **Auto-sync Schedule**
   - Set up cron job on PythonAnywhere
   - Run sync_github_projects daily/weekly

3. **Project Images**
   - Add image uploads to projects
   - Display in portfolio cards
   - Use GitHub repo social images

4. **Project Filtering**
   - Add category filter to portfolio page
   - Search functionality
   - Tag-based filtering

5. **Project Detail Pages**
   - Create dedicated page for each project
   - Show full features, tech stack, metrics
   - Link from portfolio cards

## Summary

✅ Portfolio page is now fully dynamic
✅ Projects managed via Django admin
✅ GitHub projects auto-sync to database
✅ Easy to add/edit/feature projects
✅ No more hardcoded project data
✅ Improved performance (no API calls on every page load)
✅ All existing project data preserved

The portfolio page now provides a professional, maintainable way to showcase your work!

