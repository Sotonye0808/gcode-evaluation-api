"""
WSGI config for gcode_evaluation project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from dotenv import load_dotenv

from django.core.wsgi import get_wsgi_application

project_folder = os.path.expanduser('/home/eusignatureeval/gcode-evaluation')
load_dotenv(os.path.join(project_folder, '.env'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gcode_evaluation.settings')

application = get_wsgi_application()
