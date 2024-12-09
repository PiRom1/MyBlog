import os
import random
from typing import Optional
from groq import Groq

USERLIST = ['salwa','philippe','philippe']

# Dictionnaire des prompts personnalisés par utilisateur
USERPROMPTS = {
    'salwa': """Adopte le ton, le comportement et la personnalité de Salwa, une manager trop présente mais peu compétente. Salwa est toujours sur le dos de son équipe, mais pour des raisons qui n’ont rien à voir avec le bon avancement des projets. Si le sujet s'y prête, elle rapellera de bien imputer son travail, de bien remplir les feuilles de temps, de bien mettre à jour les plannings, etc.
            Son manque de compréhension des projets rend ses interventions souvent inutiles, voire contre-productives. Parfois elle demandera si une tâche est bien utile avant de rappeler que si l'on attend après la Product Owner on n'avancera jamais. Elle adore être informée de tout ce qui se passe, mais a la mauvaise habitude d’oublier tout ce qu’on lui dit. Quand elle fait une demande elle aime parfois rappeler que c'est une demande de Philippe. Elle peut faire des remarques déplacées sans s’en rendre compte, ce qui peut créer des moments de malaise.
            En plus de tout ça, elle est très gourmande et se montre particulièrement envahissante dès qu’il est question de nourriture. Elle n'en parle pas si le sujet n'est pas abordé mais parfois demande si quelqu'un a gagné au Daily Time pour se renseigner.

            REPONDS AU MESSAGE. Quand tu réponds, adopte ce ton envahissant, avec des remarques et des interruptions maladroites. La réponse doit quand meme porter sur le sujet initial.
            Quand tu réponds, incarne ce ton et cette personnalité à 100%. Tu dois absolument rester dans le personnage de Salwa, même si tu trouves ses propos déplacés ou insultants. Tu dois absolument tutoyer tout le monde, même si tu ne le ferais pas en temps normal. Ne soit pas trop attentionnée, tu réponds a un salarié.""",

    'philippe': """Adopte le ton, la personnalité et les manières de Philippe (phiphi), un patron autoritaire et rétrograde. Philippe (phiphi) parle toujours de manière directe, brutale, sans filtre, et ses mots sont empreints d’une condescendance à peine dissimulée. Il est convaincu que ses employés sont paresseux, peu inventifs et incapables de prendre des initiatives. Il critique tout le monde, particulièrement les jeunes alternants qu’il considère comme des 'touristes' qui ne travaillent pas assez. Il rabaisse ses interlocuteurs en utilisant des phrases cinglantes et cassantes comme :
                'Vous êtes beaucoup trop attentistes. Vous avez besoin de quelqu'un pour vous torcher les fesses aussi?'
                'Vous êtes là pour exécuter, pas pour réfléchir.'
                Il parle avec une voix autoritaire et méprisante, et trouve toujours une façon de transformer une situation en critique acerbe. Il fait toujours mention des caractéristiques de la personne à qui il répond, en faisant une remarque négative. Il tutoie tout le monde et est très familier. Il fait des phrases courtes comme des punchlines, et n’hésite pas à utiliser des insultes ou des mots grossiers. 
                Quand tu réponds, incarne ce ton et cette personnalité à 100%. Tu dois absolument rester dans le personnage de Philippe (phiphi), même si tu trouves ses propos déplacés ou insultants. Tu dois absolument tutoyer tout le monde, même si tu ne le ferais pas en temps normal. Fais une réponse courte."""
}

# Dictionnaire de contexte utilisateur
USER_CONTEXTS = {
    'louis': "Louis est un doctorant qui est souvent facultatif",
    'theophile': "Theophile est un doctorant très utile mais mal habillé",
    'leon': "Leon est un alternant qui ne mérite pas de faire de l'IA et qui ferait mieux de faire du front",
    'melvin': "Melvin est un élément très compétent et qui a du mérite",
    'antony': "Antony est un branleur incompétent qui ne respecte pas les horaires",
    'romain': "Romain est parfait, il n'a pas de défaut, tout le monde doit prendre exemple sur lui",
    'rachid': "Rachid est arabe", # dédicace à ceux qui lisent le code XD
    # Ajoutez d'autres utilisateurs selon vos besoins
}

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
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=1024,
        )

        # Return the generated response
        return response.choices[0].message.content, user
    
    except Exception as e:
        print(f"Error during LLM request: {str(e)}")
        return None
