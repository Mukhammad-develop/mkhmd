from django.core.management.base import BaseCommand
from website.models import TimeSlot
from datetime import time


class Command(BaseCommand):
    help = 'Add default time slots for availability'

    def handle(self, *args, **options):
        # Clear existing time slots
        TimeSlot.objects.all().delete()
        
        # Define time slots (Monday to Friday, 9 AM - 5 PM)
        time_slots = [
            # Monday
            {'weekday': 0, 'start_time': time(9, 0), 'end_time': time(12, 0), 'duration_minutes': 60},
            {'weekday': 0, 'start_time': time(13, 0), 'end_time': time(17, 0), 'duration_minutes': 60},
            
            # Tuesday
            {'weekday': 1, 'start_time': time(9, 0), 'end_time': time(12, 0), 'duration_minutes': 60},
            {'weekday': 1, 'start_time': time(13, 0), 'end_time': time(17, 0), 'duration_minutes': 60},
            
            # Wednesday
            {'weekday': 2, 'start_time': time(9, 0), 'end_time': time(12, 0), 'duration_minutes': 60},
            {'weekday': 2, 'start_time': time(13, 0), 'end_time': time(17, 0), 'duration_minutes': 60},
            
            # Thursday
            {'weekday': 3, 'start_time': time(9, 0), 'end_time': time(12, 0), 'duration_minutes': 60},
            {'weekday': 3, 'start_time': time(13, 0), 'end_time': time(17, 0), 'duration_minutes': 60},
            
            # Friday
            {'weekday': 4, 'start_time': time(9, 0), 'end_time': time(12, 0), 'duration_minutes': 60},
            {'weekday': 4, 'start_time': time(14, 0), 'end_time': time(16, 0), 'duration_minutes': 60},
        ]
        
        # Create time slots
        for slot_data in time_slots:
            TimeSlot.objects.create(**slot_data)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Successfully created {len(time_slots)} time slots!'))
        self.stdout.write(self.style.SUCCESS('   Monday - Thursday: 9:00-12:00, 13:00-17:00'))
        self.stdout.write(self.style.SUCCESS('   Friday: 9:00-12:00, 14:00-16:00'))
        self.stdout.write(self.style.SUCCESS('   Duration: 60 minutes per slot'))

