"""
WSGI config for MyBlog project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os, sys

from django.core.wsgi import get_wsgi_application
sys.path.append("/home/domain.helioho.st/httpdocs/Myblog")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyBlog.settings')

application = get_wsgi_application()
