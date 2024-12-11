import os
import random
from typing import Optional
from groq import Groq
from .llm_prompts import USERLIST, USERPROMPTS, USER_CONTEXTS


# Fonction qui génère une réponse à partir d'un message et optionnellement d'un utilisateur
def LLMResponse(message: str, user: Optional[str] = None) -> Optional[str]:
    # Chose a random user from the list of users :
    if user is None:
        user = random.choice(USERLIST)

    og_user = message.split(' : ')[0].lower()
    user_context = USER_CONTEXTS.get(og_user, "Un salarié de l'entreprise")
    print(user_context)

    try:
        # Initialize Groq client with API key
        client = Groq(
            api_key="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"
        )

        prompt = f"{USERPROMPTS[user]}\n\nTu parles à {og_user}. Fais mention des caractéristiques de cette personne dans ta réponse. Voici les caractéristiques de cette personne : {user_context}"

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
            model="llama-3.3-70b-versatile",
            temperature=1.2,
            max_tokens=1024,
            top_p=0.95,
            presence_penalty=0.6,
            frequency_penalty=0.6
        )

        # Return the generated response
        return response.choices[0].message.content, user
    
    except Exception as e:
        print(f"Error during LLM request: {str(e)}")
        return None
    

def LLMNewMessage(user: Optional[str] = None) -> Optional[str]:
    # Chose a random user from the list of users :
    if user is None:
        user = random.choice(USERLIST)
    try:
        # Initialize Groq client with API key
        client = Groq(
            api_key="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"
        )

        prompt = f"""{USERPROMPTS[user]}\n\n Tu dois ecrire un nouveau message en incarnant le personnage de {user}.
                    Le message doit creer du débat, de la tension ou de l'humour. Le but est de faire réagir les autres membres de l'équipe. Le sujet du message est libre, mais il doit correspondre à la personnalité du personnage que tu incarnes."""

        # Send completion request to Groq with personalized prompt
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=1.2,
            max_tokens=1024,
            top_p=0.95,
            presence_penalty=0.6,
            frequency_penalty=0.6
        )

        # Return the generated response
        return response.choices[0].message.content, user
    
    except Exception as e:
        print(f"Error during LLM request: {str(e)}")
        return None
