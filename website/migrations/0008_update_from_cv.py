"""Replace the Portfolio's experience, education and skills with the CV (Nov 2026)."""
from datetime import date

from django.db import migrations, models

EXPERIENCE = [
    {
        'company': 'TradeLanes Limited',
        'role': 'Python Senior Scraping Software Engineer',
        'location': 'Oakland, California, USA',
        'start_date': date(2025, 12, 1),
        'end_date': date(2026, 10, 1),
        'description': (
            'Built and maintained web scraping and data extraction systems in Python\n'
            'Handled dynamic websites and anti-bot protections\n'
            'Managed data parsing and normalization for reliable delivery to internal systems\n'
            'Focused on scraper stability and performance'
        ),
        'technologies': 'Python, Web Scraping, Playwright, Selenium, httpx, lxml',
    },
    {
        'company': 'Silkway Global KZ',
        'role': 'Senior Software Engineer',
        'location': 'Kazakhstan',
        'start_date': date(2024, 7, 1),
        'end_date': date(2025, 10, 1),
        'description': (
            'Developed a large-scale admin panel web system with Python and Django\n'
            'The platform supported staff operations for international student recruitment\n'
            'Built user management, secure internal communication, traffic and workflow control\n'
            'Built task (to-do) tracking and finance tracking\n'
            'Contributed to back-end architecture, API development and system scalability'
        ),
        'technologies': 'Python, Django, Django REST Framework, PostgreSQL, REST APIs',
    },
    {
        'company': 'Fiverr & Upwork',
        'role': 'Python Web Scraping / Crawling Engineer',
        'location': 'Remote · Contract / Freelance',
        'start_date': date(2022, 9, 1),
        'end_date': None,
        'description': (
            'Python web scraping and data mining for clients worldwide\n'
            'Scraped Google Maps, LinkedIn, Telegram and online marketplaces\n'
            'Implemented price-tracking logic, data extraction, normalization and automation workflows\n'
            'Developed Telegram bots and chatbots for automated data processing'
        ),
        'technologies': 'Python, Selenium WebDriver, SQL, MongoDB, JSON, Excel macros, Telegram Bots',
    },
    {
        'company': 'IT Technopark Al-Jabr',
        'role': 'Python Software Developer',
        'location': 'Tashkent, Uzbekistan',
        'start_date': date(2020, 9, 1),
        'end_date': date(2024, 5, 1),
        'description': (
            'Back-end development with Python and Django: REST APIs, database design and project structure\n'
            'Built and maintained back-end systems for startup websites\n'
            'Developed and led Telegram bot projects\n'
            'Worked with founders on software planning and MVP design, turning technical ideas into working systems'
        ),
        'technologies': 'Python, Django, Django REST Framework, Telegram Bots',
    },
]

EDUCATION = [
    {
        'school': 'Northumbria University, London',
        'degree': "Bachelor's degree",
        'field': 'Business Management and Marketing',
        'location': 'London, UK',
        'start_date': date(2025, 1, 1),
        'end_date': date(2027, 8, 1),
    },
    {
        'school': 'NAPA Edu Hub',
        'degree': '',
        'field': 'Python Back-End Engineering',
        'location': 'Tashkent, Uzbekistan',
        'start_date': None,
        'end_date': None,
    },
]

SKILLS = [
    ('Python', 'languages'), ('Django', 'languages'), ('Django REST Framework', 'languages'),
    ('OpenAPI / Swagger', 'languages'),
    ('PostgreSQL', 'data'), ('MySQL', 'data'), ('MongoDB', 'data'), ('SQLite', 'data'),
    ('requests', 'automation'), ('httpx', 'automation'), ('BeautifulSoup', 'automation'),
    ('lxml', 'automation'), ('Selenium', 'automation'), ('Playwright', 'automation'),
    ('Pyppeteer', 'automation'),
    ('Authentication (JWT, OAuth2)', 'tools'), ('HTTPS, CORS, CSRF protection', 'tools'),
    ('Unit, integration & API testing', 'tools'), ('flake8, black, isort', 'tools'),
    ('Git & GitHub', 'tools'), ('Postman', 'tools'),
    ('English (Professional working proficiency)', 'spoken'), ('Russian (Fluent)', 'spoken'),
    ('Uzbek (Native)', 'spoken'),
]


def seed(apps, schema_editor):
    Experience = apps.get_model('website', 'Experience')
    Education = apps.get_model('website', 'Education')
    Skill = apps.get_model('website', 'Skill')
    Experience.objects.all().delete()
    Education.objects.all().delete()
    Skill.objects.all().delete()
    for item in EXPERIENCE:
        Experience.objects.create(**item)
    for i, item in enumerate(EDUCATION):
        Education.objects.create(order=i, **item)
    for i, (name, category) in enumerate(SKILLS):
        Skill.objects.create(name=name, category=category, order=i)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_seed_linkedin_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skill',
            name='category',
            field=models.CharField(choices=[('languages', 'Languages & frameworks'), ('data', 'Databases & data'), ('automation', 'Scraping & automation'), ('tools', 'Tools & practices'), ('spoken', 'Spoken languages')], default='languages', max_length=20),
        ),
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
