import os
import sys

APP_DIR = os.path.dirname(os.path.abspath(__file__))

# cPanel Application Manager starts the system Python; switch to the
# project's virtualenv (venv/ next to this file) if it exists.
INTERP = os.path.join(APP_DIR, "venv", "bin", "python")
if os.path.exists(INTERP) and sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

sys.path.insert(0, APP_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mkhmd.settings")
os.environ.setdefault("DJANGO_DEBUG", "False")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
