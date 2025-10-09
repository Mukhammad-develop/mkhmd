# ✅ Deployment Checklist

Use this checklist every time you deploy to PythonAnywhere.

## 📋 Pre-Deployment (Local Mac)

- [ ] All changes tested locally
- [ ] Server runs without errors (`python3 manage.py runserver`)
- [ ] Admin panel accessible and working
- [ ] Migrations created (`python3 manage.py makemigrations`)
- [ ] Migrations applied locally (`python3 manage.py migrate`)
- [ ] No sensitive data in code (passwords, API keys, etc.)
- [ ] `.gitignore` properly configured
- [ ] All files staged (`git add .`)
- [ ] Meaningful commit message written
- [ ] Code pushed to GitHub (`git push origin main`)

## 🚀 Deployment (PythonAnywhere)

- [ ] Logged into PythonAnywhere console
- [ ] Navigated to project directory (`cd ~/mkhmd`)
- [ ] Pulled latest code (`git pull origin main`)
- [ ] Checked for merge conflicts (if any, resolve them)
- [ ] Installed new dependencies (if requirements.txt changed)
  ```bash
  pip3.10 install --user -r requirements.txt
  ```
- [ ] Ran migrations (`python3.10 manage.py migrate`)
- [ ] Added initial data (if needed)
  ```bash
  python3.10 manage.py add_turnitin_project  # If first time
  python3.10 manage.py add_sample_projects   # If first time
  ```
- [ ] Collected static files (if static changed)
  ```bash
  python3.10 manage.py collectstatic --noinput
  ```
- [ ] Reloaded web app from dashboard
  - Go to: Web tab → Click "Reload www.mkhmd.uk"

## ✨ Post-Deployment Verification

- [ ] Website loads without errors (visit https://www.mkhmd.uk)
- [ ] Home page displays correctly
- [ ] Featured project shows up
- [ ] Coming soon projects display
- [ ] Admin panel accessible (https://www.mkhmd.uk/admin/)
- [ ] Projects can be added/edited in admin
- [ ] No JavaScript errors in browser console (F12)
- [ ] Mobile view looks good (test responsive design)
- [ ] All links work correctly

## 🐛 If Something Goes Wrong

- [ ] Check PythonAnywhere error logs
  - Dashboard → Web tab → Error log link
- [ ] Verify migrations applied
  ```bash
  python3.10 manage.py showmigrations
  ```
- [ ] Check if web app reloaded
- [ ] Verify file permissions
- [ ] Check database file exists and is writable
- [ ] Review recent commits for issues
- [ ] Roll back if needed (`git reset --hard HEAD~1`)

## 📝 Notes Section

Date: _______________
Deployed by: _______________
Changes made: _______________________________________________
Issues encountered: _________________________________________
Resolution: ________________________________________________

---

## 🎯 Quick Commands Reference

### Must Run Every Deployment:
```bash
cd ~/mkhmd
git pull origin main
python3.10 manage.py migrate
# Reload web app from dashboard
```

### Optional (Only When Needed):
```bash
pip3.10 install --user -r requirements.txt  # If dependencies changed
python3.10 manage.py collectstatic --noinput  # If static files changed
python3.10 manage.py add_turnitin_project  # First time only
python3.10 manage.py add_sample_projects   # First time only
```

### Useful Debug Commands:
```bash
python3.10 manage.py showmigrations  # Check migration status
python3.10 manage.py check           # System check
python3.10 manage.py shell           # Django shell for testing
tail -f /var/log/mkhmd.uk.error.log  # Watch error logs
```

---

**Pro Tip:** Save this checklist and tick off items as you go to avoid missing critical steps!

