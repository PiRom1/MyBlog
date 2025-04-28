from Blog.models import User, Message, Session


def run():

    session = Session.objects.get(session_name='Chat Acelys')
    messages = [{'writer' : message.writer.username, 'date' : message.pub_date, 'text' : message.text} for message in Message.objects.filter(session_id=session)]

    print(f"Export en cours de {len(messages)} messages ...")

    with open('chat_export.txt', 'w', encoding='utf-8') as f:
        for i,message in enumerate(messages):
            if i%100 == 0:
                print(f"Ecriture en cours du {i}ème message ...")
            f.write(f"{message}\n")


