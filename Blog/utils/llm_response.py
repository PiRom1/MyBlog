import os
import random
from typing import Optional
from groq import Groq
from .llm_prompts import USERLIST, USERPROMPTS, USER_CONTEXTS
from Blog.models import Bot, User, SessionUser, SessionBot
from datetime import datetime

# Fonction qui génère une réponse à partir d'un message et optionnellement d'un utilisateur
def LLMResponse(username:str, message: str, session, bot: Optional[str] = None) -> Optional[str]:
    
    user = User.objects.get(username=username)
    user_context = user.llm_context
    print(user_context)

    

    try:    
        # Chose a random bot :
        if bot is None:
            allowed_bots = Bot.objects.filter(sessionbot__session=session).filter(can_answer=True)
            bot = random.choice(allowed_bots)

   
        # Initialize Groq client with API key
        client = Groq(
            api_key="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"
        )



        if bot.user.username == 'enjoy':
            prompt = f"{bot.preprompt}.\nVoici l'heure exacte que tu dois donner : {datetime.now().hour} heures et {datetime.now().minute} minutes."
            print("prompt : ", prompt)
            message = ''
        
        else:
            prompt = f"{bot.preprompt}\n\nTu parles à {user.username}. Fais mention des caractéristiques de cette personne dans ta réponse. Voici les caractéristiques de cette personne : {user_context}"
            
        # Send completion request to Groq with personalized prompt
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            model=bot.model_name,
            temperature=bot.temperature,
            max_tokens=bot.max_tokens,
            top_p=bot.top_p,
            presence_penalty=bot.presence_penalty,
            frequency_penalty=bot.frequence_penalty
        )

        # Return the generated response
        return response.choices[0].message.content, bot.user
    
    except Exception as e:
        print(f"Error during LLM request: {str(e)}")
        return None, None
    

def LLMNewMessage(session, bot: Optional[str] = None) -> Optional[str]:
    # Chose a random user from the list of users :
    
    try:
    
        if bot is None:

            allowed_bots = Bot.objects.filter(sessionbot__session=session).filter(can_answer=True)
            bot = random.choice(allowed_bots)
        
            # Initialize Groq client with API key
            client = Groq(
                api_key="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"
            )

            prompt = f"""{bot.preprompt}\n\n Tu dois ecrire un nouveau message en incarnant le personnage de {bot.user}.
                        Le message doit creer du débat, de la tension ou de l'humour. Le but est de faire réagir les autres membres de l'équipe. Le sujet du message est libre, mais il doit correspondre à la personnalité du personnage que tu incarnes."""

            # Send completion request to Groq with personalized prompt
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    }
                ],
                model="mixtral-8x7b-32768",
                temperature=bot.temperature,
                max_tokens=bot.max_tokens,
                top_p=bot.top_p,
                presence_penalty=bot.presence_penalty,
                frequency_penalty=bot.frequence_penalty
            )

            # Return the generated response
            return response.choices[0].message.content, bot.user
    
    except Exception as e:
        print(f"Error during LLM request: {str(e)}")
        return None, None
