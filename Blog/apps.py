from django.apps import AppConfig

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.apps import AppConfig

class BlogConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Blog'

    def ready(self):
        import Blog.signals  # Charger les signaux

        from .scripts import drop_lootbox # The script to launch
        scheduler = BackgroundScheduler()
        scheduler.start()

        # box_trigger
        box_trigger = CronTrigger(
            year="*", month="*", day="*", hour="0", minute="0", second="0"
        )
        scheduler.add_job(
            drop_lootbox, trigger=box_trigger, name="test task", kwargs = {'nb_coin' : 100, 'nb_box' : 1}
        )

        
