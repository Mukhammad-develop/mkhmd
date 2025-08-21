#!/usr/bin/env python3
"""
Export users from Django SQLite database to CSV
Run this script to backup your users before any database changes
"""

import os
import sys
import django
import csv
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mkhmd.settings')
django.setup()

from accounts.models import User, UserProfile, EmailVerification

def export_users_to_csv():
    """Export all users and related data to CSV files"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Export Users
    users_filename = f"users_backup_{timestamp}.csv"
    with open(users_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'id', 'email', 'username', 'first_name', 'last_name', 
            'is_email_verified', 'turnitin_balance', 'bio', 'location', 
            'website', 'is_staff', 'is_active', 'is_superuser', 
            'date_joined', 'last_login'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        users = User.objects.all()
        print(f"Exporting {users.count()} users...")
        
        for user in users:
            writer.writerow({
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_email_verified': user.is_email_verified,
                'turnitin_balance': user.turnitin_balance,
                'bio': user.bio,
                'location': user.location,
                'website': user.website,
                'is_staff': user.is_staff,
                'is_active': user.is_active,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined.isoformat() if user.date_joined else '',
                'last_login': user.last_login.isoformat() if user.last_login else '',
            })
    
    print(f"✅ Users exported to: {users_filename}")
    
    # Export User Profiles
    profiles_filename = f"profiles_backup_{timestamp}.csv"
    with open(profiles_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'user_id', 'user_email', 'phone', 'date_of_birth', 'company', 
            'job_title', 'github', 'linkedin', 'twitter', 'email_notifications',
            'profile_visibility', 'created_at'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        profiles = UserProfile.objects.select_related('user').all()
        print(f"Exporting {profiles.count()} user profiles...")
        
        for profile in profiles:
            writer.writerow({
                'user_id': profile.user.id,
                'user_email': profile.user.email,
                'phone': profile.phone,
                'date_of_birth': profile.date_of_birth.isoformat() if profile.date_of_birth else '',
                'company': profile.company,
                'job_title': profile.job_title,
                'github': profile.github,
                'linkedin': profile.linkedin,
                'twitter': profile.twitter,
                'email_notifications': profile.email_notifications,
                'profile_visibility': profile.profile_visibility,
                'created_at': profile.created_at.isoformat() if profile.created_at else '',
            })
    
    print(f"✅ User profiles exported to: {profiles_filename}")
    
    # Export Email Verifications (active ones)
    verifications_filename = f"email_verifications_backup_{timestamp}.csv"
    with open(verifications_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'user_id', 'user_email', 'verification_email', 'code', 
            'is_used', 'created_at', 'expires_at'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        verifications = EmailVerification.objects.select_related('user').all()
        print(f"Exporting {verifications.count()} email verifications...")
        
        for verification in verifications:
            writer.writerow({
                'user_id': verification.user.id,
                'user_email': verification.user.email,
                'verification_email': verification.email,
                'code': verification.code,
                'is_used': verification.is_used,
                'created_at': verification.created_at.isoformat() if verification.created_at else '',
                'expires_at': verification.expires_at.isoformat() if verification.expires_at else '',
            })
    
    print(f"✅ Email verifications exported to: {verifications_filename}")
    
    # Summary
    print(f"\n📊 Export Summary:")
    print(f"   Users: {users.count()}")
    print(f"   Profiles: {profiles.count()}")
    print(f"   Verifications: {verifications.count()}")
    print(f"\n📁 Files created:")
    print(f"   {users_filename}")
    print(f"   {profiles_filename}")
    print(f"   {verifications_filename}")

def export_passwords_hash():
    """Export password hashes separately (for complete backup)"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    passwords_filename = f"user_passwords_{timestamp}.csv"
    
    with open(passwords_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['user_id', 'email', 'password_hash']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        users = User.objects.all()
        for user in users:
            writer.writerow({
                'user_id': user.id,
                'email': user.email,
                'password_hash': user.password,
            })
    
    print(f"🔐 Password hashes exported to: {passwords_filename}")
    print("⚠️  Keep this file secure - contains password hashes!")

if __name__ == "__main__":
    print("🚀 Starting user data export...")
    print("=" * 50)
    
    try:
        export_users_to_csv()
        
        # Ask if user wants password hashes too
        response = input("\n❓ Export password hashes too? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            export_passwords_hash()
        
        print("\n✅ Export completed successfully!")
        print("📋 You can now manually recreate these users if needed.")
        
    except Exception as e:
        print(f"❌ Error during export: {e}")
        sys.exit(1) 