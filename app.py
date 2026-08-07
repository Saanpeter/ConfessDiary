import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

# Vercel expects this
app = application


def _ensure_static_files():
    """Collect static files on startup if they do not already exist."""
    try:
        from django.conf import settings

        output_dir = getattr(settings, "STATIC_ROOT", None)

        if not output_dir:
            return

        output_path = str(output_dir)

        if not os.path.isdir(output_path) or not any(os.scandir(output_path)):
            call_command("collectstatic", no_input=True, verbosity=0)

    except Exception as error:
        print(f"WARNING: collectstatic failed: {error}")


_ensure_static_files()