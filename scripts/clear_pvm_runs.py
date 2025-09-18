import os
import sys
import django

# Setup Django environment
sys.path.append('/home/runner/work/MyBlog/MyBlog')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MyBlog.settings')
django.setup()

from Blog.models import DWPvmRun, DWPvmNewRun, DWPvmDino, DWUser

def clear_old_pvm_runs():
    """Clear old PvM runs from the database."""
    DWPvmRun.objects.all().delete()
    DWPvmNewRun.objects.all().delete()
    DWPvmDino.objects.all().delete()
    for dwuser in DWUser.objects.all():
        dwuser.pvm_runs_td = 0
        dwuser.save()

def run():
    clear_old_pvm_runs()
