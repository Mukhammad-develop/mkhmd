#!/bin/bash

# Deployment script for PythonAnywhere
# Run this on PythonAnywhere after pulling code

echo "🚀 Starting deployment..."

# Navigate to project directory
cd ~/mkhmd || exit

# Pull latest code
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Install/update dependencies
echo "📦 Installing dependencies..."
pip3.10 install --user -r requirements.txt

# Run migrations
echo "🗄️  Running database migrations..."
python3.10 manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python3.10 manage.py collectstatic --noinput

# Optional: Add initial data (only if needed)
read -p "Add Turnitin project? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3.10 manage.py add_turnitin_project
fi

read -p "Add sample projects? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3.10 manage.py add_sample_projects
fi

echo "✅ Deployment complete!"
echo "⚠️  Don't forget to reload your web app from the PythonAnywhere dashboard!"
echo "   Go to: Web tab → Click 'Reload' button for www.mkhmd.uk"

