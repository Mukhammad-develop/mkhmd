#!/usr/bin/env python3
"""
Import users from CSV files back into Django database
Use this to restore users after database changes
"""

import os
import sys
import django
import csv
from datetime import datetime
from django.contrib.auth.hashers import make_password

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mkhmd.settings')
django.setup()

from accounts.models import User, UserProfile, EmailVerification
from django.db import transaction

def import_users_from_csv(users_file, profiles_file=None, passwords_file=None):
    """Import users and related data from CSV files"""
    
    imported_users = 0
    imported_profiles = 0
    
    print(f"📥 Importing users from: {users_file}")
    
    # Import Users
    with open(users_file, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        with transaction.atomic():
            for row in reader:
                # Check if user already exists
                if User.objects.filter(email=row['email']).exists():
                    print(f"⚠️  User {row['email']} already exists - skipping")
                    continue
                
                # Parse dates
                date_joined = None
                if row['date_joined']:
                    try:
                        date_joined = datetime.fromisoformat(row['date_joined'].replace('Z', '+00:00'))
                    except:
                        date_joined = datetime.now()
                
                last_login = None
                if row['last_login']:
                    try:
                        last_login = datetime.fromisoformat(row['last_login'].replace('Z', '+00:00'))
                    except:
                        pass
                
                # Create user
                user = User.objects.create(
                    id=int(row['id']) if row['id'] else None,
                    email=row['email'],
                    username=row['username'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    is_email_verified=row['is_email_verified'].lower() == 'true',
                    turnitin_balance=int(row['turnitin_balance']) if row['turnitin_balance'] else 0,
                    bio=row['bio'],
                    location=row['location'],
                    website=row['website'],
                    is_staff=row['is_staff'].lower() == 'true',
                    is_active=row['is_active'].lower() == 'true',
                    is_superuser=row['is_superuser'].lower() == 'true',
                    date_joined=date_joined or datetime.now(),
                    last_login=last_login,
                    password=make_password('temporary_password_123')  # Set temporary password
                )
                
                imported_users += 1
                print(f"✅ Imported user: {user.email}")
    
    print(f"📊 Imported {imported_users} users")
    
    # Import User Profiles
    if profiles_file and os.path.exists(profiles_file):
        print(f"📥 Importing profiles from: {profiles_file}")
        
        with open(profiles_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            with transaction.atomic():
                for row in reader:
                    try:
                        user = User.objects.get(email=row['user_email'])
                        
                        # Check if profile already exists
                        if hasattr(user, 'userprofile'):
                            print(f"⚠️  Profile for {user.email} already exists - skipping")
                            continue
                        
                        # Parse date of birth
                        date_of_birth = None
                        if row['date_of_birth']:
                            try:
                                date_of_birth = datetime.fromisoformat(row['date_of_birth']).date()
                            except:
                                pass
                        
                        # Create profile
                        profile = UserProfile.objects.create(
                            user=user,
                            phone=row['phone'],
                            date_of_birth=date_of_birth,
                            company=row['company'],
                            job_title=row['job_title'],
                            github=row['github'],
                            linkedin=row['linkedin'],
                            twitter=row['twitter'],
                            email_notifications=row['email_notifications'].lower() == 'true',
                            profile_visibility=row['profile_visibility'],
                        )
                        
                        imported_profiles += 1
                        print(f"✅ Imported profile for: {user.email}")
                        
                    except User.DoesNotExist:
                        print(f"⚠️  User not found for profile: {row['user_email']}")
                        continue
        
        print(f"📊 Imported {imported_profiles} profiles")
    
    # Import password hashes if provided
    if passwords_file and os.path.exists(passwords_file):
        print(f"🔐 Importing password hashes from: {passwords_file}")
        
        with open(passwords_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            with transaction.atomic():
                for row in reader:
                    try:
                        user = User.objects.get(email=row['email'])
                        user.password = row['password_hash']
                        user.save()
                        print(f"🔐 Updated password for: {user.email}")
                    except User.DoesNotExist:
                        print(f"⚠️  User not found for password: {row['email']}")
                        continue
    
    print(f"\n✅ Import completed!")
    print(f"📊 Summary:")
    print(f"   Users imported: {imported_users}")
    print(f"   Profiles imported: {imported_profiles}")
    
    if not passwords_file:
        print(f"\n⚠️  NOTE: All users have temporary password 'temporary_password_123'")
        print(f"   Users will need to reset their passwords or you can import password hashes")

def list_csv_files():
    """List available CSV backup files"""
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    
    if not csv_files:
        print("❌ No CSV files found in current directory")
        return None, None, None
    
    print("📁 Available CSV files:")
    for i, file in enumerate(csv_files, 1):
        print(f"   {i}. {file}")
    
    # Try to auto-detect files by name
    users_file = None
    profiles_file = None
    passwords_file = None
    
    for file in csv_files:
        if 'users_backup' in file:
            users_file = file
        elif 'profiles_backup' in file:
            profiles_file = file
        elif 'user_passwords' in file:
            passwords_file = file
    
    return users_file, profiles_file, passwords_file

if __name__ == "__main__":
    print("📥 User Import Tool")
    print("=" * 50)
    
    try:
        # Auto-detect CSV files
        users_file, profiles_file, passwords_file = list_csv_files()
        
        if not users_file:
            users_file = input("📝 Enter users CSV file name: ").strip()
        
        if not os.path.exists(users_file):
            print(f"❌ File not found: {users_file}")
            sys.exit(1)
        
        # Ask about profiles and passwords
        if profiles_file:
            response = input(f"📋 Import profiles from {profiles_file}? (y/n): ").lower().strip()
            if response not in ['y', 'yes']:
                profiles_file = None
        
        if passwords_file:
            response = input(f"🔐 Import password hashes from {passwords_file}? (y/n): ").lower().strip()
            if response not in ['y', 'yes']:
                passwords_file = None
        
        # Confirm import
        print(f"\n📋 Import Plan:")
        print(f"   Users: {users_file}")
        print(f"   Profiles: {profiles_file or 'Skip'}")
        print(f"   Passwords: {passwords_file or 'Skip (temporary passwords)'}")
        
        response = input(f"\n❓ Proceed with import? (y/n): ").lower().strip()
        if response not in ['y', 'yes']:
            print("❌ Import cancelled")
            sys.exit(0)
        
        # Run import
        import_users_from_csv(users_file, profiles_file, passwords_file)
        
    except Exception as e:
        print(f"❌ Error during import: {e}")
        sys.exit(1) 