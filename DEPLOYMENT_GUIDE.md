# 🚀 Deployment Guide

## Overview
This guide explains how to deploy code changes from your local Mac to PythonAnywhere when database models are involved.

## 🔑 Key Concepts

### What Gets Synced via Git?
- ✅ Code files (Python, HTML, CSS, JS)
- ✅ Migration files (`website/migrations/*.py`)
- ✅ Configuration files
- ❌ Database file (`db.sqlite3` - gitignored)
- ❌ Media files (user uploads - gitignored)
- ❌ Python cache (`__pycache__/` - gitignored)

### Why Migrations Matter
- Migration files are version control for your database schema
- They allow you to recreate the database structure on any server
- Each environment runs migrations on its own database

---

## 📝 Step-by-Step Deployment Process

### On Your Local Machine (Mac):

```bash
# 1. Create migrations for model changes
python3 manage.py makemigrations

# 2. Test migrations locally
python3 manage.py migrate

# 3. Test the application
python3 manage.py runserver
# Visit http://127.0.0.1:8000 and verify everything works

# 4. Check migration files are created
ls website/migrations/
# You should see: 0001_initial.py (or similar)

# 5. Stage all changes
git add .

# 6. Commit with descriptive message
git commit -m "Add dynamic Project model with admin interface"

# 7. Push to GitHub
git push origin main
```

---

### On PythonAnywhere:

#### **Option 1: Manual Deployment**

```bash
# 1. SSH into PythonAnywhere or use their console

# 2. Navigate to project directory
cd ~/mkhmd

# 3. Pull latest code
git pull origin main

# 4. Install/update dependencies (if requirements.txt changed)
pip3.10 install --user -r requirements.txt

# 5. Run migrations (creates tables in production database)
python3.10 manage.py migrate

# 6. Add initial data (if needed)
python3.10 manage.py add_turnitin_project
python3.10 manage.py add_sample_projects

# 7. Collect static files (if static files changed)
python3.10 manage.py collectstatic --noinput

# 8. Reload web app
# Go to PythonAnywhere dashboard → Web tab → Click "Reload www.mkhmd.uk"
```

#### **Option 2: Using Deployment Script**

```bash
# Make script executable (first time only)
chmod +x deploy_to_pythonanywhere.sh

# Run deployment script
./deploy_to_pythonanywhere.sh
```

---

## 🎯 Common Scenarios

### Scenario 1: Added New Model or Field
```bash
# Local:
python3 manage.py makemigrations
python3 manage.py migrate
git add .
git commit -m "Add new field to Project model"
git push

# PythonAnywhere:
git pull
python3.10 manage.py migrate
# Reload web app
```

### Scenario 2: Changed Existing Code (No Model Changes)
```bash
# Local:
git add .
git commit -m "Updated home page design"
git push

# PythonAnywhere:
git pull
# Reload web app (no migrations needed)
```

### Scenario 3: Added New Dependencies
```bash
# Local:
pip install new-package
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Add new-package dependency"
git push

# PythonAnywhere:
git pull
pip3.10 install --user -r requirements.txt
# Reload web app
```

### Scenario 4: First Time Deployment
```bash
# PythonAnywhere:
git clone https://github.com/YOUR_USERNAME/mkhmd.git
cd mkhmd
pip3.10 install --user -r requirements.txt
python3.10 manage.py migrate
python3.10 manage.py add_turnitin_project
python3.10 manage.py add_sample_projects
python3.10 manage.py createsuperuser
python3.10 manage.py collectstatic --noinput
# Configure web app in PythonAnywhere dashboard
# Reload web app
```

---

## ⚠️ Important Warnings

### Never Do This:
- ❌ Don't delete migration files (they're version control)
- ❌ Don't edit migration files manually (unless you know what you're doing)
- ❌ Don't commit `db.sqlite3` to git
- ❌ Don't run `makemigrations` on production (always do it locally first)

### Always Do This:
- ✅ Create migrations locally before pushing
- ✅ Test migrations locally before deploying
- ✅ Commit migration files to git
- ✅ Run `migrate` on production after pulling
- ✅ Reload web app after deployment

---

## 🔍 Troubleshooting

### Issue: "No migrations to apply"
**Cause:** Migrations already applied or migration files not pulled
**Solution:** 
```bash
git pull origin main  # Make sure you have latest migrations
python3.10 manage.py showmigrations  # Check which migrations are applied
```

### Issue: "Database is locked"
**Cause:** Another process is using the database
**Solution:** 
```bash
# Check if dev server is running and stop it
# Or wait a few seconds and try again
```

### Issue: "Migration conflicts"
**Cause:** Multiple people created migrations at the same time
**Solution:** 
```bash
# This is advanced - reach out for help or:
python3 manage.py makemigrations --merge
```

### Issue: Web app shows old version after deployment
**Cause:** Forgot to reload web app
**Solution:** 
- Go to PythonAnywhere dashboard
- Click "Web" tab
- Click green "Reload" button for your domain

---

## 📚 Quick Reference Commands

### Local Development
```bash
python3 manage.py makemigrations      # Create migration files
python3 manage.py migrate             # Apply migrations
python3 manage.py runserver           # Start dev server
git add .                             # Stage changes
git commit -m "message"               # Commit changes
git push origin main                  # Push to GitHub
```

### PythonAnywhere Production
```bash
git pull origin main                  # Pull latest code
pip3.10 install --user -r requirements.txt  # Install dependencies
python3.10 manage.py migrate          # Apply migrations
python3.10 manage.py collectstatic --noinput  # Collect static files
# Then reload web app from dashboard
```

---

## 🎓 Understanding Migrations

### What Happens When You Run `makemigrations`?
1. Django compares your models.py with current database schema
2. Creates Python files describing the changes
3. Saves these files in `app/migrations/`

### What Happens When You Run `migrate`?
1. Django checks which migrations haven't been applied yet
2. Runs the migration code to modify the database
3. Records which migrations have been applied

### Migration Files Are:
- Version control for your database
- Reversible (you can undo them)
- Applied in order (numbered: 0001, 0002, etc.)
- Shareable via git

---

## 💡 Pro Tips

1. **Always test locally first** - Never try new migrations directly on production
2. **Commit migration files immediately** - Don't forget them
3. **Use descriptive commit messages** - Makes tracking changes easier
4. **Keep migrations small** - Easier to debug if something goes wrong
5. **Backup production database** - Before major migrations
6. **Check migration status**: `python manage.py showmigrations`
7. **View SQL**: `python manage.py sqlmigrate website 0001`

---

## 🔗 Useful Links

- [Django Migrations Documentation](https://docs.djangoproject.com/en/4.2/topics/migrations/)
- [PythonAnywhere Help Pages](https://help.pythonanywhere.com/)
- [Git Documentation](https://git-scm.com/doc)

---

## 📞 Need Help?

If you encounter issues:
1. Check the error message carefully
2. Run `python3.10 manage.py showmigrations` to see migration status
3. Check PythonAnywhere error logs (Error log link in Web tab)
4. Make sure you reloaded the web app

