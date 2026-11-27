"""Fill the Portfolio with experience, education and skills from the LinkedIn profile (Nov 2026)."""
from datetime import date

from django.db import migrations

EXPERIENCE = [
    {
        'company': 'TradeLanes',
        'role': 'Senior Python Software Engineer',
        'location': 'Oakland, California, USA',
        'start_date': date(2025, 12, 1),
        'end_date': date(2026, 10, 1),
        'description': '',
        'technologies': 'Python',
    },
    {
        'company': 'International Education Center Silkway Global',
        'role': 'Senior Software Development Engineer',
        'location': 'Kazakhstan',
        'start_date': date(2024, 7, 1),
        'end_date': date(2025, 10, 1),
        'description': (
            'Built scalable, efficient back-end solutions with Python and Django REST Framework\n'
            'Worked with MySQL, PostgreSQL and MongoDB databases\n'
            'Developed APIs and Telegram bots (Aiogram)\n'
            'Used Git and GitHub for version control and collaboration'
        ),
        'technologies': 'Python, Django REST Framework, MySQL, PostgreSQL, MongoDB, Aiogram, Git',
    },
    {
        'company': 'IT Technopark Al-Jabr',
        'role': 'Python Software Developer',
        'location': 'Tashkent, Uzbekistan',
        'start_date': date(2020, 9, 1),
        'end_date': date(2024, 5, 1),
        'description': '',
        'technologies': 'Python',
    },
]

EDUCATION = [
    {
        'school': 'Northumbria University, London',
        'degree': "Bachelor's degree",
        'field': 'Global Business Management and Marketing',
        'location': 'London, UK',
        'start_date': date(2025, 1, 1),
        'end_date': date(2027, 8, 1),
    },
]

SKILLS = [
    ('Python', 'languages'), ('Django', 'languages'), ('Django REST Framework', 'languages'),
    ('Back-End Web Development', 'languages'),
    ('PostgreSQL', 'data'), ('MySQL', 'data'), ('MongoDB', 'data'), ('SQLite', 'data'),
    ('Beautiful Soup', 'automation'), ('Selenium', 'automation'), ('Web Scraping', 'automation'),
    ('Telegram Bots (Aiogram)', 'automation'),
    ('REST APIs', 'tools'), ('Git & GitHub', 'tools'),
]


def seed(apps, schema_editor):
    Experience = apps.get_model('website', 'Experience')
    Education = apps.get_model('website', 'Education')
    Skill = apps.get_model('website', 'Skill')
    # Only fill empty tables, so re-running never duplicates or overwrites edits.
    if not Experience.objects.exists():
        for item in EXPERIENCE:
            Experience.objects.create(**item)
    if not Education.objects.exists():
        for item in EDUCATION:
            Education.objects.create(**item)
    if not Skill.objects.exists():
        for i, (name, category) in enumerate(SKILLS):
            Skill.objects.create(name=name, category=category, order=i)


def unseed(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_portfolio_experience'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
