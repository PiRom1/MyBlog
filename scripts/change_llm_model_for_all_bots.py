from Blog.models import Bot

new_model = 'qwen/qwen3.8-27b'
exceptions = [] # List of exception : username bot

def run():

    for bot in Bot.objects.all():

        if bot.user.username not in exceptions:
            bot.model_name = new_model
            bot.save()

    print(f"Every bot models are changed to {new_model}")
    print(f"Excepted for the following bots :  {exceptions}")