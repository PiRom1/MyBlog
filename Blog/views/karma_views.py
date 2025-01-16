from better_profanity import profanity
from afinn import Afinn
 #*Moderation
profanity.load_censor_words_from_file('banwords.txt')

afinn = Afinn()

def analyze_sentiment(text, labels = ["positive", "neutral", "negative"], karma_dict = {"positive": 1, "neutral": 0, "negative": -1}):
    karma = afinn.score(text)
    
    # Vérification des banwords
    if karma > -1 and profanity.contains_profanity(text) :
        karma = karma - 5

    return karma


def analyse_sentiment_macro(messages, spam_threshold = 5):
    last_writer = None
    consecutive_count = 0

    # Loop throughout messages
    for i, message in enumerate(messages):

        message.karma = analyze_sentiment(message.text)
        message.save()
        
        if message.writer == last_writer: # Check consecutivity
            consecutive_count += 1
        else:
            consecutive_count = 1
            
        if message.karma > -0.5 and consecutive_count > spam_threshold: # If messages à la suite
            message.karma -= 1
        
        # If same message as previous
        if message.karma > -0.5 and i > 0 and message.text == messages[i - 1].text and message.writer == messages[i - 1].writer:
            message.karma -= 1
            
        
        last_writer = message.writer

    return messages