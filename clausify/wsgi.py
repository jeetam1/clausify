import os
from django.core.wsgi import get_wsgi_application

# Make sure this string matches your inner folder name
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clausify.settings')

application = get_wsgi_application()

# Vercel needs this 'app' variable to find the entry point
app = application