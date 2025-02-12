"""
WSGI config for MyBlog project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys
import socket
import urllib.request

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyBlog.settings')

# Forward WSGI requests to Uvicorn running on a UNIX socket
def application(environ, start_response):
    url = "http://127.0.0.1:8080" + environ.get("PATH_INFO", "/")

    # Include query parameters if present
    if environ.get("QUERY_STRING"):
        url += "?" + environ["QUERY_STRING"]

    req = urllib.request.Request(url, headers={"Host": environ.get("HTTP_HOST", "localhost")})

    try:
        with urllib.request.urlopen(req) as response:
            start_response(f"{response.status} OK", response.headers.items())
            return [response.read()]
    except urllib.error.HTTPError as e:
        start_response(f"{e.code} ERROR", [])
        return [e.read()]
    except Exception as e:
        error_message = f"Error contacting Uvicorn: {str(e)}"
        start_response("500 Internal Server Error", [("Content-Type", "text/plain")])
        return [error_message.encode("utf-8")]
